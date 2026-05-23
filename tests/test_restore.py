"""Tests for dotdeploy.restore."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from dotdeploy.config import Config
from dotdeploy.restore import restore_snapshot, RestoreError
from dotdeploy.snapshot import _snapshot_dir


@pytest.fixture()
def cfg_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture()
def config(cfg_dir: Path) -> Config:
    cfg = Config(cfg_dir / "dotdeploy.json")
    cfg.load()
    cfg.add_profile("home")
    return cfg


def _write_snapshot(cfg: Config, profile: str, name: str, mappings: dict) -> None:
    snap_dir = _snapshot_dir(cfg, profile)
    snap_dir.mkdir(parents=True, exist_ok=True)
    snap_file = snap_dir / name
    snap_file.write_text(
        json.dumps({"profile": profile, "mappings": mappings}), encoding="utf-8"
    )


def test_restore_unknown_profile_raises(config: Config) -> None:
    with pytest.raises(RestoreError, match="Unknown profile"):
        restore_snapshot(config, "nonexistent", "snap.json")


def test_restore_missing_snapshot_raises(config: Config) -> None:
    with pytest.raises(RestoreError, match="Cannot load snapshot"):
        restore_snapshot(config, "home", "missing.json")


def test_restore_empty_mappings_raises(config: Config, tmp_path: Path) -> None:
    _write_snapshot(config, "home", "empty.json", {})
    with pytest.raises(RestoreError, match="no mappings"):
        restore_snapshot(config, "home", "empty.json")


def test_restore_creates_symlinks(config: Config, tmp_path: Path) -> None:
    src_file = tmp_path / "dotfiles" / ".bashrc"
    src_file.parent.mkdir(parents=True)
    src_file.write_text("# bashrc", encoding="utf-8")

    tgt_file = tmp_path / "home" / ".bashrc"
    tgt_file.parent.mkdir(parents=True)

    _write_snapshot(
        config,
        "home",
        "snap.json",
        {str(src_file): str(tgt_file)},
    )

    restored = restore_snapshot(config, "home", "snap.json", backup=False)

    assert str(tgt_file) in restored
    assert tgt_file.is_symlink()
    assert os.readlink(str(tgt_file)) == str(src_file)


def test_restore_persists_mappings_to_config(config: Config, tmp_path: Path) -> None:
    src_file = tmp_path / "src" / ".vimrc"
    src_file.parent.mkdir(parents=True)
    src_file.write_text("set nu", encoding="utf-8")

    tgt_file = tmp_path / "tgt" / ".vimrc"
    tgt_file.parent.mkdir(parents=True)

    _write_snapshot(
        config,
        "home",
        "snap2.json",
        {str(src_file): str(tgt_file)},
    )

    restore_snapshot(config, "home", "snap2.json", backup=False)

    reloaded = Config(config.path)
    reloaded.load()
    mappings = reloaded.get("profiles", {}).get("home", {}).get("mappings", {})
    assert str(src_file) in mappings
