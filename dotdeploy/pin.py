"""Profile pinning — mark a profile as active and persist the choice."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from dotdeploy.config import Config

PIN_KEY = "active_profile"


class PinError(Exception):
    """Raised when a pin operation fails."""


def pin_profile(cfg: Config, profile: str) -> None:
    """Mark *profile* as the active (pinned) profile.

    Raises PinError if the profile does not exist in the config.
    """
    if profile not in cfg.list_profiles():
        raise PinError(f"Profile {profile!r} does not exist.")
    cfg.set(PIN_KEY, profile)
    cfg.save()


def unpin_profile(cfg: Config) -> None:
    """Remove the active-profile pin, if any."""
    cfg.set(PIN_KEY, None)
    cfg.save()


def get_pinned(cfg: Config) -> Optional[str]:
    """Return the currently pinned profile name, or *None* if none is set."""
    return cfg.get(PIN_KEY)  # type: ignore[return-value]
