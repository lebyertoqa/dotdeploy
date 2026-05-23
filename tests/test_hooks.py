"""Tests for dotdeploy.hooks."""

import stat
import subprocess
from pathlib import Path

import pytest

from dotdeploy.hooks import (
    HOOK_EVENTS,
    HookError,
    hook_path,
    list_hooks,
    register_hook,
    remove_hook,
    run_hook,
)


@pytest.fixture()
def cfg_dir(tmp_path):
    return tmp_path


def test_hook_path_valid_event(cfg_dir):
    path = hook_path(cfg_dir, "work", "pre_deploy")
    assert path == cfg_dir / "hooks" / "work" / "pre_deploy"


def test_hook_path_invalid_event_raises(cfg_dir):
    with pytest.raises(HookError, match="Unknown hook event"):
        hook_path(cfg_dir, "work", "on_fire")


def test_list_hooks_empty_when_no_dir(cfg_dir):
    assert list_hooks(cfg_dir, "work") == []


def test_register_hook_creates_file(cfg_dir):
    path = register_hook(cfg_dir, "work", "post_deploy", "#!/bin/sh\necho done\n")
    assert path.exists()
    assert path.read_text() == "#!/bin/sh\necho done\n"


def test_register_hook_is_executable(cfg_dir):
    path = register_hook(cfg_dir, "work", "post_deploy", "#!/bin/sh\n")
    mode = path.stat().st_mode
    assert mode & stat.S_IXUSR


def test_list_hooks_returns_registered(cfg_dir):
    register_hook(cfg_dir, "work", "pre_deploy", "#!/bin/sh\n")
    register_hook(cfg_dir, "work", "post_deploy", "#!/bin/sh\n")
    hooks = list_hooks(cfg_dir, "work")
    assert "pre_deploy" in hooks
    assert "post_deploy" in hooks


def test_list_hooks_ignores_unknown_files(cfg_dir):
    hooks_dir = cfg_dir / "hooks" / "work"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "random_file").write_text("x")
    assert list_hooks(cfg_dir, "work") == []


def test_remove_hook_returns_true_when_existed(cfg_dir):
    register_hook(cfg_dir, "work", "pre_deploy", "#!/bin/sh\n")
    assert remove_hook(cfg_dir, "work", "pre_deploy") is True
    assert not hook_path(cfg_dir, "work", "pre_deploy").exists()


def test_remove_hook_returns_false_when_missing(cfg_dir):
    assert remove_hook(cfg_dir, "work", "pre_deploy") is False


def test_run_hook_returns_none_when_no_hook(cfg_dir):
    result = run_hook(cfg_dir, "work", "pre_deploy")
    assert result is None


def test_run_hook_executes_script(cfg_dir):
    register_hook(cfg_dir, "work", "post_deploy", "#!/bin/sh\necho hello\n")
    result = run_hook(cfg_dir, "work", "post_deploy")
    assert result is not None
    assert result.returncode == 0
    assert "hello" in result.stdout


def test_run_hook_raises_on_failure(cfg_dir):
    register_hook(cfg_dir, "work", "pre_undeploy", "#!/bin/sh\nexit 1\n")
    with pytest.raises(HookError, match="failed"):
        run_hook(cfg_dir, "work", "pre_undeploy")
