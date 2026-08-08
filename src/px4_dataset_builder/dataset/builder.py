"""End-to-end, local-only dataset build orchestration."""

from __future__ import annotations

import shutil
from collections.abc import Iterator
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from px4_dataset_builder._version import __version__
from px4_dataset_builder.anonymization.service import Anonymizer
from px4_dataset_builder.config.models import BuildConfig
from px4_dataset_builder.dataset.split import assign_splits
from px4_dataset_builder.events.detector import EventDetector
from px4_dataset_builder.exporters.tabular import TabularExporter, write_json
from px4_dataset_builder.models import FlightMetadata, ProcessedFlight
from px4_dataset_builder.parser.ulog import ULogParser
from px4_dataset_builder.quality.analyzer import QualityAnalyzer
from px4_dataset_builder.signals.normalizer import SignalNormalizer
from px4_dataset_builder.statistics.aggregate import aggregate_statistics
from px4_dataset_builder.topics.catalog import SIGNAL_CATALOG


@dataclass(slots=True)
class StagedFlight:
    raw_id: str
    processed: ProcessedFlight
    staging_path: Path
    sample_count: int


class DatasetBuilder:
    def __init__(self, config: BuildConfig) -> None:
        self.config = config

    def build(
        self,
        source: Path,
        output: Path | None = None,
        *,
        force: bool = False,
    ) -> dict[str, Any]:
        paths = discover_ulogs(source)
        if not paths:
            raise ValueError(f"No .ulg files found under {source}")
        source_resolved = source.resolve()
        destination = (output or self.config.output_directory).resolve()
        if source_resolved == destination or source_resolved.is_relative_to(destination):
            raise ValueError("Output directory cannot be the input path or one of its parents")
        if destination in {Path("/").resolve(), Path.home().resolve(), Path.cwd().resolve()}:
            raise ValueError(
                f"Refusing to use a broad or working directory as output: {destination}"
            )
        if destination.exists() and any(destination.iterdir()):
            if not force:
                raise FileExistsError(
                    f"Output directory is not empty: {destination}. Use --force to replace it."
                )
            shutil.rmtree(destination)
        destination.mkdir(parents=True, exist_ok=True)
        staging = destination / ".staging"
        staging.mkdir()
        exporter = TabularExporter(self.config.output_format)

        staged: list[StagedFlight] = []
        split_inputs: list[ProcessedFlight] = []
        failures: list[dict[str, str]] = []
        seen_source_hashes: set[str] = set()
        seen_flight_ids: set[str] = set()
        private_input_names = {
            path: f"input-{index:06d}.ulg" for index, path in enumerate(paths, start=1)
        }
        for path, processed, error in self._process(paths):
            if error is not None or processed is None:
                failures.append(
                    self._failure_record(
                        path,
                        error or "Unknown error",
                        private_input_names[path],
                    )
                )
                continue
            if processed.metadata.source_sha256 in seen_source_hashes:
                failures.append(
                    self._failure_record(
                        path,
                        "Duplicate ULog content was skipped.",
                        private_input_names[path],
                    )
                )
                continue
            seen_source_hashes.add(processed.metadata.source_sha256)
            raw_id = processed.metadata.flight_id
            data, metadata, events = Anonymizer().apply(
                processed.data,
                processed.metadata,
                processed.events,
                self.config.anonymization,
            )
            if metadata.flight_id in seen_flight_ids:
                failures.append(
                    self._failure_record(
                        path,
                        "Flight identifier collision; ULog was skipped.",
                        private_input_names[path],
                    )
                )
                continue
            seen_flight_ids.add(metadata.flight_id)
            split_inputs.append(
                ProcessedFlight(
                    pd.DataFrame(), processed.metadata, processed.events, processed.quality
                )
            )
            quality = processed.quality.model_copy(update={"flight_id": metadata.flight_id})
            stage_path = staging / f"{metadata.flight_id}.{exporter.extension}"
            exporter.write_frame(data, stage_path)
            staged.append(
                StagedFlight(
                    raw_id,
                    ProcessedFlight(pd.DataFrame(), metadata, events, quality),
                    stage_path,
                    len(data),
                )
            )

        if not staged:
            shutil.rmtree(staging)
            raise RuntimeError(f"All {len(paths)} ULog files failed to process: {failures}")

        split_inputs.sort(key=lambda item: item.metadata.flight_id)
        staged.sort(key=lambda item: item.raw_id)
        assignments = assign_splits(split_inputs, self.config.split)
        final_flights: list[ProcessedFlight] = []
        index: list[dict[str, Any]] = []
        all_events = []
        for record in staged:
            split = assignments[record.raw_id]
            metadata = record.processed.metadata
            relative_data_path = Path(split) / "flights" / record.staging_path.name
            final_data_path = destination / relative_data_path
            final_data_path.parent.mkdir(parents=True, exist_ok=True)
            record.staging_path.replace(final_data_path)
            metadata_path = destination / "metadata" / f"{metadata.flight_id}.json"
            write_json(record.processed.metadata.model_dump(mode="json"), metadata_path)
            final_flights.append(
                ProcessedFlight(
                    pd.DataFrame(), metadata, record.processed.events, record.processed.quality
                )
            )
            all_events.extend(record.processed.events)
            index.append(
                {
                    "flight_id": metadata.flight_id,
                    "split": split,
                    "data_file": str(relative_data_path),
                    "metadata_file": str(metadata_path.relative_to(destination)),
                    "samples": record.sample_count,
                    "events": len(record.processed.events),
                }
            )
        staging.rmdir()
        for split in ("train", "validation", "test"):
            (destination / split / "flights").mkdir(parents=True, exist_ok=True)

        event_path = destination / "events" / f"events.{exporter.extension}"
        exporter.write_events(all_events, event_path)
        write_json(index, destination / "flights" / "index.json")
        quality_payload = {
            "schema_version": "1.0",
            "reports": [flight.quality.model_dump(mode="json") for flight in final_flights],
            "failed_logs": failures,
        }
        write_json(quality_payload, destination / "data_quality_report.json")
        statistics = aggregate_statistics(final_flights, failures)
        write_json(statistics, destination / "statistics" / "summary.json")
        write_json(self._schema(), destination / "metadata" / "signal_schema.json")
        manifest = self._manifest(final_flights, index, failures, statistics, event_path)
        write_json(manifest, destination / "manifest.json")
        return manifest

    def _failure_record(self, path: Path, error: str, private_name: str) -> dict[str, str]:
        if not self.config.anonymization.enabled:
            return {"source_file": str(path), "error": error}
        sanitized_error = error
        path_variants = {str(path), str(path.resolve()), path.name}
        for value in sorted(path_variants, key=len, reverse=True):
            if value:
                sanitized_error = sanitized_error.replace(value, private_name)
        return {"source_file": private_name, "error": sanitized_error}

    def _process(
        self, paths: list[Path]
    ) -> Iterator[tuple[Path, ProcessedFlight | None, str | None]]:
        if self.config.performance.workers == 1:
            for path in paths:
                yield process_flight(path, self.config)
            return
        with ProcessPoolExecutor(max_workers=self.config.performance.workers) as executor:
            futures = {executor.submit(process_flight, path, self.config): path for path in paths}
            for future in as_completed(futures):
                path = futures[future]
                try:
                    yield future.result()
                except Exception as exc:  # defensive boundary around worker transport failures
                    yield path, None, f"{type(exc).__name__}: {exc}"

    def _manifest(
        self,
        flights: list[ProcessedFlight],
        index: list[dict[str, Any]],
        failures: list[dict[str, str]],
        statistics: dict[str, Any],
        event_path: Path,
    ) -> dict[str, Any]:
        split_distribution: dict[str, int] = {"train": 0, "validation": 0, "test": 0}
        for item in index:
            split_distribution[str(item["split"])] += 1
        sensors = sorted(
            {
                signal.split(".", 1)[0]
                for flight in flights
                for signal in flight.metadata.signals_available
            }
        )
        return {
            "schema_version": "1.0",
            "tool": {"name": "px4-dataset-builder", "version": __version__},
            "generated_at": datetime.now(UTC).isoformat(),
            "processing": "local-only",
            "output_format": self.config.output_format.value,
            "flight_count": len(flights),
            "total_duration_seconds": statistics["total_duration_seconds"],
            "total_samples": sum(int(item["samples"]) for item in index),
            "sensors_available": sensors,
            "event_distribution": statistics["event_distribution"],
            "split_distribution": split_distribution,
            "px4_versions": statistics["px4_version_distribution"],
            "failed_logs": failures,
            "incomplete_log_count": statistics["incomplete_log_count"],
            "anonymization": self.config.anonymization.model_dump(mode="json"),
            "resampling": self.config.resampling.model_dump(mode="json"),
            "files": {
                "flight_index": "flights/index.json",
                "events": str(event_path.relative_to(event_path.parents[1])),
                "statistics": "statistics/summary.json",
                "quality": "data_quality_report.json",
                "signal_schema": "metadata/signal_schema.json",
            },
        }

    @staticmethod
    def _schema() -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "time": {
                "time_s": "Seconds relative to ULog start.",
                "timestamp_us": "Original ULog timestamp; omitted during anonymization.",
            },
            "signals": {
                name: {
                    "unit": spec.unit,
                    "interpolation": spec.interpolation,
                    "valid_range": spec.valid_range,
                    "sensitive": spec.sensitive,
                    "px4_candidates": spec.candidates,
                }
                for name, spec in SIGNAL_CATALOG.items()
            },
            "derived_signals": {
                "attitude.roll_rad": {"unit": "rad", "source": "normalized quaternion"},
                "attitude.pitch_rad": {"unit": "rad", "source": "normalized quaternion"},
                "attitude.yaw_rad": {"unit": "rad", "source": "normalized quaternion"},
                "gps.north_m": {"unit": "m", "source": "optional anonymization"},
                "gps.east_m": {"unit": "m", "source": "optional anonymization"},
            },
        }


def discover_ulogs(source: Path) -> list[Path]:
    if source.is_file():
        return [source] if source.suffix.lower() == ".ulg" else []
    if not source.is_dir():
        raise FileNotFoundError(source)
    return sorted(
        path for path in source.rglob("*") if path.is_file() and path.suffix.lower() == ".ulg"
    )


def process_flight(
    path: Path, config: BuildConfig
) -> tuple[Path, ProcessedFlight | None, str | None]:
    try:
        parsed = ULogParser().parse(path, config.signals)
        normalized = SignalNormalizer().normalize(parsed, config.signals, config.resampling)
        quality = QualityAnalyzer().analyze(parsed, normalized, config.quality)
        events = EventDetector().detect(parsed, normalized, config.event_rules)
        metadata = _metadata(parsed, normalized, events, quality.passed)
        return path, ProcessedFlight(normalized, metadata, events, quality), None
    except Exception as exc:
        return path, None, f"{type(exc).__name__}: {exc}"


def _metadata(
    parsed: Any,
    normalized: pd.DataFrame,
    events: list[Any],
    quality_passed: bool,
) -> FlightMetadata:
    start = _utc_start(parsed.info)
    end = start + timedelta(seconds=parsed.duration_seconds) if start else None
    scalar_info = {
        str(key): value
        for key, value in parsed.info.items()
        if isinstance(value, (str, int, float, bool))
    }
    return FlightMetadata(
        flight_id=parsed.flight_id,
        source_file=str(parsed.source),
        source_sha256=parsed.source_sha256,
        px4_version=str(parsed.info.get("ver_sw") or parsed.info.get("ver_sw_release") or "")
        or None,
        duration_seconds=parsed.duration_seconds,
        start_timestamp=start.isoformat() if start else None,
        end_timestamp=end.isoformat() if end else None,
        start_timestamp_us=parsed.start_timestamp_us,
        end_timestamp_us=parsed.end_timestamp_us,
        topics_available=sorted(parsed.topics),
        signals_available=sorted(
            str(column) for column in normalized.columns.difference(["time_s", "timestamp_us"])
        ),
        events_detected=sorted({event.name for event in events}),
        gps_available=any(str(column).startswith("gps.") for column in normalized),
        imu_available=any(str(column).startswith("imu.") for column in normalized),
        battery_available=any(str(column).startswith("battery.") for column in normalized),
        drone_id=str(parsed.info.get("sys_uuid")) if parsed.info.get("sys_uuid") else None,
        quality_passed=quality_passed,
        source_info=scalar_info,
    )


def _utc_start(info: dict[str, Any]) -> datetime | None:
    value = info.get("time_ref_utc")
    if not isinstance(value, (int, float)) or value < 1_000_000_000_000:
        return None
    try:
        return datetime.fromtimestamp(float(value) / 1_000_000, tz=UTC)
    except (OverflowError, OSError, ValueError):
        return None
