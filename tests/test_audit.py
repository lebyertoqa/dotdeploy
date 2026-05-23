"""Tests for dotdeploy.audit module."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from dotdeploy.audit import (
    AUDIT_FILENAME,
    AuditError,
    clear_events,
    read_events,
    record_event,
)


@pytest.fixture()
def cfg_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_record_event_creates_file(cfg_dir: Path) -> None:
    record_event(cfg_dir, "deploy", profile="default")
    assert (cfg_dir / AUDIT_FILENAME).exists()


def test_record_event_returns_entry(cfg_dir: Path) -> None:
    before = time.time()
    entry = record_event(cfg_dir, "deploy", profile="work", details={"files": 3})
    after = time.time()
    assert entry["action"] == "deploy"
    assert entry["profile"] == "work"
    assert entry["details"] == {"files": 3}
    assert before <= entry["timestamp"] <= after


def test_record_multiple_events(cfg_dir: Path) -> None:
    record_event(cfg_dir, "deploy", profile="a")
    record_event(cfg_dir, "undeploy", profile="a")
    record_event(cfg_dir, "symlink_add", profile="b")
    events = read_events(cfg_dir)
    assert len(events) == 3
    assert events[0]["action"] == "deploy"
    assert events[2]["action"] == "symlink_add"


def test_read_events_empty_when_no_file(cfg_dir: Path) -> None:
    assert read_events(cfg_dir) == []


def test_read_events_parses_correctly(cfg_dir: Path) -> None:
    log_path = cfg_dir / AUDIT_FILENAME
    log_path.write_text(
        json.dumps({"timestamp": 1000.0, "action": "deploy", "profile": "x"}) + "\n"
        + json.dumps({"timestamp": 2000.0, "action": "push"}) + "\n",
        encoding="utf-8",
    )
    events = read_events(cfg_dir)
    assert len(events) == 2
    assert events[1]["action"] == "push"


def test_read_events_raises_on_corrupt_json(cfg_dir: Path) -> None:
    (cfg_dir / AUDIT_FILENAME).write_text("not-json\n", encoding="utf-8")
    with pytest.raises(AuditError):
        read_events(cfg_dir)


def test_clear_events_removes_file(cfg_dir: Path) -> None:
    record_event(cfg_dir, "deploy", profile="default")
    removed = clear_events(cfg_dir)
    assert removed == 1
    assert not (cfg_dir / AUDIT_FILENAME).exists()


def test_clear_events_on_empty_dir(cfg_dir: Path) -> None:
    removed = clear_events(cfg_dir)
    assert removed == 0
