"""Integration-level tests for the main CLI entry point."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from dotdeploy.cli import main, build_parser


@pytest.fixture()
def cfg_path(tmp_path):
    p = tmp_path / "config.json"
    p.write_text(json.dumps({"profiles": {}, "active_profile": None}))
    return str(p)


def test_build_parser_returns_parser():
    parser = build_parser()
    assert parser.prog == "dotdeploy"


def test_main_no_args_exits_nonzero():
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code != 0


def test_main_list_empty(cfg_path, capsys):
    rc = main(["--config", cfg_path, "list"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "No profiles" in out


def test_main_add_profile(cfg_path, capsys):
    rc = main(["--config", cfg_path, "add", "work"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "work" in out

    data = json.loads(Path(cfg_path).read_text())
    assert "work" in data["profiles"]


def test_main_add_duplicate_returns_error(cfg_path, capsys):
    main(["--config", cfg_path, "add", "home"])
    rc = main(["--config", cfg_path, "add", "home"])
    assert rc == 1
    out = capsys.readouterr().out
    assert "error" in out


def test_main_deploy_no_active_returns_error(cfg_path, capsys):
    rc = main(["--config", cfg_path, "deploy"])
    assert rc == 1


def test_main_func_exception_returns_1(cfg_path, capsys):
    """Any unexpected exception from a sub-command handler returns exit code 1."""
    with patch("dotdeploy.cli_profile.cmd_profile_list", side_effect=RuntimeError("boom")):
        rc = main(["--config", cfg_path, "list"])
    assert rc == 1
    err = capsys.readouterr().err
    assert "boom" in err
