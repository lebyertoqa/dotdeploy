"""Tests for dotdeploy.cli_audit module."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from dotdeploy.audit import record_event
from dotdeploy.cli_audit import cmd_audit_clear, cmd_audit_list
from dotdeploy.config import Config


class _Args(argparse.Namespace):
    def __init__(self, config_path: str, limit: int = 0) -> None:
        super().__init__()
        self.config = config_path
        self.limit = limit


@pytest.fixture()
def config(tmp_path: Path) -> Config:
    cfg_path = tmp_path / "dotdeploy.json"
    cfg = Config(str(cfg_path))
    cfg.load()  # creates defaults
    return cfg


def test_list_empty_prints_message(config: Config, capsys: pytest.CaptureFixture) -> None:
    args = _Args(config.path)
    cmd_audit_list(args)
    out = capsys.readouterr().out
    assert "No audit events" in out


def test_list_shows_events(config: Config, capsys: pytest.CaptureFixture) -> None:
    cfg_dir = Path(config.path).parent
    record_event(cfg_dir, "deploy", profile="work", details={"files": 2})
    record_event(cfg_dir, "push")
    args = _Args(config.path)
    cmd_audit_list(args)
    out = capsys.readouterr().out
    assert "deploy" in out
    assert "work" in out
    assert "push" in out


def test_list_limit_restricts_output(config: Config, capsys: pytest.CaptureFixture) -> None:
    cfg_dir = Path(config.path).parent
    for i in range(5):
        record_event(cfg_dir, f"action_{i}")
    args = _Args(config.path, limit=2)
    cmd_audit_list(args)
    out = capsys.readouterr().out
    lines = [l for l in out.splitlines() if l.strip()]
    assert len(lines) == 2
    assert "action_4" in lines[-1]


def test_clear_removes_events(config: Config, capsys: pytest.CaptureFixture) -> None:
    cfg_dir = Path(config.path).parent
    record_event(cfg_dir, "deploy", profile="default")
    record_event(cfg_dir, "undeploy", profile="default")
    args = _Args(config.path)
    cmd_audit_clear(args)
    out = capsys.readouterr().out
    assert "2" in out
    # second clear should report 0
    cmd_audit_clear(args)
    out2 = capsys.readouterr().out
    assert "0" in out2
