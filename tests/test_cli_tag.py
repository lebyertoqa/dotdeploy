"""Unit tests for dotdeploy.cli_tag."""

from __future__ import annotations

import argparse

import pytest

from dotdeploy.config import Config
from dotdeploy.cli_tag import (
    cmd_tag_add,
    cmd_tag_filter,
    cmd_tag_list,
    cmd_tag_remove,
)


class _Args(argparse.Namespace):
    def __init__(self, config_path: str, **kwargs):
        super().__init__()
        self.config = config_path
        for k, v in kwargs.items():
            setattr(self, k, v)


@pytest.fixture()
def config(tmp_path):
    c = Config(str(tmp_path / "dotdeploy.json"))
    c.load()
    c.data["profiles"]["home"] = {}
    c.data["profiles"]["work"] = {}
    c.save()
    return c


def test_tag_add_prints_confirmation(config, capsys):
    args = _Args(config.path, profile="home", tag="personal")
    cmd_tag_add(args)
    out = capsys.readouterr().out
    assert "personal" in out
    assert "home" in out


def test_tag_add_unknown_profile_exits(config, capsys):
    args = _Args(config.path, profile="ghost", tag="x")
    with pytest.raises(SystemExit) as exc:
        cmd_tag_add(args)
    assert exc.value.code == 1
    assert "Unknown profile" in capsys.readouterr().err


def test_tag_remove_success(config, capsys):
    from dotdeploy.tag import add_tag
    add_tag(config, "home", "personal")
    args = _Args(config.path, profile="home", tag="personal")
    cmd_tag_remove(args)
    out = capsys.readouterr().out
    assert "removed" in out


def test_tag_remove_missing_tag_exits(config, capsys):
    args = _Args(config.path, profile="home", tag="nope")
    with pytest.raises(SystemExit) as exc:
        cmd_tag_remove(args)
    assert exc.value.code == 1


def test_tag_list_empty(config, capsys):
    args = _Args(config.path, profile="home")
    cmd_tag_list(args)
    out = capsys.readouterr().out
    assert "No tags" in out


def test_tag_list_shows_tags(config, capsys):
    from dotdeploy.tag import add_tag
    add_tag(config, "home", "alpha")
    add_tag(config, "home", "beta")
    args = _Args(config.path, profile="home")
    cmd_tag_list(args)
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out


def test_tag_filter_no_match(config, capsys):
    args = _Args(config.path, tag="nope")
    cmd_tag_filter(args)
    out = capsys.readouterr().out
    assert "No profiles" in out


def test_tag_filter_returns_profiles(config, capsys):
    from dotdeploy.tag import add_tag
    add_tag(config, "home", "shared")
    add_tag(config, "work", "shared")
    args = _Args(config.path, tag="shared")
    cmd_tag_filter(args)
    out = capsys.readouterr().out
    assert "home" in out
    assert "work" in out
