"""CLI subcommands for the dotdeploy watch feature."""

import sys
from dotdeploy.config import Config
from dotdeploy.watch import poll_once, watch, WatchError


def _get_config(args) -> Config:
    cfg = Config(args.config)
    cfg.load()
    return cfg


def cmd_watch_poll(args) -> None:
    """Run a single drift-check pass and print results."""
    cfg = _get_config(args)
    profiles = args.profiles if args.profiles else None
    try:
        events = poll_once(cfg, profiles)
    except WatchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not events:
        print("No drift detected.")
        return

    for event in events:
        print(f"DRIFT  profile={event.profile}")
        for target in event.changed_targets:
            print(f"       {target}")


def cmd_watch_loop(args) -> None:  # pragma: no cover
    """Continuously poll and print drift events until interrupted."""
    cfg = _get_config(args)
    profiles = args.profiles if args.profiles else None
    interval = float(args.interval)
    print(f"Watching (interval={interval}s) — press Ctrl-C to stop")
    try:
        for event in watch(cfg, profiles, interval=interval):
            print(event)
    except WatchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStopped.")


def register_watch_subcommands(sub) -> None:
    # dotdeploy watch poll [--profiles p1 p2]
    p_poll = sub.add_parser("poll", help="Check for symlink drift once")
    p_poll.add_argument("--profiles", nargs="*", metavar="PROFILE",
                        help="Profiles to check (default: all)")
    p_poll.set_defaults(func=cmd_watch_poll)

    # dotdeploy watch loop [--profiles p1 p2] [--interval N]
    p_loop = sub.add_parser("loop", help="Continuously watch for symlink drift")
    p_loop.add_argument("--profiles", nargs="*", metavar="PROFILE",
                        help="Profiles to watch (default: all)")
    p_loop.add_argument("--interval", default=5.0, metavar="SECONDS",
                        help="Poll interval in seconds (default: 5)")
    p_loop.set_defaults(func=cmd_watch_loop)
