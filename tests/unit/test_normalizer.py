from pathlib import Path

import pandas as pd
import pytest

from px4_dataset_builder.config.models import ResamplingConfig
from px4_dataset_builder.models import ParsedFlight
from px4_dataset_builder.signals.normalizer import SignalNormalizer


def parsed_flight(*, start: int = 1_000_000, end: int = 1_151_000) -> ParsedFlight:
    return ParsedFlight(
        flight_id="flight-test",
        source=Path("flight.ulg"),
        source_sha256="a" * 64,
        start_timestamp_us=start,
        end_timestamp_us=end,
        topics={},
        info={},
        parameters={},
        logged_messages=[],
        corrupt=False,
    )


def test_normalized_grid_never_extends_past_flight_duration() -> None:
    frame = SignalNormalizer().normalize(
        parsed_flight(),
        ["flight.mode"],
        ResamplingConfig(frequency_hz=10.0),
    )

    assert frame["time_s"].tolist() == [0.0, 0.1]
    assert frame["time_s"].iloc[-1] <= 0.151


def test_normalizer_rejects_excessive_output_rows_before_allocation() -> None:
    with pytest.raises(ValueError, match="exceeding max_output_rows=10"):
        SignalNormalizer().normalize(
            parsed_flight(end=101_000_000),
            ["flight.mode"],
            ResamplingConfig(frequency_hz=10.0, max_output_rows=10),
        )


def test_normalizer_rejects_signed_timestamp_overflow() -> None:
    maximum = 2**63 - 1
    with pytest.raises(ValueError, match="signed 64-bit"):
        SignalNormalizer().normalize(
            parsed_flight(start=maximum - 50_000, end=maximum + 150_000),
            ["flight.mode"],
            ResamplingConfig(frequency_hz=10.0),
        )


def test_normalizer_orders_multi_instances_numerically() -> None:
    flight = parsed_flight(end=1_000_000)
    flight.topics = {
        "battery_status#10": pd.DataFrame(
            {"time_s": [0.0], "timestamp_us": [1_000_000], "voltage_v": [10.0]}
        ),
        "battery_status#2": pd.DataFrame(
            {"time_s": [0.0], "timestamp_us": [1_000_000], "voltage_v": [2.0]}
        ),
    }

    frame = SignalNormalizer().normalize(
        flight,
        ["battery.voltage_v"],
        ResamplingConfig(frequency_hz=10.0),
    )

    assert frame["battery.voltage_v"].tolist() == [2.0]
