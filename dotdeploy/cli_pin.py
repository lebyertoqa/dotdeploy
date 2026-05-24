"""CLI sub-commands for profile pinning."""

from __future__ import annotations

import argparse
from pathlib import Path

from dotdeploy.config import Config
from dotdeploy.pin import PinError, get_pinned, pin_profile, unpin_profile


def _get_config(args: argparse.Namespace) -> Config:
    cfg = Config(Path(args.config))
    cfg.load()
    return cfg


def cmd_pin_set(args: argparse.Namespace) -> None:
    """Pin a profile as the active one."""
    cfg = _get_config(args)
    try:
        pin_profile(cfg, args.profile)
    except PinError as exc:
        raise SystemExit(f"pin error: {exc}") from exc
    print(f"Pinned profile: {args.profile}")


def cmd_pin_clear(args: argparse.Namespace) -> None:
    """Remove the active-profile pin."""
    cfg = _get_config(args)
    unpin_profile(cfg)
    print("Active profile pin cleared.")


def cmd_pin_show(args: argparse.Namespace) -> None:
    """Show the currently pinned profile."""
    cfg = _get_config(args)
    pinned = get_pinned(cfg)
    if pinned:
        print(f"Active profile: {pinned}")
    else:
        print("No profile is currently pinned.")


def register_pin_subcommands(
    sub: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> None:
    p_set = sub.add_parser("pin-set", help="Pin a profile as active")
    p_set.add_argument("profile", help="Profile name to pin")
    p_set.set_defaults(func=cmd_pin_set)

    p_clear = sub.add_parser("pin-clear", help="Clear the active-profile pin")
    p_clear.set_defaults(func=cmd_pin_clear)

    p_show = sub.add_parser("pin-show", help="Show the currently pinned profile")
    p_show.set_defaults(func=cmd_pin_show)
