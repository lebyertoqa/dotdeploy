"""CLI sub-commands for the audit log."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from dotdeploy.audit import AuditError, clear_events, read_events
from dotdeploy.config import Config


def _get_config(args: argparse.Namespace) -> Config:
    cfg = Config(args.config)
    cfg.load()
    return cfg


def cmd_audit_list(args: argparse.Namespace) -> None:
    cfg = _get_config(args)
    events = read_events(Path(cfg.path).parent)
    if not events:
        print("No audit events recorded.")
        return
    limit = getattr(args, "limit", None)
    if limit:
        events = events[-limit:]
    for ev in events:
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ev["timestamp"]))
        profile = ev.get("profile", "-")
        action = ev.get("action", "?")
        details = ev.get("details", {})
        detail_str = " ".join(f"{k}={v}" for k, v in details.items()) if details else ""
        print(f"{ts}  {action:<20}  profile={profile:<15}  {detail_str}")


def cmd_audit_clear(args: argparse.Namespace) -> None:
    cfg = _get_config(args)
    removed = clear_events(Path(cfg.path).parent)
    print(f"Cleared {removed} audit event(s).")


def register_audit_subcommands(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    audit_p = sub.add_parser("audit", help="Manage the audit log")
    audit_sub = audit_p.add_subparsers(dest="audit_cmd")

    list_p = audit_sub.add_parser("list", help="Show recorded events")
    list_p.add_argument(
        "-n", "--limit", type=int, default=0, metavar="N",
        help="Show only the last N events (0 = all)"
    )
    list_p.set_defaults(func=cmd_audit_list)

    clear_p = audit_sub.add_parser("clear", help="Delete the audit log")
    clear_p.set_defaults(func=cmd_audit_clear)
