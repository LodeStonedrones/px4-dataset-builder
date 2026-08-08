from pathlib import Path

import numpy as np
import pandas as pd

from px4_dataset_builder.config.loader import load_config
from px4_dataset_builder.config.models import EventRuleConfig
from px4_dataset_builder.dataset.builder import process_flight
from px4_dataset_builder.events.detector import EventDetector
from px4_dataset_builder.models import ParsedFlight


def test_default_rules_detect_transparent_events(synthetic_ulog: Path) -> None:
    _, processed, error = process_flight(synthetic_ulog, load_config())

    assert error is None
    assert processed is not None
    names = {event.name for event in processed.events}
    assert {"gps_lost", "failsafe", "takeoff", "landing", "mode_change"} <= names
    gps_event = next(event for event in processed.events if event.name == "gps_lost")
    assert gps_event.source_signal == "gps.fix_type"
    assert gps_event.threshold == 3


def test_edge_rule_does_not_create_an_event_after_missing_data() -> None:
    flight = ParsedFlight(
        flight_id="flight",
        source=Path("flight.ulg"),
        source_sha256="a" * 64,
        start_timestamp_us=0,
        end_timestamp_us=1_000_000,
        topics={},
        info={},
        parameters={},
        logged_messages=[],
        corrupt=False,
    )
    rule = EventRuleConfig(
        name="takeoff",
        kind="edge",
        signal="land.landed",
        operator="eq",
        threshold=0,
        description="Test edge.",
    )
    data = pd.DataFrame({"time_s": [0.0, 1.0], "land.landed": [np.nan, 0.0]})

    assert EventDetector().detect(flight, data, [rule]) == []
