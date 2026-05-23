"""Pre/post deploy hook execution for dotdeploy profiles."""

import subprocess
from pathlib import Path
from typing import List, Optional


class HookError(Exception):
    """Raised when a hook script fails or is misconfigured."""


HOOK_EVENTS = ("pre_deploy", "post_deploy", "pre_undeploy", "post_undeploy")


def _hooks_dir(config_dir: Path) -> Path:
    return config_dir / "hooks"


def hook_path(config_dir: Path, profile: str, event: str) -> Path:
    """Return the expected path for a hook script."""
    if event not in HOOK_EVENTS:
        raise HookError(f"Unknown hook event '{event}'. Valid: {HOOK_EVENTS}")
    return _hooks_dir(config_dir) / profile / event


def list_hooks(config_dir: Path, profile: str) -> List[str]:
    """Return event names that have a registered hook for the given profile."""
    profile_hooks_dir = _hooks_dir(config_dir) / profile
    if not profile_hooks_dir.exists():
        return []
    return [
        p.name
        for p in sorted(profile_hooks_dir.iterdir())
        if p.is_file() and p.name in HOOK_EVENTS
    ]


def register_hook(config_dir: Path, profile: str, event: str, script: str) -> Path:
    """Write a hook script for a profile event. Returns the hook path."""
    path = hook_path(config_dir, profile, event)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(script)
    path.chmod(0o755)
    return path


def remove_hook(config_dir: Path, profile: str, event: str) -> bool:
    """Remove a hook. Returns True if it existed, False otherwise."""
    path = hook_path(config_dir, profile, event)
    if path.exists():
        path.unlink()
        return True
    return False


def run_hook(
    config_dir: Path,
    profile: str,
    event: str,
    env: Optional[dict] = None,
) -> Optional[subprocess.CompletedProcess]:
    """Execute the hook for a profile event if it exists.

    Returns CompletedProcess on success, None if no hook registered.
    Raises HookError if the script exits with a non-zero status.
    """
    path = hook_path(config_dir, profile, event)
    if not path.exists():
        return None
    result = subprocess.run(
        [str(path)],
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        raise HookError(
            f"Hook '{event}' for profile '{profile}' failed (exit {result.returncode}):\n"
            f"{result.stderr.strip()}"
        )
    return result
