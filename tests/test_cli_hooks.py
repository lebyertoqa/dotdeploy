"""Tests for dotdeploy.cli_hooks."""

import argparse
from pathlib import Path

import pytest

from dotdeploy.cli_hooks import cmd_hook_list, cmd_hook_add, cmd_hook_remove
from dotdeploy.config import Config
from dotdeploy.hooks import register_hook


class _Args:
    def __init__(self, config, **kwargs):
        self.config = config
        for k, v in kwargs.items():
            setattr(self, k, v)


@pytest.fixture()
def config(tmp_path):
    cfg_path = tmp_path / "dotdeploy.json"
    cfg = Config(str(cfg_path))
    cfg.load()
    cfg.add_profile("personal")
    cfg.save()
    return cfg_path


def test_list_empty(config, capsys):
    args = _Args(str(config), profile="personal")
    cmd_hook_list(args)
    out = capsys.readouterr().out
    assert "No hooks" in out


def test_list_shows_hook(config, tmp_path, capsys):
    cfg_dir = config.parent
    register_hook(cfg_dir, "personal", "post_deploy", "#!/bin/sh\n")
    args = _Args(str(config), profile="personal")
    cmd_hook_list(args)
    out = capsys.readouterr().out
    assert "post_deploy" in out


def test_list_unknown_profile_exits(config, capsys):
    args = _Args(str(config), profile="ghost")
    with pytest.raises(SystemExit):
        cmd_hook_list(args)


def test_add_registers_hook(config, tmp_path, capsys):
    script = tmp_path / "myhook.sh"
    script.write_text("#!/bin/sh\necho hi\n")
    args = _Args(str(config), profile="personal", event="pre_deploy", script=str(script))
    cmd_hook_add(args)
    out = capsys.readouterr().out
    assert "registered" in out
    hook = config.parent / "hooks" / "personal" / "pre_deploy"
    assert hook.exists()


def test_add_missing_script_exits(config, tmp_path, capsys):
    args = _Args(
        str(config), profile="personal", event="pre_deploy",
        script=str(tmp_path / "nonexistent.sh")
    )
    with pytest.raises(SystemExit):
        cmd_hook_add(args)


def test_remove_existing_hook(config, capsys):
    cfg_dir = config.parent
    register_hook(cfg_dir, "personal", "post_undeploy", "#!/bin/sh\n")
    args = _Args(str(config), profile="personal", event="post_undeploy")
    cmd_hook_remove(args)
    out = capsys.readouterr().out
    assert "removed" in out


def test_remove_missing_hook(config, capsys):
    args = _Args(str(config), profile="personal", event="post_undeploy")
    cmd_hook_remove(args)
    out = capsys.readouterr().out
    assert "No hook" in out
