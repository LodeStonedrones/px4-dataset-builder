"""Typed data contracts shared by pipeline modules."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class QualityCode(StrEnum):
    CORRUPT_LOG = "corrupt_log"
    MISSING_TOPIC = "missing_topic"
    NON_MONOTONIC_TIME = "non_monotonic_time"
    DUPLICATE_TIMESTAMP = "duplicate_timestamp"
    IRREGULAR_SAMPLING = "irregular_sampling"
    SENSOR_DROPOUT = "sensor_dropout"
    NAN_VALUE = "nan_value"
    INFINITE_VALUE = "infinite_value"
    OUT_OF_RANGE = "out_of_range"
    EMPTY_FLIGHT = "empty_flight"


class FlightEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    flight_id: str
    name: str
    start_s: float
    end_s: float
    severity: Severity
    source_signal: str | None = None
    observed_value: float | int | str | None = None
    threshold: float | int | str | None = None
    description: str


class QualityIssue(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: QualityCode
    severity: Severity
    message: str
    topic: str | None = None
    signal: str | None = None
    count: int = 1


class DataQualityReport(BaseModel):
    flight_id: str
    passed: bool
    issues: list[QualityIssue] = Field(default_factory=list)
    signal_statistics: dict[str, dict[str, float | int | None]] = Field(default_factory=dict)


class FlightMetadata(BaseModel):
    model_config = ConfigDict(extra="allow")

    flight_id: str
    source_file: str
    source_sha256: str
    px4_version: str | None
    duration_seconds: float
    start_timestamp: str | None
    end_timestamp: str | None
    start_timestamp_us: int
    end_timestamp_us: int
    topics_available: list[str]
    signals_available: list[str]
    events_detected: list[str]
    gps_available: bool
    imu_available: bool
    battery_available: bool
    drone_id: str | None = None
    quality_passed: bool = True
    source_info: dict[str, str | int | float | bool] = Field(default_factory=dict)


@dataclass(slots=True)
class ParsedFlight:
    flight_id: str
    source: Path
    source_sha256: str
    start_timestamp_us: int
    end_timestamp_us: int
    topics: dict[str, pd.DataFrame]
    info: dict[str, Any]
    parameters: dict[str, int | float]
    logged_messages: list[tuple[float, Severity, str]]
    corrupt: bool

    @property
    def duration_seconds(self) -> float:
        return max(0.0, (self.end_timestamp_us - self.start_timestamp_us) / 1_000_000)


@dataclass(slots=True)
class ProcessedFlight:
    data: pd.DataFrame
    metadata: FlightMetadata
    events: list[FlightEvent]
    quality: DataQualityReport
