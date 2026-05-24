"""CLI sub-commands for profile alias management."""

from __future__ import annotations

import sys
from pathlib import Path

from dotdeploy.alias import AliasError, add_alias, list_aliases, remove_alias, resolve_alias
from dotdeploy.config import Config


def _get_config(args) -> Config:
    cfg = Config(Path(args.config))
    cfg.load()
    return cfg


def cmd_alias_add(args) -> None:
    cfg = _get_config(args)
    try:
        add_alias(cfg, args.alias, args.profile)
        print(f"Alias {args.alias!r} -> {args.profile!r} added.")
    except AliasError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_alias_remove(args) -> None:
    cfg = _get_config(args)
    try:
        remove_alias(cfg, args.alias)
        print(f"Alias {args.alias!r} removed.")
    except AliasError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_alias_list(args) -> None:
    cfg = _get_config(args)
    aliases = list_aliases(cfg)
    if not aliases:
        print("No aliases defined.")
        return
    for alias, profile in sorted(aliases.items()):
        print(f"  {alias} -> {profile}")


def cmd_alias_resolve(args) -> None:
    cfg = _get_config(args)
    result = resolve_alias(cfg, args.name)
    print(result)


def register_alias_subcommands(sub) -> None:
    p_add = sub.add_parser("add", help="Add a profile alias")
    p_add.add_argument("alias", help="Short alias name")
    p_add.add_argument("profile", help="Target profile name")
    p_add.set_defaults(func=cmd_alias_add)

    p_rm = sub.add_parser("remove", help="Remove a profile alias")
    p_rm.add_argument("alias", help="Alias to remove")
    p_rm.set_defaults(func=cmd_alias_remove)

    p_ls = sub.add_parser("list", help="List all aliases")
    p_ls.set_defaults(func=cmd_alias_list)

    p_res = sub.add_parser("resolve", help="Resolve an alias to its profile")
    p_res.add_argument("name", help="Alias or profile name")
    p_res.set_defaults(func=cmd_alias_resolve)
