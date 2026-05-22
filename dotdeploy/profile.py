"""Profile-based dotfile deployment for dotdeploy."""

from pathlib import Path
from typing import Dict, List

from dotdeploy.config import Config
from dotdeploy.symlink import create_symlink, remove_symlink, SymlinkError


class ProfileDeployError(Exception):
    """Raised when deploying or undeploying a profile fails."""
    pass


def deploy_profile(
    config: Config,
    profile_name: str,
    backup_dir: str = "~/.dotdeploy_backups",
    force: bool = False,
) -> List[str]:
    """
    Deploy all symlinks defined in the given profile.

    Args:
        config: Loaded Config instance.
        profile_name: Name of the profile to deploy.
        backup_dir: Directory to back up existing files before replacing.
        force: If True, overwrite existing symlinks/files without error.

    Returns:
        List of target paths that were successfully linked.

    Raises:
        ProfileDeployError: If the profile is unknown or a symlink fails.
    """
    if profile_name not in config.profiles:
        raise ProfileDeployError(f"Unknown profile: '{profile_name}'")

    links: Dict[str, str] = config.profiles[profile_name].get("links", {})
    deployed: List[str] = []

    for source, target in links.items():
        try:
            create_symlink(source, target, backup_dir=backup_dir, force=force)
            deployed.append(target)
        except SymlinkError as exc:
            raise ProfileDeployError(
                f"Failed to link '{source}' -> '{target}': {exc}"
            ) from exc

    config.set("active_profile", profile_name)
    config.save()
    return deployed


def undeploy_profile(config: Config, profile_name: str) -> List[str]:
    """
    Remove all symlinks defined in the given profile.

    Returns:
        List of target paths that were removed.

    Raises:
        ProfileDeployError: If the profile is unknown or removal fails.
    """
    if profile_name not in config.profiles:
        raise ProfileDeployError(f"Unknown profile: '{profile_name}'")

    links: Dict[str, str] = config.profiles[profile_name].get("links", {})
    removed: List[str] = []

    for _source, target in links.items():
        try:
            if remove_symlink(target):
                removed.append(target)
        except SymlinkError as exc:
            raise ProfileDeployError(
                f"Failed to remove symlink '{target}': {exc}"
            ) from exc

    if config.get("active_profile") == profile_name:
        config.set("active_profile", None)
        config.save()

    return removed
