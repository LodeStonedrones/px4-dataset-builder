import pandas as pd

from px4_dataset_builder.anonymization.service import Anonymizer
from px4_dataset_builder.config.models import AnonymizationConfig
from px4_dataset_builder.models import FlightEvent, FlightMetadata, Severity


def metadata() -> FlightMetadata:
    return FlightMetadata(
        flight_id="secret-name-abc",
        source_file="/secret/flight.ulg",
        source_sha256="a" * 64,
        px4_version="v1.15",
        duration_seconds=1,
        start_timestamp="2026-01-01T00:00:00Z",
        end_timestamp="2026-01-01T00:00:01Z",
        start_timestamp_us=1_000_000,
        end_timestamp_us=2_000_000,
        topics_available=["vehicle_gps_position"],
        signals_available=["gps.latitude_deg", "gps.longitude_deg", "gps.altitude_m"],
        events_detected=["px4_log_message"],
        gps_available=True,
        imu_available=False,
        battery_available=False,
        drone_id="hardware-id",
        source_info={
            "sys_uuid": "hardware-id",
            "ver_sw": "v1.15",
            "time_ref_utc": 1_767_225_600_000_000,
        },
    )


def test_relative_gps_and_metadata_redaction() -> None:
    frame = pd.DataFrame(
        {
            "time_s": [0.0, 1.0],
            "timestamp_us": [1_000_000, 2_000_000],
            "gps.latitude_deg": [45.0, 45.00001],
            "gps.longitude_deg": [9.0, 9.00001],
            "gps.altitude_m": [100.0, 102.0],
        }
    )
    event = FlightEvent(
        flight_id="secret-name-abc",
        name="px4_log_message",
        start_s=0,
        end_s=0,
        severity=Severity.WARNING,
        description="potentially sensitive operator text",
    )
    data, redacted, events = Anonymizer().apply(
        frame,
        metadata(),
        [event],
        AnonymizationConfig(enabled=True, gps_mode="relative"),
    )

    assert "timestamp_us" not in data
    assert "gps.latitude_deg" not in data
    assert data.loc[0, "gps.north_m"] == 0
    assert data.loc[1, "gps.altitude_relative_m"] == 2
    assert redacted.source_file == f"flight-{'a' * 16}.ulg"
    assert redacted.drone_id is None
    assert "sys_uuid" not in redacted.source_info
    assert "time_ref_utc" not in redacted.source_info
    assert "sensitive" not in events[0].description


def test_relative_gps_drops_an_unpaired_absolute_coordinate() -> None:
    frame = pd.DataFrame({"time_s": [0.0], "gps.latitude_deg": [45.0]})

    data, redacted, _ = Anonymizer().apply(
        frame,
        metadata(),
        [],
        AnonymizationConfig(enabled=True, gps_mode="relative"),
    )

    assert "gps.latitude_deg" not in data
    assert "gps.longitude_deg" not in data
    assert not redacted.gps_available
