"""Profile validation — checks that all declared symlinks are sane before deployment."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List

from dotdeploy.config import Config
from dotdeploy.symlink import expand


@dataclass
class ValidationIssue:
    link: str
    target: str
    reason: str

    def __str__(self) -> str:
        return f"{self.link} -> {self.target}: {self.reason}"


@dataclass
class ValidationResult:
    profile: str
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0

    def __str__(self) -> str:
        if self.ok:
            return f"Profile '{self.profile}' is valid."
        lines = [f"Profile '{self.profile}' has {len(self.issues)} issue(s):"]
        for issue in self.issues:
            lines.append(f"  - {issue}")
        return "\n".join(lines)


class ValidateError(Exception):
    pass


def validate_profile(config: Config, profile_name: str) -> ValidationResult:
    """Validate all symlink entries for *profile_name*.

    Checks performed:
    - The profile exists in the config.
    - The source (target) path exists on disk.
    - The link path is not an existing regular file that would be silently overwritten
      (i.e. not a symlink and backup is disabled).
    """
    profiles = config.get("profiles", {})
    if profile_name not in profiles:
        raise ValidateError(f"Profile '{profile_name}' not found.")

    symlinks: dict = profiles[profile_name].get("symlinks", {})
    result = ValidationResult(profile=profile_name)

    backup_enabled: bool = bool(config.get("backup", True))

    for link_raw, target_raw in symlinks.items():
        link = expand(link_raw)
        target = expand(target_raw)

        if not os.path.exists(target):
            result.issues.append(
                ValidationIssue(link=link_raw, target=target_raw, reason="source path does not exist")
            )

        if os.path.exists(link) and not os.path.islink(link) and not backup_enabled:
            result.issues.append(
                ValidationIssue(
                    link=link_raw,
                    target=target_raw,
                    reason="link path is an existing file and backup is disabled",
                )
            )

    return result
