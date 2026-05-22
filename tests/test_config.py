"""Tests for dotdeploy configuration management."""

import json
import pytest
from pathlib import Path

from dotdeploy.config import Config, DEFAULT_CONFIG


@pytest.fixture
def tmp_config(tmp_path):
    """Return a Config instance backed by a temporary directory."""
    config_file = tmp_path / "config.json"
    cfg = Config(config_path=config_file)
    cfg.load()
    return cfg


def test_load_creates_defaults_when_missing(tmp_path):
    cfg = Config(config_path=tmp_path / "nonexistent.json")
    cfg.load()
    assert cfg.active_profile == "default"
    assert "default" in cfg.profiles


def test_save_and_reload(tmp_config, tmp_path):
    tmp_config.set("active_profile", "default")
    tmp_config.save()
    cfg2 = Config(config_path=tmp_config.config_path)
    cfg2.load()
    assert cfg2.active_profile == "default"


def test_add_profile(tmp_config):
    tmp_config.add_profile("work")
    assert "work" in tmp_config.profiles
    assert tmp_config.profiles["work"] == {"files": []}


def test_add_duplicate_profile_raises(tmp_config):
    tmp_config.add_profile("home")
    with pytest.raises(ValueError, match="already exists"):
        tmp_config.add_profile("home")


def test_remove_profile(tmp_config):
    tmp_config.add_profile("temp")
    tmp_config.remove_profile("temp")
    assert "temp" not in tmp_config.profiles


def test_remove_default_profile_raises(tmp_config):
    with pytest.raises(ValueError, match="Cannot remove the default profile"):
        tmp_config.remove_profile("default")


def test_switch_active_profile(tmp_config):
    tmp_config.add_profile("gaming")
    tmp_config.active_profile = "gaming"
    assert tmp_config.active_profile == "gaming"


def test_switch_to_nonexistent_profile_raises(tmp_config):
    with pytest.raises(ValueError, match="does not exist"):
        tmp_config.active_profile = "ghost"


def test_remove_active_profile_resets_to_default(tmp_config):
    tmp_config.add_profile("office")
    tmp_config.active_profile = "office"
    tmp_config.remove_profile("office")
    assert tmp_config.active_profile == "default"


def test_to_dict_returns_copy(tmp_config):
    d = tmp_config.to_dict()
    assert isinstance(d, dict)
    assert "profiles" in d
    assert "active_profile" in d
