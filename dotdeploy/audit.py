"""Audit log: record deploy/undeploy/symlink events to a JSONL file."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

AUDIT_FILENAME = "audit.log"


class AuditError(Exception):
    """Raised when audit log operations fail."""


def _audit_path(config_dir: Path) -> Path:
    return config_dir / AUDIT_FILENAME


def record_event(
    config_dir: Path,
    action: str,
    profile: Optional[str] = None,
    details: Optional[Dict] = None,
) -> Dict:
    """Append a single event to the audit log and return the entry."""
    entry: Dict = {
        "timestamp": time.time(),
        "action": action,
    }
    if profile is not None:
        entry["profile"] = profile
    if details:
        entry["details"] = details

    path = _audit_path(config_dir)
    try:
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
    except OSError as exc:
        raise AuditError(f"Cannot write audit log: {exc}") from exc

    return entry


def read_events(config_dir: Path) -> List[Dict]:
    """Return all audit log entries in chronological order."""
    path = _audit_path(config_dir)
    if not path.exists():
        return []
    events: List[Dict] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                events.append(json.loads(line))
    except (OSError, json.JSONDecodeError) as exc:
        raise AuditError(f"Cannot read audit log: {exc}") from exc
    return events


def clear_events(config_dir: Path) -> int:
    """Delete the audit log file. Returns number of entries that were present."""
    events = read_events(config_dir)
    path = _audit_path(config_dir)
    if path.exists():
        path.unlink()
    return len(events)
