import json
from pathlib import Path

import pytest

from px4_dataset_builder.config.loader import load_config
from px4_dataset_builder.config.models import OutputFormat
from px4_dataset_builder.dataset.builder import DatasetBuilder
from px4_dataset_builder.quality.validator import validate_dataset


@pytest.mark.parametrize("output_format", list(OutputFormat))
def test_end_to_end_all_formats(
    synthetic_ulog: Path, tmp_path: Path, output_format: OutputFormat
) -> None:
    config = load_config().model_copy(update={"output_format": output_format})
    output = tmp_path / f"dataset-{output_format.value}"
    manifest = DatasetBuilder(config).build(synthetic_ulog, output)

    assert manifest["flight_count"] == 1
    assert manifest["total_samples"] == 51
    assert manifest["event_distribution"]["failsafe"] == 1
    assert validate_dataset(output)["valid"]
    index = json.loads((output / "flights" / "index.json").read_text())
    assert (output / index[0]["data_file"]).is_file()


def test_anonymized_build_removes_absolute_location(synthetic_ulog: Path, tmp_path: Path) -> None:
    base = load_config()
    config = base.model_copy(
        update={
            "anonymization": base.anonymization.model_copy(
                update={"enabled": True, "gps_mode": "relative"}
            )
        }
    )
    output = tmp_path / "anonymous"
    DatasetBuilder(config).build(synthetic_ulog, output)
    index = json.loads((output / "flights" / "index.json").read_text())
    metadata = json.loads((output / index[0]["metadata_file"]).read_text())

    assert metadata["start_timestamp_us"] == 0
    assert metadata["drone_id"] is None
    assert "gps.latitude_deg" not in metadata["signals_available"]
    assert "gps.north_m" in metadata["signals_available"]
