from pathlib import Path

import pandas as pd

from px4_dataset_builder.config.models import QualityConfig
from px4_dataset_builder.models import ParsedFlight, QualityCode
from px4_dataset_builder.quality.analyzer import QualityAnalyzer


def test_quality_finds_duplicate_time_missing_topic_and_nan() -> None:
    parsed = ParsedFlight(
        flight_id="f",
        source=Path("f.ulg"),
        source_sha256="a" * 64,
        start_timestamp_us=0,
        end_timestamp_us=2_000_000,
        topics={
            "vehicle_status": pd.DataFrame(
                {"timestamp_us": [0, 1_000_000, 1_000_000], "time_s": [0, 1, 1]}
            )
        },
        info={},
        parameters={},
        logged_messages=[],
        corrupt=False,
    )
    normalized = pd.DataFrame(
        {"time_s": [0, 1], "timestamp_us": [0, 1_000_000], "gps.eph_m": [1.0, float("nan")]}
    )
    report = QualityAnalyzer().analyze(parsed, normalized, QualityConfig())
    codes = {issue.code for issue in report.issues}
    assert QualityCode.DUPLICATE_TIMESTAMP in codes
    assert QualityCode.MISSING_TOPIC in codes
    assert QualityCode.NAN_VALUE in codes
