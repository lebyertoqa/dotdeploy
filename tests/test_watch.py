"""Tests for dotdeploy.watch and dotdeploy.cli_watch."""

import os
import pytest

from dotdeploy.config import Config
from dotdeploy.watch import poll_once, watch, WatchError, WatchEvent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture()
def cfg(tmp_path):
    path = tmp_path / "config.json"
    c = Config(str(path))
    c.load()
    return c


@pytest.fixture()
def source_file(tmp_path):
    src = tmp_path / "vimrc"
    src.write_text("set number\n")
    return src


# ---------------------------------------------------------------------------
# poll_once
# ---------------------------------------------------------------------------

def test_poll_once_no_profiles_returns_empty(cfg):
    events = poll_once(cfg)
    assert events == []


def test_poll_once_unknown_profile_raises(cfg):
    with pytest.raises(WatchError, match="Unknown profile"):
        poll_once(cfg, profiles=["ghost"])


def test_poll_once_clean_profile_no_event(cfg, tmp_path, source_file):
    cfg.add_profile("base")
    link = tmp_path / ".vimrc"
    os.symlink(str(source_file), str(link))
    cfg.add_symlink("base", str(source_file), str(link))
    cfg.save()

    events = poll_once(cfg, profiles=["base"])
    assert events == []


def test_poll_once_broken_symlink_returns_event(cfg, tmp_path, source_file):
    cfg.add_profile("base")
    link = tmp_path / ".vimrc"
    # Record the mapping but do NOT create the symlink → drift
    cfg.add_symlink("base", str(source_file), str(link))
    cfg.save()

    events = poll_once(cfg, profiles=["base"])
    assert len(events) == 1
    assert events[0].profile == "base"
    assert str(link) in events[0].changed_targets


def test_watch_event_str_contains_profile(cfg, tmp_path, source_file):
    event = WatchEvent(profile="base", changed_targets=["/home/user/.vimrc"])
    text = str(event)
    assert "base" in text
    assert ".vimrc" in text


# ---------------------------------------------------------------------------
# watch generator
# ---------------------------------------------------------------------------

def test_watch_max_polls_stops(cfg):
    collected = list(watch(cfg, profiles=None, interval=0, max_polls=3))
    # No profiles → no events, but generator must terminate after 3 polls
    assert collected == []


def test_watch_yields_events(cfg, tmp_path, source_file):
    cfg.add_profile("base")
    link = tmp_path / ".vimrc"
    cfg.add_symlink("base", str(source_file), str(link))
    cfg.save()

    events = list(watch(cfg, profiles=["base"], interval=0, max_polls=2))
    # Both polls should detect drift
    assert len(events) == 2
    assert all(e.profile == "base" for e in events)
