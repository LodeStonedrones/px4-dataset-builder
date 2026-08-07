from pathlib import Path

from typer.testing import CliRunner

from px4_dataset_builder.cli.app import app

runner = CliRunner()


def test_cli_build_stats_and_validate(synthetic_ulog: Path, tmp_path: Path) -> None:
    output = tmp_path / "dataset"
    build = runner.invoke(
        app, ["build", str(synthetic_ulog), "--output", str(output), "--format", "json"]
    )
    assert build.exit_code == 0, build.output
    assert "Dataset built" in build.output

    validate = runner.invoke(app, ["validate", str(output)])
    assert validate.exit_code == 0, validate.output
    assert '"valid": true' in validate.output

    stats = runner.invoke(app, ["stats", str(output)])
    assert stats.exit_code == 0, stats.output
    assert "flight_count" in stats.output


def test_cli_generates_parseable_example(tmp_path: Path) -> None:
    output = tmp_path / "example.ulg"
    result = runner.invoke(app, ["generate-example", "--output", str(output)])
    assert result.exit_code == 0, result.output
    assert output.is_file()
