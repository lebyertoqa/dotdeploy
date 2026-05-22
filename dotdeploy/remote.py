"""Remote backup support for dotdeploy."""

import os
import subprocess
from pathlib import Path


class RemoteBackupError(Exception):
    """Raised when a remote backup operation fails."""


def _run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def init_repo(repo_path: Path) -> None:
    """Initialize a git repository at the given path if not already initialised."""
    repo_path.mkdir(parents=True, exist_ok=True)
    if not (repo_path / ".git").exists():
        result = _run(["git", "init"], cwd=repo_path)
        if result.returncode != 0:
            raise RemoteBackupError(f"git init failed: {result.stderr.strip()}")


def set_remote(repo_path: Path, remote_url: str, name: str = "origin") -> None:
    """Add or update the remote URL for the backup repository."""
    result = _run(["git", "remote", "get-url", name], cwd=repo_path)
    if result.returncode == 0:
        _run(["git", "remote", "set-url", name, remote_url], cwd=repo_path)
    else:
        result = _run(["git", "remote", "add", name, remote_url], cwd=repo_path)
        if result.returncode != 0:
            raise RemoteBackupError(f"git remote add failed: {result.stderr.strip()}")


def push_backup(repo_path: Path, message: str = "dotdeploy backup", remote: str = "origin", branch: str = "main") -> None:
    """Stage all changes, commit, and push to the remote."""
    _run(["git", "add", "-A"], cwd=repo_path)

    status = _run(["git", "status", "--porcelain"], cwd=repo_path)
    if not status.stdout.strip():
        return  # nothing to commit

    commit = _run(["git", "commit", "-m", message], cwd=repo_path)
    if commit.returncode != 0:
        raise RemoteBackupError(f"git commit failed: {commit.stderr.strip()}")

    push = _run(["git", "push", "-u", remote, branch], cwd=repo_path)
    if push.returncode != 0:
        raise RemoteBackupError(f"git push failed: {push.stderr.strip()}")


def pull_backup(repo_path: Path, remote: str = "origin", branch: str = "main") -> None:
    """Pull the latest changes from the remote."""
    if not (repo_path / ".git").exists():
        raise RemoteBackupError(f"No git repository found at {repo_path}")

    result = _run(["git", "pull", remote, branch], cwd=repo_path)
    if result.returncode != 0:
        raise RemoteBackupError(f"git pull failed: {result.stderr.strip()}")
