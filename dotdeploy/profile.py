"""Profile deploy/undeploy with hook execution."""

from pathlib import Path
from typing import Optional

from dotdeploy.config import Config
from dotdeploy.hooks import HookError, run_hook
from dotdeploy.symlink import SymlinkError, create_symlink, remove_symlink


class ProfileDeployError(Exception):
    """Raised when deploying or undeploying a profile fails."""


def deploy_profile(
    config: Config,
    profile: str,
    backup: bool = True,
    config_dir: Optional[Path] = None,
) -> None:
    """Create symlinks for every mapping in *profile*.

    Runs pre_deploy hook before and post_deploy hook after linking.
    Raises ProfileDeployError on unknown profile or symlink failure.
    """
    profiles = config.get("profiles", {})
    if profile not in profiles:
        raise ProfileDeployError(f"Unknown profile '{profile}'")

    cdir = config_dir or Path(config._path).parent

    try:
        run_hook(cdir, profile, "pre_deploy")
    except HookError as exc:
        raise ProfileDeployError(str(exc)) from exc

    mappings = profiles[profile].get("mappings", {})
    for src, dst in mappings.items():
        try:
            create_symlink(src, dst, backup=backup)
        except SymlinkError as exc:
            raise ProfileDeployError(str(exc)) from exc

    try:
        run_hook(cdir, profile, "post_deploy")
    except HookError as exc:
        raise ProfileDeployError(str(exc)) from exc


def undeploy_profile(
    config: Config,
    profile: str,
    config_dir: Optional[Path] = None,
) -> None:
    """Remove symlinks for every mapping in *profile*.

    Runs pre_undeploy hook before and post_undeploy hook after removal.
    Raises ProfileDeployError on unknown profile or symlink failure.
    """
    profiles = config.get("profiles", {})
    if profile not in profiles:
        raise ProfileDeployError(f"Unknown profile '{profile}'")

    cdir = config_dir or Path(config._path).parent

    try:
        run_hook(cdir, profile, "pre_undeploy")
    except HookError as exc:
        raise ProfileDeployError(str(exc)) from exc

    mappings = profiles[profile].get("mappings", {})
    for src, dst in mappings.items():
        try:
            remove_symlink(dst)
        except SymlinkError as exc:
            raise ProfileDeployError(str(exc)) from exc

    try:
        run_hook(cdir, profile, "post_undeploy")
    except HookError as exc:
        raise ProfileDeployError(str(exc)) from exc
