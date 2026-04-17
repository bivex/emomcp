"""Configuration loader — reads YAML, falls back to env vars."""

from __future__ import annotations

import os
from pathlib import Path

import yaml


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent.parent


def load_config(path: str | None = None) -> dict:
    if path is None:
        path = os.environ.get("EMOMCP_CONFIG", str(_project_root() / "config" / "default.yaml"))

    cfg: dict = {
        "server": {"host": "0.0.0.0", "port": 8000},
        "database": {"path": "config/emotions.db"},
        "logging": {"level": "INFO", "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"},
    }

    p = Path(path)
    if p.exists():
        with open(p) as f:
            file_cfg = yaml.safe_load(f) or {}
        _deep_merge(cfg, file_cfg)

    cfg["server"]["host"] = os.environ.get("EMOMCP_HOST", cfg["server"]["host"])
    cfg["server"]["port"] = int(os.environ.get("EMOMCP_PORT", cfg["server"]["port"]))
    cfg["database"]["path"] = os.environ.get("EMOMCP_DB", cfg["database"]["path"])

    if not Path(cfg["database"]["path"]).is_absolute():
        cfg["database"]["path"] = str(_project_root() / cfg["database"]["path"])

    return cfg


def _deep_merge(base: dict, override: dict) -> dict:
    for k, v in override.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v
    return base
