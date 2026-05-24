"""CLI subcommands for dotdeploy template rendering."""

from __future__ import annotations

import argparse
from pathlib import Path

from dotdeploy.config import Config
from dotdeploy.template import render_file, TemplateError


def _get_config(args: argparse.Namespace) -> Config:
    cfg = Config(args.config)
    cfg.load()
    return cfg


def cmd_template_render(args: argparse.Namespace) -> None:
    """Render a single template file to a destination path."""
    cfg = _get_config(args)

    variables: dict[str, str] = {}
    for pair in args.var or []:
        if "=" not in pair:
            print(f"Error: variable must be KEY=VALUE, got '{pair}'")
            raise SystemExit(1)
        key, _, value = pair.partition("=")
        variables[key.strip()] = value.strip()

    # Merge profile-level variables when a profile is specified
    if args.profile:
        profiles = cfg.get("profiles", {})
        if args.profile not in profiles:
            print(f"Error: unknown profile '{args.profile}'")
            raise SystemExit(1)
        profile_vars = profiles[args.profile].get("variables", {})
        merged = {**profile_vars, **variables}
    else:
        merged = variables

    src = Path(args.source)
    dest = Path(args.dest)

    try:
        render_file(src, dest, merged)
        print(f"Rendered {src} -> {dest}")
    except TemplateError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)


def register_template_subcommands(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("template-render", help="Render a dotfile template")
    p.add_argument("source", help="Path to template file (.ddtpl)")
    p.add_argument("dest", help="Destination path for rendered output")
    p.add_argument(
        "--var",
        metavar="KEY=VALUE",
        action="append",
        help="Extra variable (repeatable)",
    )
    p.add_argument("--profile", default="", help="Profile to load variables from")
    p.set_defaults(func=cmd_template_render)
