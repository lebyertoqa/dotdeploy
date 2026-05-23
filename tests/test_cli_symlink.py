"""Tests for dotdeploy.cli_symlink subcommands."""

import json
from pathlib import Path

import pytest

from dotdeploy.config import Config
from dotdeploy.cli_symlink import cmd_symlink_add, cmd_symlink_remove


class _Args:
    """Simple namespace mimic for argparse args."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture()
def setup(tmp_path):
    cfg_path = tmp_path / "dotdeploy.json"
    cfg = Config(str(cfg_path))
    cfg.load()  # creates defaults
    cfg.set("active_profile", "default")
    cfg.set("profiles", {"default": {"links": []}})
    cfg.save()

    source = tmp_path / "bashrc"
    source.write_text("# bashrc")
    target = tmp_path / ".bashrc"

    return {"cfg_path": str(cfg_path), "source": str(source), "target": str(target), "tmp": tmp_path}


def test_symlink_add_creates_link_and_records(setup):
    args = _Args(
        config=setup["cfg_path"],
        source=setup["source"],
        target=setup["target"],
        profile=None,
        no_backup=False,
    )
    rc = cmd_symlink_add(args)
    assert rc == 0
    assert Path(setup["target"]).is_symlink()
    assert Path(setup["target"]).resolve() == Path(setup["source"]).resolve()

    cfg = Config(setup["cfg_path"])
    cfg.load()
    links = cfg.get("profiles", {}).get("default", {}).get("links", [])
    assert any(lnk["target"] == setup["target"] for lnk in links)


def test_symlink_add_idempotent_recording(setup):
    args = _Args(
        config=setup["cfg_path"],
        source=setup["source"],
        target=setup["target"],
        profile=None,
        no_backup=False,
    )
    cmd_symlink_add(args)
    rc = cmd_symlink_add(args)  # second call
    assert rc == 0

    cfg = Config(setup["cfg_path"])
    cfg.load()
    links = cfg.get("profiles", {}).get("default", {}).get("links", [])
    matching = [lnk for lnk in links if lnk["target"] == setup["target"]]
    assert len(matching) == 1  # not duplicated


def test_symlink_add_missing_source_returns_error(setup, tmp_path):
    args = _Args(
        config=setup["cfg_path"],
        source=str(tmp_path / "nonexistent"),
        target=setup["target"],
        profile=None,
        no_backup=False,
    )
    rc = cmd_symlink_add(args)
    assert rc == 1


def test_symlink_remove_unlinks_and_unrecords(setup):
    add_args = _Args(
        config=setup["cfg_path"],
        source=setup["source"],
        target=setup["target"],
        profile=None,
        no_backup=False,
    )
    cmd_symlink_add(add_args)

    rm_args = _Args(
        config=setup["cfg_path"],
        target=setup["target"],
        profile="default",
    )
    rc = cmd_symlink_remove(rm_args)
    assert rc == 0
    assert not Path(setup["target"]).exists()

    cfg = Config(setup["cfg_path"])
    cfg.load()
    links = cfg.get("profiles", {}).get("default", {}).get("links", [])
    assert not any(lnk["target"] == setup["target"] for lnk in links)


def test_symlink_remove_nonexistent_returns_error(setup, tmp_path):
    args = _Args(
        config=setup["cfg_path"],
        target=str(tmp_path / "ghost"),
        profile=None,
    )
    rc = cmd_symlink_remove(args)
    assert rc == 1
