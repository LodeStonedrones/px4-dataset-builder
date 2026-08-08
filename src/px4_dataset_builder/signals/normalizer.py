"""Convert version-specific topic fields into one canonical wide table."""

from __future__ import annotations

from math import pi

import numpy as np
import pandas as pd

from px4_dataset_builder.config.models import ResamplingConfig
from px4_dataset_builder.models import ParsedFlight
from px4_dataset_builder.synchronization.resampler import resample
from px4_dataset_builder.topics.catalog import SIGNAL_CATALOG, SignalSpec


class SignalNormalizer:
    def normalize(
        self,
        flight: ParsedFlight,
        signal_names: list[str],
        config: ResamplingConfig,
    ) -> pd.DataFrame:
        selected = list(SIGNAL_CATALOG) if signal_names == ["*"] else signal_names
        unknown = sorted(set(selected) - SIGNAL_CATALOG.keys())
        if unknown:
            raise ValueError(f"Unknown canonical signals: {', '.join(unknown)}")

        step = 1.0 / config.frequency_hz
        duration = flight.duration_seconds
        sample_count = int(np.floor(duration * config.frequency_hz + 1e-9)) + 1
        if sample_count > config.max_output_rows:
            raise ValueError(
                "Normalized flight would contain "
                f"{sample_count} rows, exceeding max_output_rows={config.max_output_rows}"
            )
        target = np.arange(sample_count, dtype=np.float64) * step
        timestamp_offsets = np.rint(target * 1_000_000).astype(np.int64)
        maximum_timestamp = np.iinfo(np.int64).max
        if not 0 <= flight.start_timestamp_us <= maximum_timestamp - int(timestamp_offsets[-1]):
            raise ValueError("Normalized timestamps exceed the signed 64-bit output range")
        output: dict[str, np.ndarray] = {
            "time_s": target,
            "timestamp_us": flight.start_timestamp_us + timestamp_offsets,
        }
        for name in selected:
            spec = SIGNAL_CATALOG[name]
            source = self._find_source(flight, spec)
            if source is None:
                continue
            source_time, source_values = source
            method = (
                config.continuous_method if spec.interpolation == "linear" else spec.interpolation
            )
            output[name] = resample(
                source_time,
                source_values * spec.scale + spec.offset,
                target,
                method,
                config.max_interpolation_gap_s,
            )

        frame = pd.DataFrame(output)
        self._add_euler_angles(frame)
        return frame

    @staticmethod
    def _find_source(
        flight: ParsedFlight, spec: SignalSpec
    ) -> tuple[np.ndarray, np.ndarray] | None:
        for candidate in spec.candidates:
            topic_name, field_name = candidate.split(".", 1)
            keys = [
                topic_name,
                *sorted(
                    (key for key in flight.topics if key.startswith(f"{topic_name}#")),
                    key=lambda key: int(key.rsplit("#", 1)[1]),
                ),
            ]
            for key in keys:
                frame = flight.topics.get(key)
                if frame is None or field_name not in frame:
                    continue
                try:
                    values = pd.to_numeric(frame[field_name], errors="coerce").to_numpy(
                        dtype=np.float64
                    )
                except (TypeError, ValueError):
                    continue
                return frame["time_s"].to_numpy(dtype=np.float64), values
        return None

    @staticmethod
    def _add_euler_angles(frame: pd.DataFrame) -> None:
        quaternion_columns = ["attitude.q_w", "attitude.q_x", "attitude.q_y", "attitude.q_z"]
        if not all(column in frame for column in quaternion_columns):
            return
        w, x, y, z = (frame[column].to_numpy(dtype=np.float64) for column in quaternion_columns)
        norm = np.sqrt(w * w + x * x + y * y + z * z)
        valid = np.isfinite(norm) & (norm > 1e-12)
        w = np.divide(w, norm, out=np.full_like(w, np.nan), where=valid)
        x = np.divide(x, norm, out=np.full_like(x, np.nan), where=valid)
        y = np.divide(y, norm, out=np.full_like(y, np.nan), where=valid)
        z = np.divide(z, norm, out=np.full_like(z, np.nan), where=valid)
        frame["attitude.roll_rad"] = np.arctan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
        frame["attitude.pitch_rad"] = np.arcsin(np.clip(2 * (w * y - z * x), -1, 1))
        frame["attitude.yaw_rad"] = np.arctan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
        for column in ("attitude.roll_rad", "attitude.pitch_rad", "attitude.yaw_rad"):
            frame.loc[(frame[column] < -pi) | (frame[column] > pi), column] = np.nan
