"""Tests for dotdeploy.cli_template."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from dotdeploy.config import Config
from dotdeploy.cli_template import cmd_template_render, register_template_subcommands


class _Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture()
def config(tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg = Config(cfg_file)
    cfg.load()
    cfg.data["profiles"]["work"] = {
        "symlinks": {},
        "variables": {"EDITOR": "vim"},
    }
    cfg.save()
    return cfg_file


def test_render_writes_output(tmp_path, config):
    src = tmp_path / "tmux.conf.ddtpl"
    src.write_text("set -g default-command {{ SHELL }}", encoding="utf-8")
    dest = tmp_path / "out" / ".tmux.conf"

    args = _Args(
        config=config,
        source=str(src),
        dest=str(dest),
        var=["SHELL=/bin/zsh"],
        profile="",
    )
    cmd_template_render(args)
    assert dest.read_text() == "set -g default-command /bin/zsh"


def test_render_with_profile_variables(tmp_path, config):
    src = tmp_path / "vimrc.ddtpl"
    src.write_text("set editor={{ EDITOR }}", encoding="utf-8")
    dest = tmp_path / ".vimrc"

    args = _Args(
        config=config,
        source=str(src),
        dest=str(dest),
        var=None,
        profile="work",
    )
    cmd_template_render(args)
    assert dest.read_text() == "set editor=vim"


def test_render_unknown_profile_exits(tmp_path, config):
    src = tmp_path / "t.ddtpl"
    src.write_text("x", encoding="utf-8")
    dest = tmp_path / "out.txt"

    args = _Args(
        config=config,
        source=str(src),
        dest=str(dest),
        var=None,
        profile="ghost",
    )
    with pytest.raises(SystemExit):
        cmd_template_render(args)


def test_render_bad_var_format_exits(tmp_path, config):
    src = tmp_path / "t.ddtpl"
    src.write_text("x", encoding="utf-8")
    dest = tmp_path / "out.txt"

    args = _Args(
        config=config,
        source=str(src),
        dest=str(dest),
        var=["NOEQUALS"],
        profile="",
    )
    with pytest.raises(SystemExit):
        cmd_template_render(args)


def test_register_adds_subparser():
    import argparse
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_template_subcommands(sub)
    args = parser.parse_args(["template-render", "src", "dst"])
    assert args.source == "src"
    assert args.dest == "dst"
