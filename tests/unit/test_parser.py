from pathlib import Path

from px4_dataset_builder.parser.ulog import ULogParser


def test_parser_reads_real_synthetic_ulog(synthetic_ulog: Path) -> None:
    flight = ULogParser().parse(synthetic_ulog)

    assert flight.duration_seconds == 5.0
    assert flight.info["ver_sw"] == "synthetic"
    assert not flight.corrupt
    assert "vehicle_gps_position" in flight.topics
    assert list(flight.topics["sensor_combined"].columns[:2]) == ["timestamp_us", "time_s"]
    assert flight.logged_messages[0][2] == "Synthetic estimator warning"


def test_parser_rejects_non_ulog(tmp_path: Path) -> None:
    source = tmp_path / "not-a-log.txt"
    source.write_text("no")
    try:
        ULogParser().parse(source)
    except ValueError as error:
        assert "Expected a .ulg" in str(error)
    else:
        raise AssertionError("Expected ValueError")
