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
    if not isinstance(manifest, dict):
        return {"valid": False, "problems": ["manifest.json root must be an object"]}
    if manifest.get("schema_version") != "1.0":
        problems.append(f"Unsupported manifest schema: {manifest.get('schema_version')}")
    index: list[Any]
    if not index_path.is_file():
        problems.append("flights/index.json is missing")
        index = []
    else:
        try:
            loaded_index = json.loads(index_path.read_text(encoding="utf-8"))
            if not isinstance(loaded_index, list):
                problems.append("flights/index.json root must be an array")
                index = []
            else:
                index = loaded_index
        except (json.JSONDecodeError, OSError) as exc:
            problems.append(f"Flight index cannot be read: {exc}")
            index = []
    seen: set[str] = set()
    for item in index:
        if not isinstance(item, dict):
            problems.append("Flight index entries must be objects")
            continue
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
            if not _is_dataset_file(dataset, value):
                problems.append(f"{identifier}: invalid or missing {field}: {value}")
    files = manifest.get("files")
    if not isinstance(files, dict):
        problems.append("manifest files must be an object")
    else:
        for name, value in files.items():
            if not isinstance(value, str) or not _is_dataset_file(dataset, value):
                problems.append(f"invalid or missing manifest file {name}: {value}")
    if manifest.get("flight_count") != len(index):
        problems.append("manifest flight_count differs from the index")
    return {"valid": not problems, "flight_count": len(index), "problems": problems}


def _is_dataset_file(dataset: Path, value: str) -> bool:
    root = dataset.resolve()
    path = (root / value).resolve()
    return root in path.parents and path.is_file()
