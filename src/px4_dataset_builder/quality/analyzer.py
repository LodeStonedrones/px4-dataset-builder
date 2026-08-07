"""Observable data-quality checks for raw topics and normalized signals."""

from __future__ import annotations

import numpy as np
import pandas as pd

from px4_dataset_builder.config.models import QualityConfig
from px4_dataset_builder.models import (
    DataQualityReport,
    ParsedFlight,
    QualityCode,
    QualityIssue,
    Severity,
)
from px4_dataset_builder.topics.catalog import SIGNAL_CATALOG


class QualityAnalyzer:
    def analyze(
        self,
        flight: ParsedFlight,
        normalized: pd.DataFrame,
        config: QualityConfig,
    ) -> DataQualityReport:
        issues: list[QualityIssue] = []
        available_base_topics = {name.split("#", 1)[0] for name in flight.topics}
        if flight.corrupt:
            issues.append(
                QualityIssue(
                    code=QualityCode.CORRUPT_LOG,
                    severity=Severity.ERROR if config.fail_on_corrupt else Severity.WARNING,
                    message="PyULog reported file corruption.",
                )
            )
        for alternatives in config.required_topic_groups:
            if not available_base_topics.intersection(alternatives):
                issues.append(
                    QualityIssue(
                        code=QualityCode.MISSING_TOPIC,
                        severity=Severity.WARNING,
                        message=(
                            f"None of the alternative required topics are present: {alternatives}"
                        ),
                    )
                )

        for topic, frame in flight.topics.items():
            times = frame["timestamp_us"].to_numpy(dtype=np.float64)
            differences = np.diff(times)
            backwards = int(np.sum(differences < 0))
            duplicates = int(np.sum(differences == 0))
            if backwards:
                issues.append(
                    QualityIssue(
                        code=QualityCode.NON_MONOTONIC_TIME,
                        severity=Severity.ERROR,
                        message="Topic timestamps move backwards.",
                        topic=topic,
                        count=backwards,
                    )
                )
            if duplicates:
                issues.append(
                    QualityIssue(
                        code=QualityCode.DUPLICATE_TIMESTAMP,
                        severity=Severity.WARNING,
                        message="Topic contains duplicate timestamps.",
                        topic=topic,
                        count=duplicates,
                    )
                )
            positive = differences[differences > 0] / 1_000_000
            if positive.size >= 3:
                median = float(np.median(positive))
                cv = float(np.std(positive) / np.mean(positive))
                if cv > config.irregular_sampling_cv:
                    issues.append(
                        QualityIssue(
                            code=QualityCode.IRREGULAR_SAMPLING,
                            severity=Severity.WARNING,
                            message=f"Sampling interval coefficient of variation is {cv:.3f}.",
                            topic=topic,
                        )
                    )
                dropouts = int(np.sum(positive > median * config.dropout_factor))
                if dropouts:
                    issues.append(
                        QualityIssue(
                            code=QualityCode.SENSOR_DROPOUT,
                            severity=Severity.WARNING,
                            message="Topic contains gaps larger than the configured median factor.",
                            topic=topic,
                            count=dropouts,
                        )
                    )

        signal_statistics: dict[str, dict[str, float | int | None]] = {}
        for signal in normalized.columns.difference(["time_s", "timestamp_us"]):
            values = normalized[signal].to_numpy(dtype=np.float64)
            nan_count = int(np.isnan(values).sum())
            infinite_count = int(np.isinf(values).sum())
            finite = values[np.isfinite(values)]
            signal_statistics[signal] = {
                "samples": len(values),
                "finite_samples": len(finite),
                "nan_count": nan_count,
                "infinite_count": infinite_count,
                "minimum": float(np.min(finite)) if finite.size else None,
                "maximum": float(np.max(finite)) if finite.size else None,
                "mean": float(np.mean(finite)) if finite.size else None,
            }
            if nan_count:
                issues.append(
                    QualityIssue(
                        code=QualityCode.NAN_VALUE,
                        severity=Severity.WARNING,
                        message="Normalized signal contains unavailable samples.",
                        signal=signal,
                        count=nan_count,
                    )
                )
            if infinite_count:
                issues.append(
                    QualityIssue(
                        code=QualityCode.INFINITE_VALUE,
                        severity=Severity.ERROR,
                        message="Signal contains infinite values.",
                        signal=signal,
                        count=infinite_count,
                    )
                )
            valid_range = SIGNAL_CATALOG.get(signal)
            if finite.size and valid_range is not None and valid_range.valid_range is not None:
                lower, upper = valid_range.valid_range
                outside = int(np.sum((finite < lower) | (finite > upper)))
                if outside:
                    issues.append(
                        QualityIssue(
                            code=QualityCode.OUT_OF_RANGE,
                            severity=Severity.WARNING,
                            message=f"Values fall outside the documented range [{lower}, {upper}].",
                            signal=signal,
                            count=outside,
                        )
                    )
        if normalized.empty or len(normalized.columns) <= 2:
            issues.append(
                QualityIssue(
                    code=QualityCode.EMPTY_FLIGHT,
                    severity=Severity.ERROR,
                    message="No canonical signal could be extracted.",
                )
            )
        passed = not any(issue.severity in {Severity.ERROR, Severity.CRITICAL} for issue in issues)
        return DataQualityReport(
            flight_id=flight.flight_id,
            passed=passed,
            issues=issues,
            signal_statistics=signal_statistics,
        )
