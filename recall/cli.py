"""Recall CLI — the `recall` command.

Usage highlights:
  recall "kill the port my django app is using"   ask in natural language
  recall fix "<paste error output>"               diagnose & fix an error
  recall status                                   project memory summary
  recall note "stripe webhook failing at line 234"
  recall workflow save pre-commit "pytest" "flake8 ."
  recall workflow run pre-commit
  recall init                                     install shell history hook
"""

from __future__ import annotations

import os
import subprocess
import sys
import time

import typer
from rich.console import Console
from rich.panel import Panel

from . import __version__, ai, shell
from .config import load_config, save_config
from .context import build_context, detect_project
from .store import Store

app = typer.Typer(
    name="recall",
    help="Recall — the AI brain for your terminal.",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


def _store() -> Store:
    return Store()


def _confirm_and_run(command: str, caution: bool, store: Store) -> int | None:
    style = "bold red" if caution else "bold green"
    console.print(f"\n  [{style}]$ {command}[/{style}]")
    if caution:
        console.print("  [yellow]⚠ This command can be destructive — read it before running.[/yellow]")
    if not typer.confirm("  Run it?", default=not caution):
        return None
    proc = subprocess.run(command, shell=True)
    store.log_command(command, os.getcwd(), proc.returncode, source="recall")
    return proc.returncode


@app.command()
def ask(query: list[str] = typer.Argument(..., help="What you want, in plain language (English/Urdu/mixed)")):
    """Ask Recall for a command in natural language."""
    text = " ".join(query)
    store = _store()
    cfg = load_config()
    try:
        with console.status("[dim]Recall soch raha hai…[/dim]"):
            suggestion = ai.suggest_command(text, build_context(store, cfg["max_history_context"]))
    except ai.MissingAPIKeyError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    console.print(f"\n  [cyan]Recall:[/cyan] {suggestion.explanation}")
    if suggestion.command:
        _confirm_and_run(suggestion.command, suggestion.caution, store)
    else:
        console.print("  [dim]No single command fits this — try rephrasing.[/dim]")


@app.command()
def fix(error: list[str] = typer.Argument(..., help="Paste the error output (quote it)")):
    """Diagnose an error and suggest a fix — checks your own past fixes first."""
    text = " ".join(error)
    store = _store()

    known = store.find_fix(text)
    if known and known["success_count"] > 0:
        total = known["success_count"] + known["fail_count"]
        console.print(
            Panel(
                f"[bold]I've seen this error before.[/bold]\n\n"
                f"Fix that worked for you: [green]$ {known['fix_command']}[/green]\n"
                f"Confidence: {known['success_count']}/{total} times it worked on your machine",
                title="Recall — from your history", border_style="cyan",
            )
        )
        code = _confirm_and_run(known["fix_command"], caution=False, store=store)
        if code is not None:
            store.record_fix(text, known["fix_command"], worked=(code == 0))
        return

    cfg = load_config()
    try:
        with console.status("[dim]Analyzing error…[/dim]"):
            s = ai.suggest_fix(text, build_context(store, cfg["max_history_context"]))
    except ai.MissingAPIKeyError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    console.print(f"\n  [cyan]Recall:[/cyan] {s.diagnosis or ''}")
    console.print(f"  {s.explanation}")
    if s.command:
        code = _confirm_and_run(s.command, s.caution, store)
        if code is not None:
            store.record_fix(text, s.command, worked=(code == 0))
            console.print("  [dim]Noted — I'll remember whether this fix worked.[/dim]")


@app.command()
def status():
    """Show what Recall remembers about the current project."""
    store = _store()
    project = detect_project(os.getcwd())
    memories = store.project_memories(project)
    last = store.last_activity(project)
    recent = store.recent_history(limit=5, cwd=os.getcwd())

    lines = [f"[bold]Project:[/bold] {os.path.basename(project)}"]
    if last:
        days = (time.time() - last) / 86400
        lines.append(f"[bold]Last activity:[/bold] {days:.0f} day(s) ago" if days >= 1
                     else "[bold]Last activity:[/bold] today")
    if memories:
        lines.append("\n[bold]Notes & decisions:[/bold]")
        for m in memories[:10]:
            lines.append(f"  • \\[{m['kind']}] {m['content']}")
    if recent:
        lines.append("\n[bold]Recent commands here:[/bold]")
        for r in recent:
            lines.append(f"  $ {r['command']}")
    if not memories and not recent:
        lines.append("[dim]Nothing yet — run `recall init` to start capturing history, "
                     "and `recall note \"...\"` to save project notes.[/dim]")
    console.print(Panel("\n".join(lines), title="Recall — project memory", border_style="cyan"))


@app.command()
def note(text: list[str] = typer.Argument(..., help="Note to remember for this project"),
         kind: str = typer.Option("note", help="note | decision | issue | next-step")):
    """Save a note/decision/issue against the current project."""
    store = _store()
    project = detect_project(os.getcwd())
    store.add_memory(project, " ".join(text), kind=kind)
    console.print(f"[green]✓ Remembered for {os.path.basename(project)}[/green]")


@app.command()
def history(search: list[str] = typer.Argument(None, help="Search terms (empty = recent)")):
    """Search your captured command history."""
    store = _store()
    rows = (store.search_history(" ".join(search)) if search
            else store.recent_history(limit=20))
    if not rows:
        console.print("[dim]No matching history. Run `recall init` to start capturing commands.[/dim]")
        return
    for r in rows:
        when = time.strftime("%b %d %H:%M", time.localtime(r["ts"]))
        console.print(f"[dim]{when}  {r['cwd']}[/dim]\n  $ {r['command']}")


workflow_app = typer.Typer(help="Save and run repeatable command sequences.", no_args_is_help=True)
app.add_typer(workflow_app, name="workflow")


@workflow_app.command("save")
def workflow_save(name: str, steps: list[str] = typer.Argument(..., help="Each step as a quoted command")):
    """Save a named workflow, e.g.: recall workflow save pre-commit "pytest" "flake8 ."""
    _store().save_workflow(name, steps, project=detect_project(os.getcwd()))
    console.print(f"[green]✓ Workflow '{name}' saved ({len(steps)} steps). Run: recall workflow run {name}[/green]")


@workflow_app.command("run")
def workflow_run(name: str):
    """Run a saved workflow, stopping on the first failure."""
    store = _store()
    wf = store.get_workflow(name)
    if not wf:
        console.print(f"[red]No workflow named '{name}'. See: recall workflow list[/red]")
        raise typer.Exit(1)
    steps, _ = wf
    for i, step in enumerate(steps, 1):
        console.print(f"\n[bold cyan]({i}/{len(steps)})[/bold cyan] $ {step}")
        proc = subprocess.run(step, shell=True)
        store.log_command(step, os.getcwd(), proc.returncode, source="workflow")
        if proc.returncode != 0:
            console.print(f"[red]✗ Step {i} failed (exit {proc.returncode}) — stopping.[/red]")
            raise typer.Exit(proc.returncode)
    store.bump_workflow(name)
    console.print(f"\n[green]✓ Workflow '{name}' completed.[/green]")


@workflow_app.command("list")
def workflow_list():
    """List saved workflows."""
    rows = _store().list_workflows()
    if not rows:
        console.print("[dim]No workflows yet. Save one: recall workflow save <name> \"cmd1\" \"cmd2\"[/dim]")
        return
    import json as _json
    for r in rows:
        steps = _json.loads(r["steps"])
        console.print(f"[bold]{r['name']}[/bold] — {len(steps)} steps, run {r['run_count']}x")
        for s in steps:
            console.print(f"  $ {s}")


@app.command()
def init():
    """Install the shell hook that captures your command history locally."""
    sh = shell.detect_shell()
    if sh == "unknown":
        console.print("[yellow]Couldn't detect zsh/bash. Add this to your shell rc manually:[/yellow]")
        console.print(shell.ZSH_HOOK)
        return
    installed, msg = shell.install_hook(sh)
    console.print(f"[green]✓ {msg}[/green]" if installed else f"[dim]{msg}[/dim]")
    console.print("[dim]All history stays local in ~/.recall/recall.db — nothing is uploaded.[/dim]")


config_app = typer.Typer(help="View or change Recall settings.", no_args_is_help=True)
app.add_typer(config_app, name="config")


@config_app.command("set")
def config_set(key: str, value: str):
    """Set a config value, e.g.: recall config set api_key sk-ant-..."""
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
    console.print(f"[green]✓ {key} set[/green]")


@config_app.command("show")
def config_show():
    """Show current config (API key masked)."""
    cfg = load_config()
    for k, v in cfg.items():
        if k == "api_key" and v:
            v = str(v)[:10] + "…"
        console.print(f"{k} = {v}")


@app.command("_log", hidden=True)
def _log(command: list[str] = typer.Argument(...),
         exit_code: int = typer.Option(None, "--exit-code")):
    """Internal: called by the shell hook to record a command."""
    _store().log_command(" ".join(command), os.getcwd(), exit_code, source="shell")


@app.command()
def version():
    """Print Recall's version."""
    console.print(f"recall {__version__}")


def main():  # pragma: no cover
    # Allow `recall some natural language` without the `ask` subcommand:
    # if the first arg isn't a known command, treat everything as a query.
    known = {"ask", "fix", "status", "note", "history", "workflow", "init",
             "config", "version", "_log", "--help", "-h", "--install-completion",
             "--show-completion"}
    if len(sys.argv) > 1 and sys.argv[1] not in known:
        sys.argv.insert(1, "ask")
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
