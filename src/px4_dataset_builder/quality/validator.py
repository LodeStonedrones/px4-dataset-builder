"""Validate a built dataset's structure, metadata, and artifact evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from px4_dataset_builder.utils.hashing import sha256_file

SUPPORTED_MANIFEST_SCHEMAS = {"1.0", "1.1"}


def validate_dataset(dataset: Path) -> dict[str, Any]:
    problems: list[str] = []
    warnings: list[str] = []
    manifest_path = dataset / "manifest.json"
    index_path = dataset / "flights" / "index.json"
    if not manifest_path.is_file():
        return {
            "valid": False,
            "flight_count": 0,
            "problems": ["manifest.json is missing"],
            "warnings": [],
        }
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return {
            "valid": False,
            "flight_count": 0,
            "problems": [f"manifest.json cannot be read: {exc}"],
            "warnings": [],
        }
    if not isinstance(manifest, dict):
        return {
            "valid": False,
            "flight_count": 0,
            "problems": ["manifest.json root must be an object"],
            "warnings": [],
        }
    if manifest.get("schema_version") not in SUPPORTED_MANIFEST_SCHEMAS:
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
        metadata_file = item.get("metadata_file")
        if isinstance(metadata_file, str) and _is_dataset_file(dataset, metadata_file):
            _validate_metadata(dataset / metadata_file, identifier, problems)
    files = manifest.get("files")
    if not isinstance(files, dict):
        problems.append("manifest files must be an object")
    else:
        for name, value in files.items():
            if not isinstance(value, str) or not _is_dataset_file(dataset, value):
                problems.append(f"invalid or missing manifest file {name}: {value}")
    if manifest.get("flight_count") != len(index):
        problems.append("manifest flight_count differs from the index")
    if manifest.get("schema_version") == "1.1":
        _validate_artifacts(dataset, manifest, problems)
        _validate_configuration(dataset, manifest, problems)
    elif manifest.get("schema_version") == "1.0":
        warnings.append("Manifest schema 1.0 has no required artifact checksums")
    return {
        "valid": not problems,
        "flight_count": len(index),
        "problems": problems,
        "warnings": warnings,
    }


def _is_dataset_file(dataset: Path, value: str) -> bool:
    root = dataset.resolve()
    path = (root / value).resolve()
    return root in path.parents and path.is_file()


def _validate_metadata(path: Path, expected_flight_id: str, problems: list[str]) -> None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        problems.append(f"{expected_flight_id}: metadata cannot be read: {exc}")
        return
    if not isinstance(payload, dict) or payload.get("flight_id") != expected_flight_id:
        problems.append(f"{expected_flight_id}: metadata flight_id does not match the index")


def _validate_artifacts(dataset: Path, manifest: dict[str, Any], problems: list[str]) -> None:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        problems.append("manifest artifacts must be an object")
        return
    for relative_path, evidence in artifacts.items():
        if not isinstance(relative_path, str) or not isinstance(evidence, dict):
            problems.append(f"invalid artifact evidence: {relative_path}")
            continue
        if not _is_dataset_file(dataset, relative_path):
            problems.append(f"invalid or missing artifact: {relative_path}")
            continue
        expected_hash = evidence.get("sha256")
        expected_size = evidence.get("size_bytes")
        path = dataset / relative_path
        if not isinstance(expected_hash, str) or len(expected_hash) != 64:
            problems.append(f"{relative_path}: invalid SHA-256 evidence")
        elif sha256_file(path) != expected_hash:
            problems.append(f"{relative_path}: SHA-256 checksum mismatch")
        if not isinstance(expected_size, int) or expected_size < 0:
            problems.append(f"{relative_path}: invalid size evidence")
        elif path.stat().st_size != expected_size:
            problems.append(f"{relative_path}: file size mismatch")

    required_artifacts = {
        str(item[field])
        for item in _index_entries(dataset)
        for field in ("data_file", "metadata_file")
        if isinstance(item.get(field), str)
    }
    files = manifest.get("files")
    if isinstance(files, dict):
        required_artifacts.update(value for value in files.values() if isinstance(value, str))
    missing_evidence = sorted(required_artifacts - artifacts.keys())
    for relative_path in missing_evidence:
        problems.append(f"artifact checksum evidence is missing: {relative_path}")


def _validate_configuration(dataset: Path, manifest: dict[str, Any], problems: list[str]) -> None:
    evidence = manifest.get("configuration")
    if not isinstance(evidence, dict):
        problems.append("manifest configuration evidence must be an object")
        return
    relative_path = evidence.get("file")
    expected_hash = evidence.get("sha256")
    if not isinstance(relative_path, str) or not _is_dataset_file(dataset, relative_path):
        problems.append("effective configuration file is invalid or missing")
        return
    try:
        payload = json.loads((dataset / relative_path).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        problems.append(f"effective configuration cannot be read: {exc}")
        return
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    actual_hash = hashlib.sha256(canonical).hexdigest()
    if not isinstance(expected_hash, str) or actual_hash != expected_hash:
        problems.append("effective configuration digest mismatch")


def _index_entries(dataset: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads((dataset / "flights" / "index.json").read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return [item for item in payload if isinstance(item, dict)] if isinstance(payload, list) else []
