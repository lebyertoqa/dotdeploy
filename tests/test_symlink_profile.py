"""Tests for symlink and profile deployment features."""

import pytest
from pathlib import Path

from dotdeploy.symlink import create_symlink, remove_symlink, SymlinkError
from dotdeploy.profile import deploy_profile, undeploy_profile, ProfileDeployError
from dotdeploy.config import Config


# ---------------------------------------------------------------------------
# Symlink tests
# ---------------------------------------------------------------------------

def test_create_symlink_basic(tmp_path):
    src = tmp_path / "bashrc"
    src.write_text("# bashrc")
    tgt = tmp_path / "home" / ".bashrc"

    create_symlink(str(src), str(tgt))

    assert tgt.is_symlink()
    assert tgt.resolve() == src.resolve()


def test_create_symlink_idempotent(tmp_path):
    src = tmp_path / "vimrc"
    src.write_text("set number")
    tgt = tmp_path / ".vimrc"

    create_symlink(str(src), str(tgt))
    create_symlink(str(src), str(tgt))  # Should not raise

    assert tgt.is_symlink()


def test_create_symlink_missing_source_raises(tmp_path):
    with pytest.raises(SymlinkError, match="Source does not exist"):
        create_symlink(str(tmp_path / "missing"), str(tmp_path / "target"))


def test_create_symlink_existing_file_backed_up(tmp_path):
    src = tmp_path / "src"
    src.write_text("new")
    tgt = tmp_path / "tgt"
    tgt.write_text("old")
    backup_dir = tmp_path / "backups"

    create_symlink(str(src), str(tgt), backup_dir=str(backup_dir))

    assert tgt.is_symlink()
    assert (backup_dir / "tgt").read_text() == "old"


def test_create_symlink_existing_file_no_backup_raises(tmp_path):
    src = tmp_path / "src"
    src.write_text("new")
    tgt = tmp_path / "tgt"
    tgt.write_text("old")

    with pytest.raises(SymlinkError):
        create_symlink(str(src), str(tgt))


def test_remove_symlink(tmp_path):
    src = tmp_path / "src"
    src.write_text("data")
    tgt = tmp_path / "tgt"
    tgt.symlink_to(src)

    result = remove_symlink(str(tgt))
    assert result is True
    assert not tgt.exists()


def test_remove_symlink_nonexistent_returns_false(tmp_path):
    result = remove_symlink(str(tmp_path / "ghost"))
    assert result is False


# ---------------------------------------------------------------------------
# Profile deployment tests
# ---------------------------------------------------------------------------

@pytest.fixture
def cfg(tmp_path):
    config_file = tmp_path / "config.json"
    c = Config(str(config_file))
    c.load()
    return c


def test_deploy_profile(cfg, tmp_path):
    src = tmp_path / "bashrc"
    src.write_text("# shell")
    tgt = tmp_path / "home" / ".bashrc"

    cfg.add_profile("work", links={str(src): str(tgt)})
    deployed = deploy_profile(cfg, "work", backup_dir=str(tmp_path / "bak"))

    assert str(tgt) in deployed
    assert tgt.is_symlink()
    assert cfg.get("active_profile") == "work"


def test_deploy_unknown_profile_raises(cfg):
    with pytest.raises(ProfileDeployError, match="Unknown profile"):
        deploy_profile(cfg, "nonexistent")


def test_undeploy_profile(cfg, tmp_path):
    src = tmp_path / "gitconfig"
    src.write_text("[user]")
    tgt = tmp_path / ".gitconfig"

    cfg.add_profile("home", links={str(src): str(tgt)})
    deploy_profile(cfg, "home", backup_dir=str(tmp_path / "bak"))
    removed = undeploy_profile(cfg, "home")

    assert str(tgt) in removed
    assert not tgt.exists()
    assert cfg.get("active_profile") is None
