"""Profile alias support — map short names to existing profiles."""

from __future__ import annotations

from dotdeploy.config import Config

_ALIAS_KEY = "aliases"


class AliasError(Exception):
    """Raised when an alias operation fails."""


def _aliases(cfg: Config) -> dict:
    return cfg.data.setdefault(_ALIAS_KEY, {})


def add_alias(cfg: Config, alias: str, profile: str) -> None:
    """Register *alias* as a short-name for *profile*.

    Raises AliasError if the profile does not exist, if the alias
    already maps to a different profile, or if the alias name
    collides with an existing profile name.
    """
    if profile not in cfg.list_profiles():
        raise AliasError(f"Profile {profile!r} does not exist.")
    if alias in cfg.list_profiles():
        raise AliasError(f"{alias!r} is already a profile name.")
    existing = _aliases(cfg).get(alias)
    if existing is not None and existing != profile:
        raise AliasError(
            f"Alias {alias!r} already points to {existing!r}."
        )
    _aliases(cfg)[alias] = profile
    cfg.save()


def remove_alias(cfg: Config, alias: str) -> None:
    """Remove *alias*. Raises AliasError if it does not exist."""
    if alias not in _aliases(cfg):
        raise AliasError(f"Alias {alias!r} not found.")
    del _aliases(cfg)[alias]
    cfg.save()


def resolve_alias(cfg: Config, name: str) -> str:
    """Return the profile name that *name* resolves to.

    If *name* is a known alias the target profile is returned;
    otherwise *name* is returned unchanged (it may be a direct
    profile name — callers are responsible for validating it).
    """
    return _aliases(cfg).get(name, name)


def list_aliases(cfg: Config) -> dict[str, str]:
    """Return a copy of the alias mapping {alias: profile}."""
    return dict(_aliases(cfg))
