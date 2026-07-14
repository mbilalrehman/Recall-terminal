"""Gather the local context that makes Recall's answers personal:
OS, current directory, git state, and recent command history."""

from __future__ import annotations

import os
import platform
import re
import subprocess
import time
from pathlib import Path

from .store import Store

# Patterns for secrets that must never leave the machine, even inside
# history context sent to the API.
_SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{10,}"),                      # API keys (OpenAI/Anthropic style)
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),                       # GitHub tokens
    re.compile(r"AKIA[0-9A-Z]{16}"),                           # AWS access keys
    re.compile(r"(?i)(password|passwd|pwd|token|secret|api[_-]?key)\s*[=:]\s*\S+"),
    re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}"),  # JWTs
]


def redact(text: str) -> str:
    for pat in _SECRET_PATTERNS:
        text = pat.sub("[REDACTED]", text)
    return text


def _run(cmd: list[str]) -> str:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        return out.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def git_context(cwd: str) -> dict:
    if not _run(["git", "-C", cwd, "rev-parse", "--is-inside-work-tree"]) == "true":
        return {}
    return {
        "branch": _run(["git", "-C", cwd, "branch", "--show-current"]),
        "last_commit": _run(["git", "-C", cwd, "log", "-1", "--format=%h %s (%cr)"]),
        "dirty_files": len(_run(["git", "-C", cwd, "status", "--porcelain"]).splitlines()),
    }


def detect_project(cwd: str) -> str:
    """The project root is the nearest ancestor with a .git dir, else the cwd."""
    p = Path(cwd)
    for parent in [p, *p.parents]:
        if (parent / ".git").exists():
            return str(parent)
    return cwd


def build_context(store: Store, max_history: int = 30) -> dict:
    cwd = os.getcwd()
    project = detect_project(cwd)
    history = [
        {"cmd": redact(r["command"]), "cwd": r["cwd"]}
        for r in store.recent_history(limit=max_history)
    ]
    memories = [
        {"kind": r["kind"], "content": redact(r["content"])}
        for r in store.project_memories(project, limit=15)
    ]
    return {
        "os": f"{platform.system()} {platform.release()}",
        "cwd": cwd,
        "project": project,
        "git": git_context(cwd),
        "recent_commands": history,
        "project_memories": memories,
        "time": time.strftime("%Y-%m-%d %H:%M"),
    }
