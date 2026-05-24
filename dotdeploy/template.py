"""Template rendering for dotfiles with variable substitution."""

import re
import os
from pathlib import Path

TEMPLATE_EXT = ".ddtpl"
_VAR_PATTERN = re.compile(r"\{\{\s*(\w+)\s*\}\}")


class TemplateError(Exception):
    """Raised when template rendering fails."""


def _default_variables() -> dict:
    """Return default variables available in every template."""
    return {
        "HOME": str(Path.home()),
        "USER": os.environ.get("USER", os.environ.get("USERNAME", "")),
        "HOSTNAME": os.environ.get("HOSTNAME", ""),
    }


def render(template_text: str, variables: dict | None = None) -> str:
    """Render *template_text* replacing ``{{ VAR }}`` placeholders.

    Variables from *variables* override the built-in defaults.
    Unknown placeholders raise :class:`TemplateError`.
    """
    ctx = _default_variables()
    if variables:
        ctx.update(variables)

    def _replace(match: re.Match) -> str:
        key = match.group(1)
        if key not in ctx:
            raise TemplateError(f"Unknown template variable: '{key}'")
        return ctx[key]

    return _VAR_PATTERN.sub(_replace, template_text)


def render_file(src: Path, dest: Path, variables: dict | None = None) -> None:
    """Read *src*, render it, and write the result to *dest*.

    Raises :class:`TemplateError` on unknown variables or I/O errors.
    """
    if not src.exists():
        raise TemplateError(f"Template source not found: {src}")
    try:
        text = src.read_text(encoding="utf-8")
        rendered = render(text, variables)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(rendered, encoding="utf-8")
    except TemplateError:
        raise
    except OSError as exc:
        raise TemplateError(f"I/O error rendering template: {exc}") from exc


def is_template(path: Path) -> bool:
    """Return True if *path* has the template extension."""
    return path.suffix == TEMPLATE_EXT
