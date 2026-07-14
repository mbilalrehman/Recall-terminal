"""Shell integration: hooks that capture every command you run into
Recall's local history, so the AI has real context to work with.

Everything stays on your machine (~/.recall/recall.db). Nothing is
uploaded anywhere.
"""

from __future__ import annotations

import os
from pathlib import Path

ZSH_HOOK = r"""
# --- Recall shell hook (zsh) ---
_recall_preexec() { RECALL_LAST_CMD="$1"; }
_recall_precmd() {
  local code=$?
  if [[ -n "$RECALL_LAST_CMD" ]]; then
    command recall _log --exit-code $code -- "$RECALL_LAST_CMD" &>/dev/null &!
    RECALL_LAST_CMD=""
  fi
}
autoload -Uz add-zsh-hook
add-zsh-hook preexec _recall_preexec
add-zsh-hook precmd _recall_precmd
# --- end Recall hook ---
"""

BASH_HOOK = r"""
# --- Recall shell hook (bash) ---
_recall_log() {
  local code=$?
  local cmd
  cmd=$(HISTTIMEFORMAT= history 1 | sed 's/^ *[0-9]* *//')
  if [[ -n "$cmd" && "$cmd" != "$RECALL_LAST_LOGGED" ]]; then
    RECALL_LAST_LOGGED="$cmd"
    (command recall _log --exit-code $code -- "$cmd" &>/dev/null &)
  fi
}
PROMPT_COMMAND="_recall_log${PROMPT_COMMAND:+;$PROMPT_COMMAND}"
# --- end Recall hook ---
"""

MARKER = "--- Recall shell hook"


def detect_shell() -> str:
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return "zsh"
    if "bash" in shell:
        return "bash"
    return "unknown"


def rc_file(shell: str) -> Path:
    return Path.home() / (".zshrc" if shell == "zsh" else ".bashrc")


def hook_snippet(shell: str) -> str:
    return ZSH_HOOK if shell == "zsh" else BASH_HOOK


def install_hook(shell: str) -> tuple[bool, str]:
    """Append the hook to the rc file. Returns (installed, message)."""
    rc = rc_file(shell)
    if rc.exists() and MARKER in rc.read_text():
        return False, f"Hook already installed in {rc}"
    with rc.open("a") as f:
        f.write("\n" + hook_snippet(shell))
    return True, f"Hook installed in {rc} — restart your shell or run: source {rc}"
