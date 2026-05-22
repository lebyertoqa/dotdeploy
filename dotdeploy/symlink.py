"""Symlink management for dotdeploy."""

import os
import shutil
from pathlib import Path
from typing import Optional


class SymlinkError(Exception):
    """Raised when a symlink operation fails."""
    pass


def expand(path: str) -> Path:
    """Expand ~ and environment variables in a path."""
    return Path(os.path.expandvars(os.path.expanduser(path)))


def create_symlink(source: str, target: str, backup_dir: Optional[str] = None, force: bool = False) -> None:
    """
    Create a symlink from target -> source.

    Args:
        source: The dotfile source path (in the dotfiles repo).
        target: The destination path (e.g. ~/.bashrc).
        backup_dir: If set, back up an existing target file here before replacing.
        force: If True, overwrite existing symlinks without backing up.

    Raises:
        SymlinkError: If source does not exist or target cannot be created.
    """
    src = expand(source)
    tgt = expand(target)

    if not src.exists():
        raise SymlinkError(f"Source does not exist: {src}")

    if tgt.is_symlink():
        if tgt.resolve() == src.resolve():
            return  # Already correctly linked
        if not force:
            raise SymlinkError(
                f"Target {tgt} is already a symlink to {tgt.resolve()}. Use force=True to overwrite."
            )
        tgt.unlink()
    elif tgt.exists():
        if backup_dir:
            _backup_file(tgt, expand(backup_dir))
        elif not force:
            raise SymlinkError(
                f"Target {tgt} already exists. Provide backup_dir or use force=True."
            )
        else:
            tgt.unlink() if tgt.is_file() else shutil.rmtree(tgt)

    tgt.parent.mkdir(parents=True, exist_ok=True)
    tgt.symlink_to(src)


def remove_symlink(target: str) -> bool:
    """
    Remove a symlink at the given target path.

    Returns:
        True if the symlink was removed, False if it did not exist.

    Raises:
        SymlinkError: If target exists but is not a symlink.
    """
    tgt = expand(target)
    if not tgt.exists() and not tgt.is_symlink():
        return False
    if not tgt.is_symlink():
        raise SymlinkError(f"Target {tgt} exists but is not a symlink; refusing to remove.")
    tgt.unlink()
    return True


def _backup_file(path: Path, backup_dir: Path) -> None:
    """Copy path into backup_dir, preserving the filename."""
    backup_dir.mkdir(parents=True, exist_ok=True)
    dest = backup_dir / path.name
    shutil.copy2(path, dest)
    path.unlink()
