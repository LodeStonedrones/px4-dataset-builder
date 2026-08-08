"""Validated public configuration schema."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from px4_dataset_builder.topics.catalog import SIGNAL_CATALOG


class OutputFormat(StrEnum):
    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"


class SplitStrategy(StrEnum):
    RANDOM = "random"
    FLIGHT = "flight"
    DRONE = "drone"
    DATE = "date"
    EVENT = "event"


class RuleKind(StrEnum):
    THRESHOLD = "threshold"
    CHANGE = "change"
    EDGE = "edge"
    GAP = "gap"


class ResamplingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frequency_hz: float = Field(default=10.0, gt=0, le=1_000)
    continuous_method: Literal["linear", "nearest"] = "linear"
    max_interpolation_gap_s: float = Field(default=1.0, gt=0)
    max_output_rows: int = Field(default=1_000_000, ge=1, le=100_000_000)


class EventRuleConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    kind: RuleKind
    signal: str
    operator: Literal["lt", "le", "gt", "ge", "eq", "ne"] | None = None
    threshold: float | int | None = None
    min_duration_s: float = Field(default=0.0, ge=0)
    severity: Literal["info", "warning", "error", "critical"] = "warning"
    description: str

    @model_validator(mode="after")
    def validate_rule(self) -> EventRuleConfig:
        if self.kind in {RuleKind.THRESHOLD, RuleKind.EDGE} and (
            self.operator is None or self.threshold is None
        ):
            raise ValueError("threshold and edge rules require operator and threshold")
        if self.kind == RuleKind.GAP and self.threshold is None:
            raise ValueError("gap rules require a threshold in seconds")
        return self


class SplitConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strategy: SplitStrategy = SplitStrategy.RANDOM
    train: float = Field(default=0.70, ge=0, le=1)
    validation: float = Field(default=0.15, ge=0, le=1)
    test: float = Field(default=0.15, ge=0, le=1)
    seed: int = 42

    @model_validator(mode="after")
    def ratios_sum_to_one(self) -> SplitConfig:
        if abs(self.train + self.validation + self.test - 1.0) > 1e-9:
            raise ValueError("train + validation + test must equal 1.0")
        return self


class AnonymizationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    gps_mode: Literal["remove", "relative", "keep"] = "remove"
    relative_altitude: bool = True
    hash_source_filenames: bool = True
    remove_metadata: list[str] = Field(
        default_factory=lambda: [
            "sys_uuid",
            "ver_hw",
            "sys_name",
            "vehicle_name",
            "serial_number",
        ]
    )


class QualityConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    required_topic_groups: list[list[str]] = Field(
        default_factory=lambda: [
            ["vehicle_status"],
            ["sensor_combined", "vehicle_imu"],
        ]
    )
    irregular_sampling_cv: float = Field(default=0.25, gt=0)
    dropout_factor: float = Field(default=5.0, gt=1)
    fail_on_corrupt: bool = True


class PerformanceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workers: int = Field(default=1, ge=1, le=64)


class BuildConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    signals: list[str] = Field(default_factory=lambda: ["*"])
    output_format: OutputFormat = OutputFormat.PARQUET
    resampling: ResamplingConfig = Field(default_factory=ResamplingConfig)
    event_rules: list[EventRuleConfig] = Field(default_factory=list)
    split: SplitConfig = Field(default_factory=SplitConfig)
    anonymization: AnonymizationConfig = Field(default_factory=AnonymizationConfig)
    quality: QualityConfig = Field(default_factory=QualityConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    output_directory: Path = Path("dataset")

    @model_validator(mode="after")
    def validate_signal_selection(self) -> BuildConfig:
        if not self.signals:
            raise ValueError("signals must contain at least one canonical signal or '*'")
        if "*" in self.signals and self.signals != ["*"]:
            raise ValueError("the '*' signal wildcard must be used on its own")

        selected = set(SIGNAL_CATALOG) if self.signals == ["*"] else set(self.signals)
        unknown = sorted(selected - SIGNAL_CATALOG.keys())
        if unknown:
            raise ValueError(f"unknown canonical signals: {', '.join(unknown)}")

        rule_names: set[str] = set()
        for rule in self.event_rules:
            if not rule.name.strip():
                raise ValueError("event rule names must not be blank")
            if rule.name in rule_names:
                raise ValueError(f"duplicate event rule name: {rule.name}")
            rule_names.add(rule.name)
            if rule.signal not in SIGNAL_CATALOG:
                raise ValueError(
                    f"event rule '{rule.name}' uses unknown canonical signal: {rule.signal}"
                )
            if rule.signal not in selected:
                raise ValueError(
                    f"event rule '{rule.name}' requires signal '{rule.signal}' to be selected"
                )
        return self
