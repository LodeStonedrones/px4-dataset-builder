import pandas as pd

from px4_dataset_builder.config.models import SplitConfig, SplitStrategy
from px4_dataset_builder.dataset.split import assign_splits
from px4_dataset_builder.models import DataQualityReport, FlightMetadata, ProcessedFlight


def flight(identifier: str, drone: str) -> ProcessedFlight:
    metadata = FlightMetadata(
        flight_id=identifier,
        source_file=f"{identifier}.ulg",
        source_sha256=identifier * 8,
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
        drone_id=drone,
    )
    return ProcessedFlight(
        pd.DataFrame(), metadata, [], DataQualityReport(flight_id=identifier, passed=True)
    )


def test_drone_split_prevents_group_leakage() -> None:
    flights = [flight("a", "one"), flight("b", "one"), flight("c", "two"), flight("d", "two")]
    assignments = assign_splits(
        flights, SplitConfig(strategy=SplitStrategy.DRONE, train=0.5, validation=0.25, test=0.25)
    )
    assert assignments["a"] == assignments["b"]
    assert assignments["c"] == assignments["d"]


def test_random_split_is_reproducible() -> None:
    flights = [flight(str(index), str(index)) for index in range(20)]
    config = SplitConfig(seed=7)
    assert assign_splits(flights, config) == assign_splits(flights, config)
