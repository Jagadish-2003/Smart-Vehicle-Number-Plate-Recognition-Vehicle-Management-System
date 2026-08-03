"""Reads and writes the JSON-based application configuration."""
import json
import os
import threading
from config.settings import CONFIG_PATH

_lock = threading.Lock()


class ConfigManager:
    def __init__(self, path: str = CONFIG_PATH):
        self.path = path
        self._config = self._load()

    def _load(self) -> dict:
        with _lock:
            if not os.path.exists(self.path):
                raise FileNotFoundError(f"Config file not found at {self.path}")
            with open(self.path, "r") as f:
                return json.load(f)

    def reload(self) -> dict:
        self._config = self._load()
        return self._config

    def get(self, *keys, default=None):
        node = self._config
        for k in keys:
            if not isinstance(node, dict) or k not in node:
                return default
            node = node[k]
        return node

    def set(self, *keys_and_value):
        """set('model', 'confidence_threshold', 0.6)"""
        *keys, value = keys_and_value
        node = self._config
        for k in keys[:-1]:
            node = node.setdefault(k, {})
        node[keys[-1]] = value
        self._save()

    def _save(self):
        with _lock:
            with open(self.path, "w") as f:
                json.dump(self._config, f, indent=2)

    def as_dict(self) -> dict:
        return self._config


config_manager = ConfigManager()
