"""Stable identifiers and streaming file hashes."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def flight_id(path: Path, digest: str) -> str:
    safe_stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", path.stem).strip("-") or "flight"
    return f"{safe_stem}-{digest[:10]}"


def private_alias(digest: str) -> str:
    return f"flight-{digest[:16]}"
