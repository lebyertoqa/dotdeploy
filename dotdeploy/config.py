"""Configuration management for dotdeploy."""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "dotdeploy" / "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "dotfiles_dir": str(Path.home() / ".dotfiles"),
    "active_profile": "default",
    "profiles": {
        "default": {
            "files": []
        }
    },
    "remote": {
        "enabled": False,
        "provider": None,
        "repo": None
    }
}


class Config:
    """Handles loading, saving, and accessing dotdeploy configuration."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        self._data: Dict[str, Any] = {}

    def load(self) -> None:
        """Load configuration from disk, creating defaults if not present."""
        if not self.config_path.exists():
            self._data = dict(DEFAULT_CONFIG)
            return
        with open(self.config_path, "r") as f:
            self._data = json.load(f)

    def save(self) -> None:
        """Persist configuration to disk."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self._data, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a top-level config value."""
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a top-level config value."""
        self._data[key] = value

    @property
    def active_profile(self) -> str:
        return self._data.get("active_profile", "default")

    @active_profile.setter
    def active_profile(self, profile: str) -> None:
        if profile not in self._data.get("profiles", {}):
            raise ValueError(f"Profile '{profile}' does not exist.")
        self._data["active_profile"] = profile

    @property
    def profiles(self) -> Dict[str, Any]:
        return self._data.get("profiles", {})

    def add_profile(self, name: str) -> None:
        """Add a new empty profile."""
        if name in self._data.setdefault("profiles", {}):
            raise ValueError(f"Profile '{name}' already exists.")
        self._data["profiles"][name] = {"files": []}

    def remove_profile(self, name: str) -> None:
        """Remove a profile by name."""
        if name == "default":
            raise ValueError("Cannot remove the default profile.")
        self._data.get("profiles", {}).pop(name, None)
        if self.active_profile == name:
            self._data["active_profile"] = "default"

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)
