"""Tests for dotdeploy.cli_alias sub-commands."""

from __future__ import annotations

import sys
import pytest
from pathlib import Path

from dotdeploy.config import Config
from dotdeploy.alias import add_alias
from dotdeploy.cli_alias import (
    cmd_alias_add,
    cmd_alias_list,
    cmd_alias_remove,
    cmd_alias_resolve,
)


class _Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


@pytest.fixture()
def config(tmp_path: Path) -> Config:
    cfg = Config(tmp_path / "config.json")
    cfg.load()
    cfg.add_profile("work")
    cfg.add_profile("home")
    return cfg


def test_alias_add_prints_confirmation(config, capsys):
    args = _Args(config=str(config.path), alias="w", profile="work")
    cmd_alias_add(args)
    out = capsys.readouterr().out
    assert "w" in out and "work" in out


def test_alias_add_unknown_profile_exits(config):
    args = _Args(config=str(config.path), alias="x", profile="ghost")
    with pytest.raises(SystemExit) as exc_info:
        cmd_alias_add(args)
    assert exc_info.value.code != 0


def test_alias_list_empty(config, capsys):
    args = _Args(config=str(config.path))
    cmd_alias_list(args)
    out = capsys.readouterr().out
    assert "No aliases" in out


def test_alias_list_shows_entries(config, capsys):
    add_alias(config, "w", "work")
    args = _Args(config=str(config.path))
    cmd_alias_list(args)
    out = capsys.readouterr().out
    assert "w" in out
    assert "work" in out


def test_alias_remove_success(config, capsys):
    add_alias(config, "w", "work")
    args = _Args(config=str(config.path), alias="w")
    cmd_alias_remove(args)
    out = capsys.readouterr().out
    assert "removed" in out.lower()


def test_alias_remove_missing_exits(config):
    args = _Args(config=str(config.path), alias="ghost")
    with pytest.raises(SystemExit) as exc_info:
        cmd_alias_remove(args)
    assert exc_info.value.code != 0


def test_alias_resolve_known(config, capsys):
    add_alias(config, "w", "work")
    args = _Args(config=str(config.path), name="w")
    cmd_alias_resolve(args)
    out = capsys.readouterr().out
    assert out.strip() == "work"


def test_alias_resolve_passthrough(config, capsys):
    args = _Args(config=str(config.path), name="work")
    cmd_alias_resolve(args)
    out = capsys.readouterr().out
    assert out.strip() == "work"
