"""Restore a dotfiles profile from a snapshot."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

from dotdeploy.config import Config
from dotdeploy.snapshot import load_snapshot
from dotdeploy.symlink import create_symlink, SymlinkError


class RestoreError(Exception):
    """Raised when a restore operation fails."""


def restore_snapshot(
    cfg: Config,
    profile: str,
    snapshot_name: str,
    *,
    backup: bool = True,
) -> List[str]:
    """Restore symlinks for *profile* from *snapshot_name*.

    Returns a list of target paths that were successfully linked.
    Raises :class:`RestoreError` on any unrecoverable problem.
    """
    if profile not in cfg.get("profiles", {}):
        raise RestoreError(f"Unknown profile: {profile!r}")

    try:
        data: Dict = load_snapshot(cfg, profile, snapshot_name)
    except Exception as exc:  # noqa: BLE001
        raise RestoreError(f"Cannot load snapshot {snapshot_name!r}: {exc}") from exc

    mappings: Dict[str, str] = data.get("mappings", {})
    if not mappings:
        raise RestoreError(
            f"Snapshot {snapshot_name!r} for profile {profile!r} contains no mappings."
        )

    restored: List[str] = []
    errors: List[str] = []

    for src, tgt in mappings.items():
        try:
            create_symlink(Path(src), Path(tgt), backup=backup)
            restored.append(tgt)
        except SymlinkError as exc:
            errors.append(f"{tgt}: {exc}")

    if errors:
        detail = "; ".join(errors)
        raise RestoreError(f"Restore completed with errors — {detail}")

    # Persist the restored mappings back into the live config
    cfg.get("profiles", {})[profile]["mappings"] = mappings
    cfg.save()

    return restored
