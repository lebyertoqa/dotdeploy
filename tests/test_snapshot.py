"""Tests for dotdeploy.snapshot."""

import json
import pytest
from pathlib import Path

from dotdeploy.snapshot import (
    SnapshotError,
    create_snapshot,
    list_snapshots,
    load_snapshot,
    delete_snapshot,
)


@pytest.fixture()
def cfg_dir(tmp_path):
    return str(tmp_path)


LINKS = {
    str(Path.home() / ".bashrc"): "/dotfiles/bash/bashrc",
    str(Path.home() / ".vimrc"): "/dotfiles/vim/vimrc",
}


def test_create_snapshot_returns_filename(cfg_dir):
    name = create_snapshot(cfg_dir, "work", LINKS)
    assert name.startswith("work_")
    assert name.endswith(".json")


def test_create_snapshot_writes_file(cfg_dir):
    name = create_snapshot(cfg_dir, "work", LINKS)
    snap_path = Path(cfg_dir) / "snapshots" / name
    assert snap_path.exists()


def test_create_snapshot_content(cfg_dir):
    name = create_snapshot(cfg_dir, "home", LINKS)
    snap_path = Path(cfg_dir) / "snapshots" / name
    data = json.loads(snap_path.read_text())
    assert data["profile"] == "home"
    assert data["links"] == LINKS
    assert "created_at" in data


def test_create_snapshot_empty_profile_raises(cfg_dir):
    with pytest.raises(SnapshotError, match="profile_name"):
        create_snapshot(cfg_dir, "", LINKS)


def test_list_snapshots_empty(cfg_dir):
    assert list_snapshots(cfg_dir) == []


def test_list_snapshots_returns_all(cfg_dir):
    create_snapshot(cfg_dir, "work", LINKS)
    create_snapshot(cfg_dir, "home", LINKS)
    names = list_snapshots(cfg_dir)
    assert len(names) == 2


def test_list_snapshots_filtered_by_profile(cfg_dir):
    create_snapshot(cfg_dir, "work", LINKS)
    create_snapshot(cfg_dir, "work", LINKS)
    create_snapshot(cfg_dir, "home", LINKS)
    work_snaps = list_snapshots(cfg_dir, profile_name="work")
    assert len(work_snaps) == 2
    assert all(s.startswith("work_") for s in work_snaps)


def test_load_snapshot_returns_dict(cfg_dir):
    name = create_snapshot(cfg_dir, "work", LINKS)
    data = load_snapshot(cfg_dir, name)
    assert isinstance(data, dict)
    assert data["profile"] == "work"


def test_load_snapshot_missing_raises(cfg_dir):
    with pytest.raises(SnapshotError, match="not found"):
        load_snapshot(cfg_dir, "nonexistent_20240101T000000Z.json")


def test_delete_snapshot_removes_file(cfg_dir):
    name = create_snapshot(cfg_dir, "work", LINKS)
    delete_snapshot(cfg_dir, name)
    assert list_snapshots(cfg_dir) == []


def test_delete_snapshot_missing_raises(cfg_dir):
    with pytest.raises(SnapshotError, match="not found"):
        delete_snapshot(cfg_dir, "ghost_20240101T000000Z.json")
