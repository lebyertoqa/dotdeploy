"""Entry-point for the dotdeploy CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotdeploy.cli_profile import register_profile_subcommands
from dotdeploy.cli_symlink import register_symlink_subcommands
from dotdeploy.cli_remote import register_remote_subcommands
from dotdeploy.cli_diff import register_diff_subcommands
from dotdeploy.cli_audit import register_audit_subcommands
from dotdeploy.cli_hooks import register_hook_subcommands
from dotdeploy.cli_encrypt import register_encrypt_subcommands
from dotdeploy.cli_template import register_template_subcommands

_DEFAULT_CONFIG = Path.home() / ".dotdeploy" / "config.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dotdeploy",
        description="Minimal dotfiles manager with profile switching and remote backup.",
    )
    parser.add_argument(
        "--config",
        default=str(_DEFAULT_CONFIG),
        metavar="PATH",
        help="Path to dotdeploy config file (default: %(default)s)",
    )

    sub = parser.add_subparsers(dest="command", metavar="<command>")

    register_profile_subcommands(sub)
    register_symlink_subcommands(sub)
    register_remote_subcommands(sub)
    register_diff_subcommands(sub)
    register_audit_subcommands(sub)
    register_hook_subcommands(sub)
    register_encrypt_subcommands(sub)
    register_template_subcommands(sub)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)
