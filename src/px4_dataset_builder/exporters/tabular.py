"""CSV, JSON Lines, and Parquet writers with one schema per table."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from px4_dataset_builder.config.models import OutputFormat
from px4_dataset_builder.models import FlightEvent


class TabularExporter:
    def __init__(self, output_format: OutputFormat) -> None:
        self.output_format = output_format

    @property
    def extension(self) -> str:
        return "jsonl" if self.output_format == OutputFormat.JSON else self.output_format.value

    def write_frame(self, frame: pd.DataFrame, destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if self.output_format == OutputFormat.PARQUET:
            frame.to_parquet(destination, index=False, compression="zstd", engine="pyarrow")
        elif self.output_format == OutputFormat.CSV:
            frame.to_csv(destination, index=False)
        else:
            frame.to_json(destination, orient="records", lines=True, double_precision=15)
        return destination

    def write_events(self, events: list[FlightEvent], destination: Path) -> Path:
        rows = [event.model_dump(mode="json") for event in events]
        columns = [
            "flight_id",
            "name",
            "start_s",
            "end_s",
            "severity",
            "source_signal",
            "observed_value",
            "threshold",
            "description",
        ]
        return self.write_frame(pd.DataFrame(rows, columns=columns), destination)


def write_json(payload: Any, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False, default=str) + "\n",
        encoding="utf-8",
    )
    temporary.replace(destination)
    return destination
