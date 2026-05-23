"""CLI sub-commands for profile management."""

import argparse
from typing import Optional

from dotdeploy.config import Config
from dotdeploy.profile import deploy_profile, undeploy_profile, ProfileDeployError


def cmd_profile_list(args: argparse.Namespace, config: Config) -> int:
    profiles = config.get("profiles", {})
    active = config.get("active_profile")
    if not profiles:
        print("No profiles defined.")
        return 0
    for name in sorted(profiles):
        marker = "*" if name == active else " "
        print(f"  {marker} {name}")
    return 0


def cmd_profile_add(args: argparse.Namespace, config: Config) -> int:
    try:
        config.add_profile(args.name)
        config.save()
        print(f"Profile '{args.name}' added.")
    except ValueError as exc:
        print(f"error: {exc}")
        return 1
    return 0


def cmd_profile_deploy(args: argparse.Namespace, config: Config) -> int:
    name: Optional[str] = args.name or config.get("active_profile")
    if not name:
        print("error: no profile specified and no active profile set.")
        return 1
    try:
        deployed = deploy_profile(name, config)
        config.set("active_profile", name)
        config.save()
        print(f"Deployed profile '{name}': {len(deployed)} symlink(s) created.")
    except ProfileDeployError as exc:
        print(f"error: {exc}")
        return 1
    return 0


def cmd_profile_undeploy(args: argparse.Namespace, config: Config) -> int:
    name: Optional[str] = args.name or config.get("active_profile")
    if not name:
        print("error: no profile specified and no active profile set.")
        return 1
    try:
        removed = undeploy_profile(name, config)
        if config.get("active_profile") == name:
            config.set("active_profile", None)
            config.save()
        print(f"Undeployed profile '{name}': {len(removed)} symlink(s) removed.")
    except ProfileDeployError as exc:
        print(f"error: {exc}")
        return 1
    return 0


def register_profile_subcommands(sub) -> None:
    # list
    p_list = sub.add_parser("list", help="List available profiles.")
    p_list.set_defaults(func=cmd_profile_list)

    # add
    p_add = sub.add_parser("add", help="Add a new profile.")
    p_add.add_argument("name", help="Profile name.")
    p_add.set_defaults(func=cmd_profile_add)

    # deploy
    p_deploy = sub.add_parser("deploy", help="Deploy a profile's dotfiles.")
    p_deploy.add_argument("name", nargs="?", help="Profile name (defaults to active).")
    p_deploy.set_defaults(func=cmd_profile_deploy)

    # undeploy
    p_undeploy = sub.add_parser("undeploy", help="Remove a profile's symlinks.")
    p_undeploy.add_argument("name", nargs="?", help="Profile name (defaults to active).")
    p_undeploy.set_defaults(func=cmd_profile_undeploy)
