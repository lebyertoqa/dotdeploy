"""Profile priority management for dotdeploy.

Allows assigning integer priorities to profiles so that when multiple
profiles define the same symlink target the highest-priority profile wins.
"""

from __future__ import annotations

from typing import List, Tuple

from .config import Config

_PRIORITY_KEY = "priorities"
_DEFAULT_PRIORITY = 0


class PriorityError(Exception):
    """Raised when a priority operation fails."""


def set_priority(cfg: Config, profile: str, value: int) -> None:
    """Set the priority for *profile*.

    Raises PriorityError if the profile does not exist.
    """
    if profile not in cfg.get("profiles", {}):
        raise PriorityError(f"Unknown profile: {profile!r}")
    priorities: dict = cfg.get(_PRIORITY_KEY, {})
    priorities[profile] = value
    cfg.set(_PRIORITY_KEY, priorities)
    cfg.save()


def get_priority(cfg: Config, profile: str) -> int:
    """Return the priority for *profile* (default 0).

    Raises PriorityError if the profile does not exist.
    """
    if profile not in cfg.get("profiles", {}):
        raise PriorityError(f"Unknown profile: {profile!r}")
    return cfg.get(_PRIORITY_KEY, {}).get(profile, _DEFAULT_PRIORITY)


def clear_priority(cfg: Config, profile: str) -> None:
    """Remove any explicit priority for *profile*, reverting to the default.

    Raises PriorityError if the profile does not exist.
    """
    if profile not in cfg.get("profiles", {}):
        raise PriorityError(f"Unknown profile: {profile!r}")
    priorities: dict = cfg.get(_PRIORITY_KEY, {})
    priorities.pop(profile, None)
    cfg.set(_PRIORITY_KEY, priorities)
    cfg.save()


def ranked_profiles(cfg: Config) -> List[Tuple[str, int]]:
    """Return all profiles sorted by priority descending (highest first).

    Each element is a ``(profile_name, priority)`` tuple.
    """
    profiles = list(cfg.get("profiles", {}).keys())
    priorities = cfg.get(_PRIORITY_KEY, {})
    ranked = [(p, priorities.get(p, _DEFAULT_PRIORITY)) for p in profiles]
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked
