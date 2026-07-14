"""SQLite persistence layer for Recall.

Tables:
  history    — every shell command captured by the shell hook or run via Recall
  memories   — per-project notes, decisions, and session state
  workflows  — named, reusable command sequences
  fixes      — error patterns and the fixes that worked, with success counts
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

from .config import DB_PATH, ensure_home

SCHEMA = """
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL NOT NULL,
    cwd TEXT NOT NULL,
    command TEXT NOT NULL,
    exit_code INTEGER,
    source TEXT DEFAULT 'shell'
);
CREATE INDEX IF NOT EXISTS idx_history_cwd ON history(cwd);
CREATE INDEX IF NOT EXISTS idx_history_ts ON history(ts);

CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL NOT NULL,
    project TEXT NOT NULL,
    kind TEXT NOT NULL DEFAULT 'note',
    content TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_memories_project ON memories(project);

CREATE TABLE IF NOT EXISTS workflows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    project TEXT,
    steps TEXT NOT NULL,
    created_ts REAL NOT NULL,
    run_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS fixes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL NOT NULL,
    error_snippet TEXT NOT NULL,
    fix_command TEXT NOT NULL,
    success_count INTEGER DEFAULT 0,
    fail_count INTEGER DEFAULT 0
);
"""


class Store:
    def __init__(self, db_path: Path | None = None):
        ensure_home()
        self.conn = sqlite3.connect(db_path or DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    # ------------------------------------------------------------- history
    def log_command(self, command: str, cwd: str, exit_code: int | None = None,
                    source: str = "shell") -> None:
        command = command.strip()
        if not command or command.startswith("recall _log"):
            return
        self.conn.execute(
            "INSERT INTO history (ts, cwd, command, exit_code, source) VALUES (?, ?, ?, ?, ?)",
            (time.time(), cwd, command, exit_code, source),
        )
        self.conn.commit()

    def recent_history(self, limit: int = 30, cwd: str | None = None) -> list[sqlite3.Row]:
        if cwd:
            cur = self.conn.execute(
                "SELECT * FROM history WHERE cwd = ? ORDER BY ts DESC LIMIT ?", (cwd, limit))
        else:
            cur = self.conn.execute(
                "SELECT * FROM history ORDER BY ts DESC LIMIT ?", (limit,))
        return cur.fetchall()

    def search_history(self, query: str, limit: int = 20) -> list[sqlite3.Row]:
        cur = self.conn.execute(
            "SELECT * FROM history WHERE command LIKE ? ORDER BY ts DESC LIMIT ?",
            (f"%{query}%", limit),
        )
        return cur.fetchall()

    # ------------------------------------------------------------ memories
    def add_memory(self, project: str, content: str, kind: str = "note") -> None:
        self.conn.execute(
            "INSERT INTO memories (ts, project, kind, content) VALUES (?, ?, ?, ?)",
            (time.time(), project, kind, content),
        )
        self.conn.commit()

    def project_memories(self, project: str, limit: int = 50) -> list[sqlite3.Row]:
        cur = self.conn.execute(
            "SELECT * FROM memories WHERE project = ? ORDER BY ts DESC LIMIT ?",
            (project, limit),
        )
        return cur.fetchall()

    def last_activity(self, project: str) -> float | None:
        cur = self.conn.execute(
            "SELECT MAX(ts) AS ts FROM history WHERE cwd LIKE ?", (f"{project}%",))
        row = cur.fetchone()
        return row["ts"] if row and row["ts"] else None

    # ----------------------------------------------------------- workflows
    def save_workflow(self, name: str, steps: list[str], project: str | None = None) -> None:
        self.conn.execute(
            "INSERT INTO workflows (name, project, steps, created_ts) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(name) DO UPDATE SET steps = excluded.steps, project = excluded.project",
            (name, project, json.dumps(steps), time.time()),
        )
        self.conn.commit()

    def get_workflow(self, name: str) -> tuple[list[str], str | None] | None:
        cur = self.conn.execute("SELECT * FROM workflows WHERE name = ?", (name,))
        row = cur.fetchone()
        if not row:
            return None
        return json.loads(row["steps"]), row["project"]

    def list_workflows(self) -> list[sqlite3.Row]:
        return self.conn.execute("SELECT * FROM workflows ORDER BY name").fetchall()

    def bump_workflow(self, name: str) -> None:
        self.conn.execute(
            "UPDATE workflows SET run_count = run_count + 1 WHERE name = ?", (name,))
        self.conn.commit()

    # --------------------------------------------------------------- fixes
    @staticmethod
    def _tokens(text: str) -> set[str]:
        import re
        return set(re.findall(r"[a-z0-9_\-./:]{4,}", text.lower()))

    def find_fix(self, error_text: str) -> sqlite3.Row | None:
        """Token-overlap match against stored error snippets. Good enough for
        the MVP; semantic search replaces this in Phase 2."""
        words = self._tokens(error_text)
        best, best_score = None, 0
        for row in self.conn.execute("SELECT * FROM fixes").fetchall():
            score = len(words & self._tokens(row["error_snippet"]))
            if score > best_score:
                best, best_score = row, score
        return best if best_score >= 2 else None

    def record_fix(self, error_text: str, fix_command: str, worked: bool) -> None:
        snippet = error_text.strip()[:400]
        cur = self.conn.execute(
            "SELECT id FROM fixes WHERE error_snippet = ? AND fix_command = ?",
            (snippet, fix_command),
        )
        row = cur.fetchone()
        col = "success_count" if worked else "fail_count"
        if row:
            self.conn.execute(
                f"UPDATE fixes SET {col} = {col} + 1 WHERE id = ?", (row["id"],))
        else:
            self.conn.execute(
                "INSERT INTO fixes (ts, error_snippet, fix_command, success_count, fail_count) "
                "VALUES (?, ?, ?, ?, ?)",
                (time.time(), snippet, fix_command, 1 if worked else 0, 0 if worked else 1),
            )
        self.conn.commit()
