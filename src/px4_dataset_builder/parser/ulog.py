"""Memory-conscious PyULog adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from pyulog import ULog

from px4_dataset_builder.models import ParsedFlight, Severity
from px4_dataset_builder.topics.catalog import required_topics
from px4_dataset_builder.utils.hashing import flight_id, sha256_file


class ULogParser:
    """Parse one ULog and release PyULog objects before the next flight is processed."""

    def parse(self, source: Path, signals: list[str] | None = None) -> ParsedFlight:
        if source.suffix.lower() != ".ulg":
            raise ValueError(f"Expected a .ulg file, got: {source}")
        if not source.is_file():
            raise FileNotFoundError(source)

        digest = sha256_file(source)
        topic_filter = sorted(required_topics(signals or ["*"]))
        ulog = ULog(str(source), message_name_filter_list=topic_filter)
        start_us = int(ulog.start_timestamp)
        topics: dict[str, pd.DataFrame] = {}
        for dataset in ulog.data_list:
            key = dataset.name if dataset.multi_id == 0 else f"{dataset.name}#{dataset.multi_id}"
            columns = {
                name: values
                for name, values in dataset.data.items()
                if not name.startswith("_padding")
            }
            frame = pd.DataFrame(columns, copy=False)
            if "timestamp" not in frame:
                continue
            frame = frame.rename(columns={"timestamp": "timestamp_us"})
            frame.insert(1, "time_s", (frame["timestamp_us"] - start_us) / 1_000_000)
            topics[key] = frame

        return ParsedFlight(
            flight_id=flight_id(source, digest),
            source=source.resolve(),
            source_sha256=digest,
            start_timestamp_us=start_us,
            end_timestamp_us=int(ulog.last_timestamp),
            topics=topics,
            info={str(key): value for key, value in ulog.msg_info_dict.items()},
            parameters={str(key): value for key, value in ulog.initial_parameters.items()},
            logged_messages=self._messages(ulog, start_us),
            corrupt=bool(ulog.file_corruption),
        )

    @staticmethod
    def _messages(ulog: Any, start_us: int) -> list[tuple[float, Severity, str]]:
        result: list[tuple[float, Severity, str]] = []
        for message in ulog.logged_messages:
            level_value = getattr(message, "log_level_str", "info")
            level = str(level_value() if callable(level_value) else level_value).lower()
            severity = {
                "warning": Severity.WARNING,
                "warn": Severity.WARNING,
                "error": Severity.ERROR,
                "critical": Severity.CRITICAL,
                "alert": Severity.CRITICAL,
                "emergency": Severity.CRITICAL,
            }.get(level, Severity.INFO)
            result.append(
                (
                    (int(message.timestamp) - start_us) / 1_000_000,
                    severity,
                    str(message.message),
                )
            )
        return result
