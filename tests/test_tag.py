"""Unit tests for dotdeploy.tag."""

from __future__ import annotations

import pytest

from dotdeploy.config import Config
from dotdeploy.tag import TagError, add_tag, list_tags, profiles_with_tag, remove_tag


@pytest.fixture()
def cfg(tmp_path):
    c = Config(str(tmp_path / "dotdeploy.json"))
    c.load()
    c.data["profiles"]["home"] = {}
    c.data["profiles"]["work"] = {}
    c.save()
    return c


def test_add_tag_persists(cfg):
    add_tag(cfg, "home", "personal")
    assert "personal" in cfg.data["profiles"]["home"]["tags"]


def test_add_tag_idempotent(cfg):
    add_tag(cfg, "home", "personal")
    add_tag(cfg, "home", "personal")
    assert cfg.data["profiles"]["home"]["tags"].count("personal") == 1


def test_add_tag_unknown_profile_raises(cfg):
    with pytest.raises(TagError, match="Unknown profile"):
        add_tag(cfg, "ghost", "x")


def test_remove_tag(cfg):
    add_tag(cfg, "home", "personal")
    remove_tag(cfg, "home", "personal")
    assert "personal" not in cfg.data["profiles"]["home"].get("tags", [])


def test_remove_tag_not_present_raises(cfg):
    with pytest.raises(TagError, match="not found"):
        remove_tag(cfg, "home", "nonexistent")


def test_remove_tag_unknown_profile_raises(cfg):
    with pytest.raises(TagError, match="Unknown profile"):
        remove_tag(cfg, "ghost", "x")


def test_list_tags_empty(cfg):
    assert list_tags(cfg, "home") == []


def test_list_tags_sorted(cfg):
    add_tag(cfg, "home", "zebra")
    add_tag(cfg, "home", "alpha")
    assert list_tags(cfg, "home") == ["alpha", "zebra"]


def test_list_tags_unknown_profile_raises(cfg):
    with pytest.raises(TagError, match="Unknown profile"):
        list_tags(cfg, "ghost")


def test_profiles_with_tag_empty(cfg):
    assert profiles_with_tag(cfg, "personal") == []


def test_profiles_with_tag_matches(cfg):
    add_tag(cfg, "home", "personal")
    add_tag(cfg, "work", "personal")
    result = profiles_with_tag(cfg, "personal")
    assert result == ["home", "work"]


def test_profiles_with_tag_partial_match(cfg):
    add_tag(cfg, "home", "personal")
    result = profiles_with_tag(cfg, "personal")
    assert result == ["home"]
    assert "work" not in result
