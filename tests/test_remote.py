"""Tests for dotdeploy.remote backup module."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from dotdeploy.remote import (
    RemoteBackupError,
    init_repo,
    pull_backup,
    push_backup,
    set_remote,
)


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """Return a temporary path intended as a git repo root."""
    return tmp_path / "backup"


def _completed(returncode: int = 0, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


class TestInitRepo:
    def test_creates_directory_and_runs_git_init(self, repo: Path) -> None:
        with patch("dotdeploy.remote._run", return_value=_completed()) as mock_run:
            init_repo(repo)
        assert repo.exists()
        mock_run.assert_called_once_with(["git", "init"], cwd=repo)

    def test_skips_init_when_git_dir_exists(self, repo: Path) -> None:
        repo.mkdir(parents=True)
        (repo / ".git").mkdir()
        with patch("dotdeploy.remote._run") as mock_run:
            init_repo(repo)
        mock_run.assert_not_called()

    def test_raises_on_git_init_failure(self, repo: Path) -> None:
        with patch("dotdeploy.remote._run", return_value=_completed(returncode=1, stderr="fatal error")):
            with pytest.raises(RemoteBackupError, match="git init failed"):
                init_repo(repo)


class TestSetRemote:
    def test_adds_remote_when_none_exists(self, repo: Path) -> None:
        responses = [_completed(returncode=1), _completed(returncode=0)]
        with patch("dotdeploy.remote._run", side_effect=responses) as mock_run:
            set_remote(repo, "https://example.com/dots.git")
        mock_run.assert_any_call(["git", "remote", "add", "origin", "https://example.com/dots.git"], cwd=repo)

    def test_updates_remote_when_already_exists(self, repo: Path) -> None:
        responses = [_completed(returncode=0, stdout="https://old.com"), _completed(returncode=0)]
        with patch("dotdeploy.remote._run", side_effect=responses) as mock_run:
            set_remote(repo, "https://new.com/dots.git")
        mock_run.assert_any_call(["git", "remote", "set-url", "origin", "https://new.com/dots.git"], cwd=repo)

    def test_raises_when_add_fails(self, repo: Path) -> None:
        with patch("dotdeploy.remote._run", side_effect=[_completed(returncode=1), _completed(returncode=1, stderr="err")]):
            with pytest.raises(RemoteBackupError, match="git remote add failed"):
                set_remote(repo, "https://example.com/dots.git")


class TestPushBackup:
    def test_commits_and_pushes_when_changes_exist(self, repo: Path) -> None:
        responses = [
            _completed(),                          # git add
            _completed(stdout="M .bashrc\n"),      # git status
            _completed(),                          # git commit
            _completed(),                          # git push
        ]
        with patch("dotdeploy.remote._run", side_effect=responses):
            push_backup(repo)

    def test_skips_commit_when_nothing_to_commit(self, repo: Path) -> None:
        responses = [_completed(), _completed(stdout="")]
        with patch("dotdeploy.remote._run", side_effect=responses) as mock_run:
            push_backup(repo)
        assert mock_run.call_count == 2  # add + status only

    def test_raises_on_push_failure(self, repo: Path) -> None:
        responses = [
            _completed(),
            _completed(stdout="M file"),
            _completed(),
            _completed(returncode=1, stderr="push rejected"),
        ]
        with patch("dotdeploy.remote._run", side_effect=responses):
            with pytest.raises(RemoteBackupError, match="git push failed"):
                push_backup(repo)


class TestPullBackup:
    def test_raises_when_no_git_repo(self, repo: Path) -> None:
        repo.mkdir()
        with pytest.raises(RemoteBackupError, match="No git repository"):
            pull_backup(repo)

    def test_pulls_successfully(self, repo: Path) -> None:
        repo.mkdir()
        (repo / ".git").mkdir()
        with patch("dotdeploy.remote._run", return_value=_completed()) as mock_run:
            pull_backup(repo)
        mock_run.assert_called_once_with(["git", "pull", "origin", "main"], cwd=repo)
