"""Tests for dotdeploy.diff and dotdeploy.cli_diff."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from dotdeploy.diff import DiffResult, diff_profile
from dotdeploy.config import Config


@pytest.fixture()
def cfg(tmp_path):
    config_file = tmp_path / "dotdeploy.json"
    c = Config(str(config_file))
    c.load()
    c.add_profile("home")
    return c


def test_diff_unknown_profile_raises(cfg):
    with pytest.raises(KeyError, match="nope"):
        diff_profile(cfg, "nope")


def test_diff_empty_profile_is_clean(cfg):
    result = diff_profile(cfg, "home")
    assert result.clean
    assert result.profile == "home"


def test_diff_detects_missing_symlink(cfg, tmp_path):
    src = tmp_path / "bashrc"
    src.write_text("# bash")
    dst = tmp_path / ".bashrc"
    # Register in config but do NOT create the symlink
    cfg.profiles["home"].setdefault("symlinks", {})[str(src)] = str(dst)

    result = diff_profile(cfg, "home")
    assert str(dst) in result.missing
    assert not result.ok
    assert not result.clean


def test_diff_detects_ok_symlink(cfg, tmp_path):
    src = tmp_path / "vimrc"
    src.write_text("set nu")
    dst = tmp_path / ".vimrc"
    os.symlink(str(src), str(dst))
    cfg.profiles["home"].setdefault("symlinks", {})[str(src)] = str(dst)

    result = diff_profile(cfg, "home")
    assert str(dst) in result.ok
    assert not result.missing
    assert result.clean


def test_diff_detects_broken_symlink(cfg, tmp_path):
    src = tmp_path / "gone"
    dst = tmp_path / ".gone"
    # Symlink points to non-existent source
    os.symlink(str(src), str(dst))
    cfg.profiles["home"].setdefault("symlinks", {})[str(src)] = str(dst)

    result = diff_profile(cfg, "home")
    assert str(dst) in result.broken
    assert not result.clean


def test_diff_detects_extra_symlink(cfg, tmp_path):
    src = tmp_path / "real_src"
    src.write_text("data")
    wrong_src = tmp_path / "wrong_src"
    wrong_src.write_text("other")
    dst = tmp_path / ".cfg"
    # Symlink points to wrong_src, but config says it should point to src
    os.symlink(str(wrong_src), str(dst))
    cfg.profiles["home"].setdefault("symlinks", {})[str(src)] = str(dst)

    result = diff_profile(cfg, "home")
    assert str(dst) in result.extra
    assert not result.clean


def test_diff_result_clean_flag():
    r = DiffResult(profile="p")
    assert r.clean
    r.missing.append("/x")
    assert not r.clean
