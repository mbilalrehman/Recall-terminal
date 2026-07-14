"""Configuration for Recall.

All state lives under ~/.recall/ :
  config.json  — user settings (model, API key if not in env)
  recall.db    — SQLite store (history, memories, workflows, fixes)
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

RECALL_HOME = Path(os.environ.get("RECALL_HOME", Path.home() / ".recall"))
CONFIG_PATH = RECALL_HOME / "config.json"
DB_PATH = RECALL_HOME / "recall.db"

DEFAULTS: dict[str, Any] = {
    "model": "claude-sonnet-5",
    "max_history_context": 30,
    "auto_run": False,
    "language": "auto",  # auto | en | ur — language Recall replies in
}


def ensure_home() -> None:
    RECALL_HOME.mkdir(parents=True, exist_ok=True)


def load_config() -> dict[str, Any]:
    ensure_home()
    cfg = dict(DEFAULTS)
    if CONFIG_PATH.exists():
        try:
            cfg.update(json.loads(CONFIG_PATH.read_text()))
        except (json.JSONDecodeError, OSError):
            pass
    return cfg


def save_config(cfg: dict[str, Any]) -> None:
    ensure_home()
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))


def get_api_key() -> str | None:
    """API key resolution order: env var, then config file."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    return load_config().get("api_key")
