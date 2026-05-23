"""CLI sub-commands for the diff feature."""

from __future__ import annotations

import argparse
import sys

from .config import Config
from .diff import diff_profile


def _get_config(args: argparse.Namespace) -> Config:
    cfg = Config(args.config)
    cfg.load()
    return cfg


def cmd_diff(args: argparse.Namespace) -> None:
    """Print a diff of expected vs actual symlinks for a profile."""
    cfg = _get_config(args)
    profile = args.profile or cfg.get("active_profile")

    if not profile:
        print("error: no profile specified and no active profile set.", file=sys.stderr)
        sys.exit(1)

    try:
        result = diff_profile(cfg, profile)
    except KeyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if result.clean:
        print(f"Profile '{profile}' is clean — all symlinks are in place.")
        return

    if result.ok:
        for dst in result.ok:
            print(f"  OK       {dst}")
    if result.missing:
        for dst in result.missing:
            print(f"  MISSING  {dst}")
    if result.broken:
        for dst in result.broken:
            print(f"  BROKEN   {dst}")
    if result.extra:
        for dst in result.extra:
            print(f"  EXTRA    {dst}")

    sys.exit(1)


def register_diff_subcommands(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("diff", help="Show symlink diff for a profile")
    p.add_argument(
        "profile",
        nargs="?",
        default=None,
        help="Profile name (defaults to active profile)",
    )
    p.set_defaults(func=cmd_diff)
