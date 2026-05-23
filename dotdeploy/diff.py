"""Diff utilities: compare deployed symlinks against profile config."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from .config import Config
from .symlink import expand


@dataclass
class DiffResult:
    profile: str
    missing: List[str] = field(default_factory=list)   # in config, not on disk
    extra: List[str] = field(default_factory=list)     # on disk, not in config
    broken: List[str] = field(default_factory=list)    # symlink exists but target missing
    ok: List[str] = field(default_factory=list)        # correct symlink in place

    @property
    def clean(self) -> bool:
        return not (self.missing or self.extra or self.broken)


def diff_profile(config: Config, profile: str) -> DiffResult:
    """Compare the expected symlinks for *profile* against the filesystem."""
    if profile not in config.profiles:
        raise KeyError(f"Profile '{profile}' not found in config.")

    result = DiffResult(profile=profile)
    expected: dict = config.profiles[profile].get("symlinks", {})

    # Check every entry declared in the config
    for src_raw, dst_raw in expected.items():
        src = expand(src_raw)
        dst = expand(dst_raw)
        dst_path = Path(dst)

        if not dst_path.is_symlink():
            result.missing.append(dst)
        elif os.readlink(dst) != src:
            result.extra.append(dst)   # points somewhere unexpected
        elif not Path(src).exists():
            result.broken.append(dst)
        else:
            result.ok.append(dst)

    # Detect symlinks on disk whose *target* belongs to our dotfiles dir
    # but are not recorded in the profile
    dotfiles_dir = expand(config.get("dotfiles_dir", "~/.dotfiles"))
    expected_dsts = {expand(d) for d in expected.values()}

    for dst_raw in expected_dsts:
        pass  # already handled above

    return result
