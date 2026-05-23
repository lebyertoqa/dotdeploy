"""CLI subcommands for managing individual symlinks."""

import argparse
from pathlib import Path

from .config import Config
from .symlink import create_symlink, remove_symlink, SymlinkError


def _get_config(args) -> Config:
    cfg = Config(args.config)
    cfg.load()
    return cfg


def cmd_symlink_add(args) -> int:
    """Create a symlink from TARGET -> SOURCE and record it in the active profile."""
    cfg = _get_config(args)
    profile = args.profile or cfg.get("active_profile")
    if not profile:
        print("error: no active profile set; use --profile or 'profile deploy'")
        return 1

    source = str(Path(args.source).expanduser().resolve())
    target = str(Path(args.target).expanduser())

    try:
        create_symlink(source, target, backup=not args.no_backup)
    except SymlinkError as exc:
        print(f"error: {exc}")
        return 1

    profiles = cfg.get("profiles", {})
    entry = profiles.setdefault(profile, {"links": []})
    links = entry.setdefault("links", [])
    record = {"source": source, "target": target}
    if record not in links:
        links.append(record)
        cfg.save()
        print(f"added link: {target} -> {source} (profile: {profile})")
    else:
        print(f"link already recorded in profile '{profile}'")
    return 0


def cmd_symlink_remove(args) -> int:
    """Remove a symlink by TARGET and optionally unrecord it from the profile."""
    cfg = _get_config(args)
    profile = args.profile or cfg.get("active_profile")

    target = str(Path(args.target).expanduser())

    try:
        remove_symlink(target)
    except SymlinkError as exc:
        print(f"error: {exc}")
        return 1

    if profile:
        profiles = cfg.get("profiles", {})
        links = profiles.get(profile, {}).get("links", [])
        before = len(links)
        profiles[profile]["links"] = [
            lnk for lnk in links if lnk.get("target") != target
        ]
        if len(profiles[profile]["links"]) < before:
            cfg.save()
            print(f"removed link and unrecorded from profile '{profile}': {target}")
            return 0

    print(f"removed link: {target}")
    return 0


def register_symlink_subcommands(sub: argparse._SubParsersAction) -> None:
    """Attach symlink subcommands to an existing subparser group."""
    # symlink add
    p_add = sub.add_parser("symlink-add", help="create a symlink and record it")
    p_add.add_argument("source", help="dotfile source path (in dotfiles repo)")
    p_add.add_argument("target", help="symlink target path (e.g. ~/.bashrc)")
    p_add.add_argument("--profile", default=None, help="profile to record link in")
    p_add.add_argument("--no-backup", action="store_true", help="do not backup existing file")
    p_add.set_defaults(func=cmd_symlink_add)

    # symlink remove
    p_rm = sub.add_parser("symlink-remove", help="remove a symlink and unrecord it")
    p_rm.add_argument("target", help="symlink target path to remove")
    p_rm.add_argument("--profile", default=None, help="profile to unrecord link from")
    p_rm.set_defaults(func=cmd_symlink_remove)
