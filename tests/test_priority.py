"""Tests for dotdeploy.priority."""

import pytest

from dotdeploy.config import Config
from dotdeploy.priority import (
    PriorityError,
    clear_priority,
    get_priority,
    ranked_profiles,
    set_priority,
)


@pytest.fixture()
def cfg(tmp_path):
    path = tmp_path / "config.json"
    c = Config(str(path))
    c.load()
    c.add_profile("base")
    c.add_profile("work")
    c.add_profile("personal")
    return c


def test_get_priority_default(cfg):
    assert get_priority(cfg, "base") == 0


def test_set_priority_persists(cfg):
    set_priority(cfg, "work", 10)
    assert get_priority(cfg, "work") == 10


def test_set_priority_reloads(cfg, tmp_path):
    set_priority(cfg, "work", 5)
    # Reload from disk to confirm persistence
    cfg2 = Config(cfg.path)
    cfg2.load()
    assert get_priority(cfg2, "work") == 5


def test_set_priority_unknown_profile_raises(cfg):
    with pytest.raises(PriorityError, match="Unknown profile"):
        set_priority(cfg, "ghost", 99)


def test_get_priority_unknown_profile_raises(cfg):
    with pytest.raises(PriorityError, match="Unknown profile"):
        get_priority(cfg, "ghost")


def test_clear_priority_reverts_to_default(cfg):
    set_priority(cfg, "base", 7)
    clear_priority(cfg, "base")
    assert get_priority(cfg, "base") == 0


def test_clear_priority_unknown_profile_raises(cfg):
    with pytest.raises(PriorityError, match="Unknown profile"):
        clear_priority(cfg, "nobody")


def test_clear_priority_when_not_set_is_noop(cfg):
    # Should not raise even if no explicit priority was set
    clear_priority(cfg, "personal")
    assert get_priority(cfg, "personal") == 0


def test_ranked_profiles_default_order(cfg):
    result = ranked_profiles(cfg)
    names = [r[0] for r in result]
    assert set(names) == {"base", "work", "personal"}
    priorities = [r[1] for r in result]
    assert priorities == sorted(priorities, reverse=True)


def test_ranked_profiles_respects_priority(cfg):
    set_priority(cfg, "personal", 20)
    set_priority(cfg, "work", 10)
    result = ranked_profiles(cfg)
    assert result[0] == ("personal", 20)
    assert result[1] == ("work", 10)
    assert result[2][0] == "base"


def test_ranked_profiles_empty(tmp_path):
    path = tmp_path / "empty.json"
    c = Config(str(path))
    c.load()
    assert ranked_profiles(c) == []
