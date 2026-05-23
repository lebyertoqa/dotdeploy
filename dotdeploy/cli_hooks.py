"""CLI subcommands for managing profile hooks."""

import argparse
from pathlib import Path

from dotdeploy.config import Config
from dotdeploy.hooks import (
    HOOK_EVENTS,
    HookError,
    list_hooks,
    register_hook,
    remove_hook,
)


def _get_config(args: argparse.Namespace) -> Config:
    cfg = Config(args.config)
    cfg.load()
    return cfg


def cmd_hook_list(args: argparse.Namespace) -> None:
    cfg = _get_config(args)
    profile = args.profile
    if profile not in cfg.get("profiles", {}):
        print(f"Unknown profile '{profile}'.")
        raise SystemExit(1)
    hooks = list_hooks(Path(args.config).parent, profile)
    if not hooks:
        print(f"No hooks registered for profile '{profile}'.")
    else:
        for event in hooks:
            print(f"  {event}")


def cmd_hook_add(args: argparse.Namespace) -> None:
    cfg = _get_config(args)
    profile = args.profile
    if profile not in cfg.get("profiles", {}):
        print(f"Unknown profile '{profile}'.")
        raise SystemExit(1)
    script_path = Path(args.script)
    if not script_path.exists():
        print(f"Script not found: {args.script}")
        raise SystemExit(1)
    script_content = script_path.read_text()
    try:
        path = register_hook(
            Path(args.config).parent, profile, args.event, script_content
        )
        print(f"Hook registered: {path}")
    except HookError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)


def cmd_hook_remove(args: argparse.Namespace) -> None:
    cfg = _get_config(args)
    profile = args.profile
    if profile not in cfg.get("profiles", {}):
        print(f"Unknown profile '{profile}'.")
        raise SystemExit(1)
    try:
        removed = remove_hook(Path(args.config).parent, profile, args.event)
        if removed:
            print(f"Hook '{args.event}' removed for profile '{profile}'.")
        else:
            print(f"No hook '{args.event}' found for profile '{profile}'.")
    except HookError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)


def register_hook_subcommands(
    subparsers: argparse._SubParsersAction,
    parent: argparse.ArgumentParser,
) -> None:
    hook_p = subparsers.add_parser("hook", help="Manage profile hooks", parents=[parent])
    hook_sub = hook_p.add_subparsers(dest="hook_cmd")

    p_list = hook_sub.add_parser("list", help="List hooks for a profile", parents=[parent])
    p_list.add_argument("profile")
    p_list.set_defaults(func=cmd_hook_list)

    p_add = hook_sub.add_parser("add", help="Register a hook script", parents=[parent])
    p_add.add_argument("profile")
    p_add.add_argument("event", choices=HOOK_EVENTS)
    p_add.add_argument("script", help="Path to executable script file")
    p_add.set_defaults(func=cmd_hook_add)

    p_rm = hook_sub.add_parser("remove", help="Remove a hook", parents=[parent])
    p_rm.add_argument("profile")
    p_rm.add_argument("event", choices=HOOK_EVENTS)
    p_rm.set_defaults(func=cmd_hook_remove)
