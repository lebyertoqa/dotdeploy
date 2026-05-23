"""Unit tests for cli_profile sub-commands."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from dotdeploy.config import Config
from dotdeploy.cli_profile import (
    cmd_profile_list,
    cmd_profile_add,
    cmd_profile_deploy,
    cmd_profile_undeploy,
)


class _Args:
    """Simple namespace substitute."""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture()
def config(tmp_path):
    p = tmp_path / "config.json"
    cfg = Config(str(p))
    cfg.load()
    return cfg


def test_list_empty(config, capsys):
    rc = cmd_profile_list(_Args(), config)
    assert rc == 0
    assert "No profiles" in capsys.readouterr().out


def test_list_shows_profiles(config, capsys):
    config.add_profile("home")
    config.add_profile("work")
    config.set("active_profile", "home")
    rc = cmd_profile_list(_Args(), config)
    assert rc == 0
    out = capsys.readouterr().out
    assert "* home" in out
    assert "  work" in out


def test_add_saves_profile(config, capsys):
    rc = cmd_profile_add(_Args(name="office"), config)
    assert rc == 0
    assert "office" in config.get("profiles", {})


def test_add_duplicate_returns_1(config, capsys):
    config.add_profile("dup")
    rc = cmd_profile_add(_Args(name="dup"), config)
    assert rc == 1


def test_deploy_no_name_no_active_returns_1(config, capsys):
    rc = cmd_profile_deploy(_Args(name=None), config)
    assert rc == 1


def test_deploy_calls_deploy_profile(config, capsys):
    config.add_profile("dev")
    with patch("dotdeploy.cli_profile.deploy_profile", return_value=["/a", "/b"]) as mock_dp:
        rc = cmd_profile_deploy(_Args(name="dev"), config)
    assert rc == 0
    mock_dp.assert_called_once_with("dev", config)
    assert config.get("active_profile") == "dev"


def test_undeploy_clears_active(config, capsys):
    config.add_profile("dev")
    config.set("active_profile", "dev")
    with patch("dotdeploy.cli_profile.undeploy_profile", return_value=["/a"]):
        rc = cmd_profile_undeploy(_Args(name="dev"), config)
    assert rc == 0
    assert config.get("active_profile") is None
