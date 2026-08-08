"""Professional local-first command-line interface."""

from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from px4_dataset_builder._version import __version__
from px4_dataset_builder.config.loader import load_config
from px4_dataset_builder.config.models import OutputFormat
from px4_dataset_builder.dataset.builder import DatasetBuilder, process_flight
from px4_dataset_builder.parser.ulog import ULogParser
from px4_dataset_builder.quality.validator import validate_dataset
from px4_dataset_builder.utils.synthetic_ulog import generate_synthetic_ulog

app = typer.Typer(
    name="px4-dataset",
    no_args_is_help=True,
    help="Build documented, local-first datasets from PX4 ULogs.",
)
console = Console()


def version_callback(value: bool) -> None:
    if value:
        console.print(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option("--version", callback=version_callback, is_eager=True, help="Show version."),
    ] = None,
) -> None:
    """PX4 Dataset Builder performs no network or cloud operation."""


@app.command("build")
def build_command(
    source: Annotated[
        Path, typer.Argument(exists=True, readable=True, help=".ulg file or directory")
    ],
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Dataset directory; overrides the config file"),
    ] = None,
    config_path: Annotated[
        Path | None, typer.Option("--config", "-c", exists=True, readable=True)
    ] = None,
    output_format: Annotated[
        OutputFormat | None, typer.Option("--format", help="csv, json, or parquet")
    ] = None,
    anonymize: Annotated[
        bool, typer.Option("--anonymize", help="Enable configured anonymization")
    ] = False,
    workers: Annotated[int | None, typer.Option("--workers", min=1, max=64)] = None,
    force: Annotated[
        bool, typer.Option("--force", help="Replace a non-empty output directory")
    ] = False,
) -> None:
    """Build a dataset from one ULog or a recursive directory of ULogs."""
    config = load_config(config_path)
    updates: dict[str, object] = {}
    if output is not None:
        updates["output_directory"] = output
    if output_format is not None:
        updates["output_format"] = output_format
    if anonymize:
        updates["anonymization"] = config.anonymization.model_copy(update={"enabled": True})
    if workers is not None:
        updates["performance"] = config.performance.model_copy(update={"workers": workers})
    config = config.model_copy(update=updates)
    destination = output or config.output_directory
    with console.status("Processing ULogs locally..."):
        manifest = DatasetBuilder(config).build(source, destination, force=force)
    table = Table(title="Dataset built")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    table.add_row("Flights", str(manifest["flight_count"]))
    table.add_row("Samples", str(manifest["total_samples"]))
    table.add_row("Duration", f"{manifest['total_duration_seconds']:.1f} s")
    table.add_row("Failed logs", str(len(manifest["failed_logs"])))
    console.print(table)
    console.print(f"Dataset: [bold]{destination.resolve()}[/bold]")


@app.command("inspect")
def inspect_command(
    log: Annotated[Path, typer.Argument(exists=True, readable=True)],
    config_path: Annotated[Path | None, typer.Option("--config", "-c")] = None,
) -> None:
    """Inspect selected source topics and canonical signals without writing a dataset."""
    config = load_config(config_path)
    path, processed, error = process_flight(log, config)
    if error or processed is None:
        raise typer.BadParameter(f"Could not inspect {path}: {error}")
    payload = {
        "metadata": processed.metadata.model_dump(mode="json"),
        "quality": processed.quality.model_dump(mode="json"),
        "event_count": len(processed.events),
        "sample_count": len(processed.data),
    }
    console.print_json(json.dumps(payload, default=str))


@app.command("events")
def events_command(
    log: Annotated[Path, typer.Argument(exists=True, readable=True)],
    config_path: Annotated[Path | None, typer.Option("--config", "-c")] = None,
) -> None:
    """Detect and print configured events for one ULog."""
    config = load_config(config_path)
    _, processed, error = process_flight(log, config)
    if error or processed is None:
        raise typer.BadParameter(error or "Unknown processing error")
    console.print_json(
        json.dumps([event.model_dump(mode="json") for event in processed.events], default=str)
    )


@app.command("stats")
def stats_command(dataset: Annotated[Path, typer.Argument(exists=True, file_okay=False)]) -> None:
    """Print aggregate statistics generated for a dataset."""
    path = dataset / "statistics" / "summary.json"
    if not path.is_file():
        raise typer.BadParameter(f"Statistics not found: {path}")
    console.print_json(path.read_text(encoding="utf-8"))


@app.command("validate")
def validate_command(
    dataset: Annotated[Path, typer.Argument(exists=True, file_okay=False)],
) -> None:
    """Validate dataset structure, metadata, and available artifact checksums."""
    result = validate_dataset(dataset)
    console.print_json(json.dumps(result))
    if not result["valid"]:
        raise typer.Exit(code=1)


@app.command("init-config")
def init_config_command(
    output: Annotated[Path, typer.Option("--output", "-o")] = Path("config.yaml"),
) -> None:
    """Write the documented default YAML configuration."""
    if output.exists():
        raise typer.BadParameter(f"Refusing to overwrite {output}")
    text = files("px4_dataset_builder.config").joinpath("default.yaml").read_text("utf-8")
    output.write_text(text, encoding="utf-8")
    console.print(f"Configuration written to [bold]{output.resolve()}[/bold]")


@app.command("generate-example")
def generate_example_command(
    output: Annotated[Path, typer.Option("--output", "-o")] = Path("synthetic-flight.ulg"),
) -> None:
    """Generate a tiny deterministic ULog with synthetic coordinates and no identity."""
    if output.exists():
        raise typer.BadParameter(f"Refusing to overwrite {output}")
    generate_synthetic_ulog(output)
    parsed = ULogParser().parse(output)
    console.print(
        f"Synthetic ULog: [bold]{output.resolve()}[/bold] "
        f"({len(parsed.topics)} topics, {parsed.duration_seconds:.1f} s)"
    )


if __name__ == "__main__":
    app()
