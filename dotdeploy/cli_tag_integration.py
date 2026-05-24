"""Thin integration helper: wire tag sub-commands into the main CLI parser.

This module is imported by dotdeploy/cli.py to keep cli.py small.
"""

from __future__ import annotations

import argparse

from .cli_tag import register_tag_subcommands


def attach(sub: argparse._SubParsersAction, default_config: str) -> None:  # noqa: SLF001
    """Register all tag-related sub-commands onto *sub*.

    Parameters
    ----------
    sub:
        The sub-parsers action returned by ``parser.add_subparsers()``.
    default_config:
        Default path forwarded to every tag sub-command's ``--config``
        argument so callers do not need to repeat it.
    """
    register_tag_subcommands(sub, default_config)


__all__ = ["attach"]
