"""Snapshot support: capture and restore the current deployed state of a profile."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

SNAPSHOT_DIR_NAME = "snapshots"


class SnapshotError(Exception):
    """Raised when a snapshot operation fails."""


def _snapshot_dir(config_dir: str) -> Path:
    d = Path(config_dir) / SNAPSHOT_DIR_NAME
    d.mkdir(parents=True, exist_ok=True)
    return d


def create_snapshot(config_dir: str, profile_name: str, links: Dict[str, str]) -> str:
    """Persist a snapshot of *links* for *profile_name*.

    *links* is a mapping of ``{target: source}`` exactly as stored in the
    profile config.  Returns the snapshot filename (not the full path).
    """
    if not profile_name:
        raise SnapshotError("profile_name must not be empty")

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"{profile_name}_{ts}.json"
    snapshot_path = _snapshot_dir(config_dir) / filename

    payload = {
        "profile": profile_name,
        "created_at": ts,
        "links": links,
    }
    snapshot_path.write_text(json.dumps(payload, indent=2))
    return filename


def list_snapshots(config_dir: str, profile_name: str | None = None) -> List[str]:
    """Return snapshot filenames, optionally filtered by *profile_name*."""
    d = _snapshot_dir(config_dir)
    files = sorted(f.name for f in d.glob("*.json"))
    if profile_name:
        files = [f for f in files if f.startswith(f"{profile_name}_")]
    return files


def load_snapshot(config_dir: str, filename: str) -> dict:
    """Load and return the raw snapshot dict for *filename*."""
    snapshot_path = _snapshot_dir(config_dir) / filename
    if not snapshot_path.exists():
        raise SnapshotError(f"Snapshot not found: {filename}")
    return json.loads(snapshot_path.read_text())


def delete_snapshot(config_dir: str, filename: str) -> None:
    """Delete a single snapshot file."""
    snapshot_path = _snapshot_dir(config_dir) / filename
    if not snapshot_path.exists():
        raise SnapshotError(f"Snapshot not found: {filename}")
    snapshot_path.unlink()
