"""File watcher that detects when deployed dotfiles drift from their symlink targets."""

import os
import time
from dataclasses import dataclass, field
from typing import List, Optional

from dotdeploy.config import Config
from dotdeploy.diff import diff_profile


class WatchError(Exception):
    """Raised when the watcher encounters an unrecoverable error."""


@dataclass
class WatchEvent:
    profile: str
    changed_targets: List[str]
    timestamp: float = field(default_factory=time.time)

    def __str__(self) -> str:  # pragma: no cover
        targets = ", ".join(self.changed_targets)
        ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(self.timestamp))
        return f"[{ts}] profile={self.profile} changed={targets}"


def _collect_dirty_targets(cfg: Config, profile: str) -> List[str]:
    """Return list of symlink targets that are no longer correct for *profile*."""
    result = diff_profile(cfg, profile)
    dirty = []
    for issue in result.issues:
        # issue.target is the filesystem path that should be a symlink
        dirty.append(issue.target)
    return dirty


def poll_once(cfg: Config, profiles: Optional[List[str]] = None) -> List[WatchEvent]:
    """Check all (or specified) profiles once and return drift events."""
    if profiles is None:
        profiles = cfg.list_profiles()

    events: List[WatchEvent] = []
    for profile in profiles:
        if profile not in cfg.list_profiles():
            raise WatchError(f"Unknown profile: {profile!r}")
        dirty = _collect_dirty_targets(cfg, profile)
        if dirty:
            events.append(WatchEvent(profile=profile, changed_targets=dirty))
    return events


def watch(cfg: Config, profiles: Optional[List[str]] = None,
          interval: float = 5.0, max_polls: Optional[int] = None):
    """Continuously poll for drift, yielding WatchEvent objects.

    Stops after *max_polls* iterations (useful for testing).
    """
    polls = 0
    while True:
        events = poll_once(cfg, profiles)
        for event in events:
            yield event
        polls += 1
        if max_polls is not None and polls >= max_polls:
            return
        time.sleep(interval)  # pragma: no cover
