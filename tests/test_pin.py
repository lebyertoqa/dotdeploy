"""Tests for dotdeploy.pin and dotdeploy.cli_pin."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from dotdeploy.config import Config
from dotdeploy.pin import PIN_KEY, PinError, get_pinned, pin_profile, unpin_profile


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def cfg(tmp_path: Path) -> Config:
    c = Config(tmp_path / "config.json")
    c.load()
    c.add_profile("work")
    c.add_profile("home")
    return c


# ---------------------------------------------------------------------------
# Unit tests for pin.py
# ---------------------------------------------------------------------------

def test_pin_profile_sets_key(cfg: Config) -> None:
    pin_profile(cfg, "work")
    assert cfg.get(PIN_KEY) == "work"


def test_pin_profile_persists(cfg: Config) -> None:
    pin_profile(cfg, "home")
    reloaded = Config(cfg._path)  # type: ignore[attr-defined]
    reloaded.load()
    assert reloaded.get(PIN_KEY) == "home"


def test_pin_unknown_profile_raises(cfg: Config) -> None:
    with pytest.raises(PinError, match="does not exist"):
        pin_profile(cfg, "nonexistent")


def test_get_pinned_none_by_default(cfg: Config) -> None:
    assert get_pinned(cfg) is None


def test_get_pinned_returns_name(cfg: Config) -> None:
    pin_profile(cfg, "work")
    assert get_pinned(cfg) == "work"


def test_unpin_clears_value(cfg: Config) -> None:
    pin_profile(cfg, "work")
    unpin_profile(cfg)
    assert get_pinned(cfg) is None


def test_unpin_persists(cfg: Config) -> None:
    pin_profile(cfg, "work")
    unpin_profile(cfg)
    reloaded = Config(cfg._path)  # type: ignore[attr-defined]
    reloaded.load()
    assert reloaded.get(PIN_KEY) is None


# ---------------------------------------------------------------------------
# CLI integration tests
# ---------------------------------------------------------------------------

class _Args(argparse.Namespace):
    def __init__(self, cfg: Config, **kwargs):
        super().__init__()
        self.config = str(cfg._path)  # type: ignore[attr-defined]
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_cmd_pin_set_prints_name(cfg: Config, capsys) -> None:
    from dotdeploy.cli_pin import cmd_pin_set
    cmd_pin_set(_Args(cfg, profile="home"))
    out = capsys.readouterr().out
    assert "home" in out


def test_cmd_pin_set_unknown_exits(cfg: Config) -> None:
    from dotdeploy.cli_pin import cmd_pin_set
    with pytest.raises(SystemExit):
        cmd_pin_set(_Args(cfg, profile="ghost"))


def test_cmd_pin_show_no_pin(cfg: Config, capsys) -> None:
    from dotdeploy.cli_pin import cmd_pin_show
    cmd_pin_show(_Args(cfg))
    assert "No profile" in capsys.readouterr().out


def test_cmd_pin_show_with_pin(cfg: Config, capsys) -> None:
    from dotdeploy.cli_pin import cmd_pin_show
    pin_profile(cfg, "work")
    cmd_pin_show(_Args(cfg))
    assert "work" in capsys.readouterr().out


def test_cmd_pin_clear_removes_pin(cfg: Config, capsys) -> None:
    from dotdeploy.cli_pin import cmd_pin_clear
    pin_profile(cfg, "work")
    cmd_pin_clear(_Args(cfg))
    assert get_pinned(cfg) is None
    assert "cleared" in capsys.readouterr().out
