"""CLI commands for remote backup operations."""

import argparse
from pathlib import Path

from dotdeploy.config import Config
from dotdeploy.remote import RemoteBackupError, init_repo, pull_backup, push_backup, set_remote

_DEFAULT_BACKUP_REPO = str(Path.home() / ".dotdeploy-backup")


def _get_repo_path(config: Config) -> Path:
    """Return the configured backup repository path."""
    return Path(config.get("backup_repo", _DEFAULT_BACKUP_REPO))


def cmd_remote_init(args: argparse.Namespace, config: Config) -> int:
    """Initialise a local git repo and optionally set a remote URL."""
    repo_path = _get_repo_path(config)
    try:
        init_repo(repo_path)
        print(f"Initialised backup repository at {repo_path}")
        if args.remote_url:
            set_remote(repo_path, args.remote_url)
            config.set("backup_remote", args.remote_url)
            config.save()
            print(f"Remote set to {args.remote_url}")
    except RemoteBackupError as exc:
        print(f"Error: {exc}")
        return 1
    return 0


def cmd_remote_push(args: argparse.Namespace, config: Config) -> int:
    """Push local dotfiles backup to the remote."""
    repo_path = _get_repo_path(config)
    message = getattr(args, "message", "dotdeploy backup")
    try:
        push_backup(repo_path, message=message)
        print("Backup pushed successfully.")
    except RemoteBackupError as exc:
        print(f"Error: {exc}")
        return 1
    return 0


def cmd_remote_pull(args: argparse.Namespace, config: Config) -> int:
    """Pull the latest backup from the remote."""
    repo_path = _get_repo_path(config)
    try:
        pull_backup(repo_path)
        print("Backup pulled successfully.")
    except RemoteBackupError as exc:
        print(f"Error: {exc}")
        return 1
    return 0


def register_remote_subcommands(subparsers: argparse._SubParsersAction, config: Config) -> None:  # noqa: SLF001
    """Register remote sub-commands onto the main argument parser."""
    remote_parser = subparsers.add_parser("remote", help="Remote backup operations")
    remote_sub = remote_parser.add_subparsers(dest="remote_cmd", required=True)

    p_init = remote_sub.add_parser("init", help="Initialise backup repository")
    p_init.add_argument("--url", dest="remote_url", default=None, help="Remote git URL")
    p_init.set_defaults(func=lambda a: cmd_remote_init(a, config))

    p_push = remote_sub.add_parser("push", help="Push backup to remote")
    p_push.add_argument("-m", "--message", default="dotdeploy backup", help="Commit message")
    p_push.set_defaults(func=lambda a: cmd_remote_push(a, config))

    p_pull = remote_sub.add_parser("pull", help="Pull backup from remote")
    p_pull.set_defaults(func=lambda a: cmd_remote_pull(a, config))
