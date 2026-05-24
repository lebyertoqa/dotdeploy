"""Profile status summary: combines diff, pin, and hook information."""

from dataclasses import dataclass, field
from typing import List, Optional

from .config import Config
from .diff import diff_profile, DiffResult
from .pin import get_pinned
from .hooks import list_hooks, VALID_EVENTS


class StatusError(Exception):
    pass


@dataclass
class ProfileStatus:
    profile: str
    pinned: bool
    total_links: int
    ok_links: int
    missing_links: List[str] = field(default_factory=list)
    broken_links: List[str] = field(default_factory=list)
    hooks: List[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return not self.missing_links and not self.broken_links

    def summary_line(self) -> str:
        state = "clean" if self.is_clean else "dirty"
        pin_marker = " [pinned]" if self.pinned else ""
        return (
            f"{self.profile}{pin_marker}: {state} "
            f"({self.ok_links}/{self.total_links} links ok, "
            f"{len(self.hooks)} hooks)"
        )


def profile_status(cfg: Config, profile: str) -> ProfileStatus:
    """Return a ProfileStatus for the given profile."""
    if profile not in cfg.list_profiles():
        raise StatusError(f"Unknown profile: {profile!r}")

    diff: DiffResult = diff_profile(cfg, profile)

    pinned_profile: Optional[str] = get_pinned(cfg)
    pinned = pinned_profile == profile

    hook_names: List[str] = []
    for event in VALID_EVENTS:
        for h in list_hooks(cfg, event):
            hook_names.append(f"{event}:{h}")

    return ProfileStatus(
        profile=profile,
        pinned=pinned,
        total_links=diff.total,
        ok_links=diff.ok,
        missing_links=diff.missing,
        broken_links=diff.broken,
        hooks=hook_names,
    )


def all_profiles_status(cfg: Config) -> List[ProfileStatus]:
    """Return ProfileStatus for every profile in the config."""
    return [profile_status(cfg, p) for p in cfg.list_profiles()]
