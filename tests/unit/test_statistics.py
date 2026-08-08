import pandas as pd

from px4_dataset_builder.models import (
    DataQualityReport,
    FlightMetadata,
    ProcessedFlight,
    QualityCode,
    QualityIssue,
    Severity,
)
from px4_dataset_builder.statistics.aggregate import aggregate_statistics


def test_incomplete_log_count_counts_flights_not_missing_topic_issues() -> None:
    metadata = FlightMetadata(
        flight_id="flight",
        source_file="flight.ulg",
        source_sha256="a" * 64,
        px4_version=None,
        duration_seconds=1,
        start_timestamp=None,
        end_timestamp=None,
        start_timestamp_us=0,
        end_timestamp_us=1_000_000,
        topics_available=[],
        signals_available=[],
        events_detected=[],
        gps_available=False,
        imu_available=False,
        battery_available=False,
    )
    issues = [
        QualityIssue(
            code=QualityCode.MISSING_TOPIC,
            severity=Severity.ERROR,
            message=f"Missing group {index}",
        )
        for index in range(2)
    ]
    flight = ProcessedFlight(
        pd.DataFrame(),
        metadata,
        [],
        DataQualityReport(flight_id="flight", passed=False, issues=issues),
    )

    statistics = aggregate_statistics([flight], [])

    assert statistics["quality_issue_distribution"]["missing_topic"] == 2
    assert statistics["incomplete_log_count"] == 1
