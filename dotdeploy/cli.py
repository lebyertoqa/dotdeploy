"""Main CLI entry point for dotdeploy."""

import argparse
import sys

from dotdeploy.cli_remote import register_remote_subcommands
from dotdeploy.cli_profile import register_profile_subcommands
from dotdeploy.config import Config


DEFAULT_CONFIG = "~/.dotdeploy/config.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dotdeploy",
        description="Minimal dotfiles manager with profile switching and remote backup.",
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG,
        metavar="PATH",
        help=f"Path to config file (default: {DEFAULT_CONFIG})",
    )

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    register_profile_subcommands(sub)
    register_remote_subcommands(sub)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = Config(args.config)
    config.load()

    try:
        return args.func(args, config) or 0
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
