from pathlib import Path

from px4_dataset_builder.config.loader import load_config
from px4_dataset_builder.dataset.builder import process_flight


def test_default_rules_detect_transparent_events(synthetic_ulog: Path) -> None:
    _, processed, error = process_flight(synthetic_ulog, load_config())

    assert error is None
    assert processed is not None
    names = {event.name for event in processed.events}
    assert {"gps_lost", "failsafe", "takeoff", "landing", "mode_change"} <= names
    gps_event = next(event for event in processed.events if event.name == "gps_lost")
    assert gps_event.source_signal == "gps.fix_type"
    assert gps_event.threshold == 3
