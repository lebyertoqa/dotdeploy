"""Tests for dotdeploy.status module."""

import os
import pytest

from dotdeploy.config import Config
from dotdeploy.status import ProfileStatus, StatusError, profile_status, all_profiles_status


@pytest.fixture
def cfg(tmp_path):
    c = Config(str(tmp_path / "dotdeploy.json"))
    c.load()
    return c


@pytest.fixture
def source_file(tmp_path):
    src = tmp_path / "bashrc"
    src.write_text("# bashrc")
    return str(src)


def test_status_unknown_profile_raises(cfg):
    with pytest.raises(StatusError, match="Unknown profile"):
        profile_status(cfg, "ghost")


def test_status_empty_profile_is_clean(cfg):
    cfg.add_profile("base")
    status = profile_status(cfg, "base")
    assert status.is_clean
    assert status.total_links == 0
    assert status.ok_links == 0
    assert status.missing_links == []
    assert status.broken_links == []


def test_status_not_pinned_by_default(cfg):
    cfg.add_profile("base")
    status = profile_status(cfg, "base")
    assert not status.pinned


def test_status_pinned_flag(cfg):
    cfg.add_profile("base")
    cfg.set("pinned_profile", "base")
    cfg.save()
    status = profile_status(cfg, "base")
    assert status.pinned


def test_status_detects_missing_link(cfg, source_file, tmp_path):
    cfg.add_profile("base")
    target = str(tmp_path / "link_target")
    cfg.add_symlink("base", source_file, target)
    # symlink not actually created on disk
    status = profile_status(cfg, "base")
    assert not status.is_clean
    assert target in status.missing_links


def test_status_ok_when_symlink_exists(cfg, source_file, tmp_path):
    cfg.add_profile("base")
    target = str(tmp_path / "link_target")
    os.symlink(source_file, target)
    cfg.add_symlink("base", source_file, target)
    status = profile_status(cfg, "base")
    assert status.is_clean
    assert status.ok_links == 1
    assert status.total_links == 1


def test_summary_line_clean(cfg):
    cfg.add_profile("work")
    status = profile_status(cfg, "work")
    line = status.summary_line()
    assert "work" in line
    assert "clean" in line
    assert "[pinned]" not in line


def test_summary_line_pinned(cfg):
    cfg.add_profile("work")
    cfg.set("pinned_profile", "work")
    cfg.save()
    status = profile_status(cfg, "work")
    assert "[pinned]" in status.summary_line()


def test_all_profiles_status_empty(cfg):
    result = all_profiles_status(cfg)
    assert result == []


def test_all_profiles_status_multiple(cfg):
    cfg.add_profile("base")
    cfg.add_profile("work")
    result = all_profiles_status(cfg)
    assert len(result) == 2
    profiles = {s.profile for s in result}
    assert profiles == {"base", "work"}
