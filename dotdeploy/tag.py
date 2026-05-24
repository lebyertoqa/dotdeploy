"""Profile tagging — assign tags to profiles for grouping and filtering."""

from __future__ import annotations

from typing import List

from .config import Config

TAGS_KEY = "tags"


class TagError(Exception):
    """Raised when a tagging operation fails."""


def _profile_tags(cfg: Config, profile: str) -> List[str]:
    """Return the mutable tags list for *profile*, creating it if absent."""
    if profile not in cfg.get("profiles", {}):
        raise TagError(f"Unknown profile: {profile!r}")
    profiles = cfg.get("profiles")
    entry = profiles.setdefault(profile, {})
    return entry.setdefault(TAGS_KEY, [])


def add_tag(cfg: Config, profile: str, tag: str) -> None:
    """Add *tag* to *profile*.  No-op if the tag already exists."""
    tags = _profile_tags(cfg, profile)
    if tag not in tags:
        tags.append(tag)
        cfg.save()


def remove_tag(cfg: Config, profile: str, tag: str) -> None:
    """Remove *tag* from *profile*.  Raises TagError if tag not present."""
    tags = _profile_tags(cfg, profile)
    if tag not in tags:
        raise TagError(f"Tag {tag!r} not found on profile {profile!r}")
    tags.remove(tag)
    cfg.save()


def list_tags(cfg: Config, profile: str) -> List[str]:
    """Return a sorted copy of the tags assigned to *profile*."""
    return sorted(_profile_tags(cfg, profile))


def profiles_with_tag(cfg: Config, tag: str) -> List[str]:
    """Return a sorted list of profile names that carry *tag*."""
    result = []
    for name, data in cfg.get("profiles", {}).items():
        if tag in data.get(TAGS_KEY, []):
            result.append(name)
    return sorted(result)
