"""Unit tests for dotdeploy.alias."""

from __future__ import annotations

import pytest
from pathlib import Path

from dotdeploy.config import Config
from dotdeploy.alias import (
    AliasError,
    add_alias,
    list_aliases,
    remove_alias,
    resolve_alias,
)


@pytest.fixture()
def cfg(tmp_path: Path) -> Config:
    c = Config(tmp_path / "config.json")
    c.load()
    c.add_profile("work")
    c.add_profile("home")
    return c


def test_add_alias_persists(cfg):
    add_alias(cfg, "w", "work")
    cfg2 = Config(cfg.path)
    cfg2.load()
    assert list_aliases(cfg2)["w"] == "work"


def test_add_alias_idempotent(cfg):
    add_alias(cfg, "w", "work")
    add_alias(cfg, "w", "work")  # same mapping — should not raise
    assert list_aliases(cfg)["w"] == "work"


def test_add_alias_unknown_profile_raises(cfg):
    with pytest.raises(AliasError, match="does not exist"):
        add_alias(cfg, "x", "nonexistent")


def test_add_alias_collides_with_profile_name_raises(cfg):
    with pytest.raises(AliasError, match="already a profile name"):
        add_alias(cfg, "work", "home")


def test_add_alias_conflict_raises(cfg):
    add_alias(cfg, "w", "work")
    with pytest.raises(AliasError, match="already points to"):
        add_alias(cfg, "w", "home")


def test_remove_alias(cfg):
    add_alias(cfg, "w", "work")
    remove_alias(cfg, "w")
    assert "w" not in list_aliases(cfg)


def test_remove_alias_missing_raises(cfg):
    with pytest.raises(AliasError, match="not found"):
        remove_alias(cfg, "ghost")


def test_resolve_alias_known(cfg):
    add_alias(cfg, "w", "work")
    assert resolve_alias(cfg, "w") == "work"


def test_resolve_alias_passthrough(cfg):
    """Unknown names are returned unchanged (direct profile names)."""
    assert resolve_alias(cfg, "work") == "work"


def test_list_aliases_empty(cfg):
    assert list_aliases(cfg) == {}


def test_list_aliases_multiple(cfg):
    add_alias(cfg, "w", "work")
    add_alias(cfg, "h", "home")
    result = list_aliases(cfg)
    assert result == {"w": "work", "h": "home"}
