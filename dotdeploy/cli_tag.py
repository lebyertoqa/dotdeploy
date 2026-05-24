"""CLI sub-commands for profile tagging."""

from __future__ import annotations

import argparse
import sys

from .config import Config
from .tag import TagError, add_tag, list_tags, profiles_with_tag, remove_tag


def _get_config(args: argparse.Namespace) -> Config:
    cfg = Config(args.config)
    cfg.load()
    return cfg


def cmd_tag_add(args: argparse.Namespace) -> None:
    cfg = _get_config(args)
    try:
        add_tag(cfg, args.profile, args.tag)
        print(f"Tag {args.tag!r} added to profile {args.profile!r}.")
    except TagError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_tag_remove(args: argparse.Namespace) -> None:
    cfg = _get_config(args)
    try:
        remove_tag(cfg, args.profile, args.tag)
        print(f"Tag {args.tag!r} removed from profile {args.profile!r}.")
    except TagError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_tag_list(args: argparse.Namespace) -> None:
    cfg = _get_config(args)
    try:
        tags = list_tags(cfg, args.profile)
    except TagError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    if tags:
        for t in tags:
            print(t)
    else:
        print(f"No tags for profile {args.profile!r}.")


def cmd_tag_filter(args: argparse.Namespace) -> None:
    cfg = _get_config(args)
    profiles = profiles_with_tag(cfg, args.tag)
    if profiles:
        for p in profiles:
            print(p)
    else:
        print(f"No profiles carry tag {args.tag!r}.")


def register_tag_subcommands(sub: argparse._SubParsersAction, global_config_arg: str) -> None:  # noqa: SLF001
    def _base(name: str, help_: str) -> argparse.ArgumentParser:
        p = sub.add_parser(name, help=help_)
        p.add_argument("--config", default=global_config_arg)
        return p

    pa = _base("tag-add", "Add a tag to a profile")
    pa.add_argument("profile")
    pa.add_argument("tag")
    pa.set_defaults(func=cmd_tag_add)

    pr = _base("tag-remove", "Remove a tag from a profile")
    pr.add_argument("profile")
    pr.add_argument("tag")
    pr.set_defaults(func=cmd_tag_remove)

    pl = _base("tag-list", "List tags for a profile")
    pl.add_argument("profile")
    pl.set_defaults(func=cmd_tag_list)

    pf = _base("tag-filter", "List profiles that carry a tag")
    pf.add_argument("tag")
    pf.set_defaults(func=cmd_tag_filter)
