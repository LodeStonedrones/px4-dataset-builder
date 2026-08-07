"""Validate a built dataset's manifest and referenced files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def validate_dataset(dataset: Path) -> dict[str, Any]:
    problems: list[str] = []
    manifest_path = dataset / "manifest.json"
    index_path = dataset / "flights" / "index.json"
    if not manifest_path.is_file():
        return {"valid": False, "problems": ["manifest.json is missing"]}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return {"valid": False, "problems": [f"manifest.json cannot be read: {exc}"]}
    if manifest.get("schema_version") != "1.0":
        problems.append(f"Unsupported manifest schema: {manifest.get('schema_version')}")
    if not index_path.is_file():
        problems.append("flights/index.json is missing")
        index: list[dict[str, Any]] = []
    else:
        try:
            index = json.loads(index_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            problems.append(f"Flight index cannot be read: {exc}")
            index = []
    seen: set[str] = set()
    for item in index:
        identifier = item.get("flight_id")
        if not isinstance(identifier, str) or identifier in seen:
            problems.append(f"Invalid or duplicate flight_id: {identifier}")
            continue
        seen.add(identifier)
        for field in ("data_file", "metadata_file"):
            value = item.get(field)
            if not isinstance(value, str):
                problems.append(f"{identifier}: missing {field}")
                continue
            path = (dataset / value).resolve()
            if dataset.resolve() not in path.parents or not path.is_file():
                problems.append(f"{identifier}: invalid or missing {field}: {value}")
    if manifest.get("flight_count") != len(index):
        problems.append("manifest flight_count differs from the index")
    return {"valid": not problems, "flight_count": len(index), "problems": problems}
