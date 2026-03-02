"""Configuration Manager for OpenPango"""
import json
import os
from pathlib import Path
from typing import Any


class ConfigManager:
    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path or "~/.openclaw/config.json").expanduser()
        self.config = {}
        self._load()
    
    def _load(self):
        if self.config_path.exists():
            with open(self.config_path) as f:
                self.config = json.load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by dot-notation key."""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # Check env var
                env_key = "OPENPANGO_" + "_".join(keys).upper()
                return os.getenv(env_key, default)
        return value
    
    def set(self, key: str, value: Any):
        """Set config value."""
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value
        self._save()
    
    def _save(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)


if __name__ == "__main__":
    config = ConfigManager()
    print("Config manager ready")
