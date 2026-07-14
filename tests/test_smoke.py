"""Smoke tests: store, redaction, and CLI wiring. No API key needed."""

import json

from typer.testing import CliRunner

from recall import __version__
from recall.cli import app
from recall.context import redact
from recall.store import Store

runner = CliRunner()


def test_store_history_and_search(tmp_path):
    s = Store(tmp_path / "t.db")
    s.log_command("docker compose up -d", "/proj", 0)
    s.log_command("git push", "/proj", 0)
    assert len(s.recent_history()) == 2
    hits = s.search_history("docker")
    assert len(hits) == 1 and "docker" in hits[0]["command"]


def test_store_ignores_own_log_calls(tmp_path):
    s = Store(tmp_path / "t.db")
    s.log_command("recall _log --exit-code 0 -- ls", "/proj")
    assert s.recent_history() == []


def test_workflows_roundtrip(tmp_path):
    s = Store(tmp_path / "t.db")
    s.save_workflow("pre-commit", ["pytest", "flake8 ."], project="/proj")
    steps, project = s.get_workflow("pre-commit")
    assert steps == ["pytest", "flake8 ."] and project == "/proj"


def test_fix_matching_and_confidence(tmp_path):
    s = Store(tmp_path / "t.db")
    s.record_fix("Error: Port 8000 is already in use.", "fuser -k 8000/tcp", worked=True)
    s.record_fix("Error: Port 8000 is already in use.", "fuser -k 8000/tcp", worked=True)
    row = s.find_fix("something about Port 8000 already in use again")
    assert row is not None and row["success_count"] == 2
    assert s.find_fix("completely unrelated words entirely") is None


def test_redact_secrets():
    dirty = (
        "export ANTHROPIC_API_KEY=sk-ant-abc123xyz789012 "
        "curl -u me:pw --header 'token: ghp_abcdefghijklmnopqrstuv12' "
        "aws AKIAIOSFODNN7EXAMPLE password=hunter22"
    )
    clean = redact(dirty)
    for secret in ("sk-ant", "ghp_", "AKIA", "hunter22"):
        assert secret not in clean


def test_cli_version_and_help():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0 and __version__ in result.stdout
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0 and "workflow" in result.stdout


def test_cli_note_and_status(tmp_path, monkeypatch):
    monkeypatch.setattr("recall.cli._store", lambda: Store(tmp_path / "t.db"))
    result = runner.invoke(app, ["note", "stripe", "webhook", "failing", "--kind", "issue"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0 and "stripe webhook failing" in result.stdout
