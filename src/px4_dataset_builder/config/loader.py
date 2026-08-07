"""YAML configuration loader."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import Any

import yaml

from px4_dataset_builder.config.models import BuildConfig


def load_config(path: Path | None = None) -> BuildConfig:
    if path is None:
        text = files("px4_dataset_builder.config").joinpath("default.yaml").read_text("utf-8")
        return BuildConfig.model_validate(yaml.safe_load(text))
    if not path.is_file():
        raise FileNotFoundError(path)
    payload: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        raise ValueError("Configuration root must be a mapping")
    return BuildConfig.model_validate(payload)
