"""Tests for dotdeploy.validate."""

import os
import pytest

from dotdeploy.config import Config
from dotdeploy.validate import ValidateError, ValidationResult, validate_profile


@pytest.fixture()
def cfg(tmp_path):
    path = tmp_path / "dotdeploy.json"
    c = Config(str(path))
    c.load()
    return c


@pytest.fixture()
def source_file(tmp_path):
    src = tmp_path / "bashrc"
    src.write_text("# bashrc")
    return src


def test_validate_unknown_profile_raises(cfg):
    with pytest.raises(ValidateError, match="not found"):
        validate_profile(cfg, "ghost")


def test_validate_empty_profile_is_ok(cfg):
    cfg.add_profile("base")
    result = validate_profile(cfg, "base")
    assert result.ok
    assert result.profile == "base"


def test_validate_valid_symlink(cfg, source_file, tmp_path):
    link = str(tmp_path / "link_bashrc")
    cfg.add_profile("base")
    cfg.get("profiles")["base"]["symlinks"] = {link: str(source_file)}
    cfg.save()

    result = validate_profile(cfg, "base")
    assert result.ok, str(result)


def test_validate_missing_source_is_issue(cfg, tmp_path):
    link = str(tmp_path / "link_bashrc")
    missing = str(tmp_path / "no_such_file")
    cfg.add_profile("base")
    cfg.get("profiles")["base"]["symlinks"] = {link: missing}
    cfg.save()

    result = validate_profile(cfg, "base")
    assert not result.ok
    assert len(result.issues) == 1
    assert "does not exist" in result.issues[0].reason


def test_validate_existing_file_no_backup_is_issue(cfg, source_file, tmp_path):
    link = tmp_path / "existing_link"
    link.write_text("old content")

    cfg.set("backup", False)
    cfg.add_profile("base")
    cfg.get("profiles")["base"]["symlinks"] = {str(link): str(source_file)}
    cfg.save()

    result = validate_profile(cfg, "base")
    assert not result.ok
    assert any("backup is disabled" in i.reason for i in result.issues)


def test_validate_existing_file_with_backup_is_ok(cfg, source_file, tmp_path):
    link = tmp_path / "existing_link"
    link.write_text("old content")

    cfg.set("backup", True)
    cfg.add_profile("base")
    cfg.get("profiles")["base"]["symlinks"] = {str(link): str(source_file)}
    cfg.save()

    result = validate_profile(cfg, "base")
    assert result.ok, str(result)


def test_validation_result_str_ok(cfg):
    cfg.add_profile("base")
    result = validate_profile(cfg, "base")
    assert "valid" in str(result)


def test_validation_result_str_issues(cfg, tmp_path):
    missing = str(tmp_path / "ghost")
    link = str(tmp_path / "lnk")
    cfg.add_profile("base")
    cfg.get("profiles")["base"]["symlinks"] = {link: missing}
    cfg.save()
    result = validate_profile(cfg, "base")
    assert "issue" in str(result)
