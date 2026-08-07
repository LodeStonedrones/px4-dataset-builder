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


def test_anonymized_build_redacts_failed_input_paths(synthetic_ulog: Path, tmp_path: Path) -> None:
    inputs = tmp_path / "sensitive-inputs"
    inputs.mkdir()
    valid = inputs / "valid.ulg"
    valid.write_bytes(synthetic_ulog.read_bytes())
    broken = inputs / "customer-secret.ulg"
    broken.write_bytes(b"not a ULog")
    base = load_config()
    config = base.model_copy(
        update={"anonymization": base.anonymization.model_copy(update={"enabled": True})}
    )

    output = tmp_path / "anonymous-with-failure"
    manifest = DatasetBuilder(config).build(inputs, output)
    serialized = json.dumps(manifest)

    assert manifest["flight_count"] == 1
    assert manifest["failed_logs"][0]["source_file"].startswith("input-")
    assert "customer-secret" not in serialized
    assert str(inputs) not in serialized


def test_validator_checks_every_manifest_file(synthetic_ulog: Path, tmp_path: Path) -> None:
    output = tmp_path / "dataset"
    DatasetBuilder(load_config()).build(synthetic_ulog, output)
    (output / "statistics" / "summary.json").unlink()

    result = validate_dataset(output)

    assert not result["valid"]
    assert any("manifest file statistics" in problem for problem in result["problems"])
