"""Claude-powered engine: turns natural language + personal context into
exact shell commands, and errors into fixes."""

from __future__ import annotations

import json
from dataclasses import dataclass

from .config import get_api_key, load_config

SYSTEM_PROMPT = """\
You are Recall, an AI assistant that lives inside a developer's terminal.
You know the user's OS, current directory, git state, recent shell history,
and their saved project notes. Use that context to give answers tailored to
THIS user — not generic answers.

The user may write in English, Urdu (Roman script), or a mix. Reply in the
same language mix they used, but the shell command itself is always plain.

Respond ONLY with a JSON object, no markdown fences, with these keys:
  "command":     the exact shell command to run (string, or null if the
                 request isn't answerable with a command)
  "explanation": one or two short sentences explaining the command and,
                 when relevant, referencing the user's own context/history
  "caution":     true if the command is destructive or risky (rm, force
                 push, DROP, prune, kill, chmod/chown on system paths...)
"""

FIX_PROMPT = """\
You are Recall, an AI assistant inside a developer's terminal, diagnosing an
error the user just hit. You know their OS, directory, git state, and recent
commands — use them to give a fix for THEIR exact environment.

The user may write in English, Roman Urdu, or a mix; reply in the same mix.

Respond ONLY with a JSON object, no markdown fences, with these keys:
  "diagnosis":   one short sentence on what's wrong
  "command":     the exact fix command to run (string, or null)
  "explanation": brief note on why this fix, and a fallback if it fails
  "caution":     true if the fix is destructive or risky
"""


@dataclass
class Suggestion:
    command: str | None
    explanation: str
    caution: bool = False
    diagnosis: str | None = None


class MissingAPIKeyError(RuntimeError):
    pass


def _client():
    key = get_api_key()
    if not key:
        raise MissingAPIKeyError(
            "No API key found. Set ANTHROPIC_API_KEY or run: recall config set api_key <key>"
        )
    import anthropic

    return anthropic.Anthropic(api_key=key)


def _ask(system: str, user_content: str) -> dict:
    cfg = load_config()
    resp = _client().messages.create(
        model=cfg["model"],
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": user_content}],
    )
    text = resp.content[0].text.strip()
    # Be tolerant of models that wrap JSON in fences despite instructions.
    if text.startswith("```"):
        text = text.strip("`")
        text = text[text.find("{"):text.rfind("}") + 1]
    return json.loads(text)


def suggest_command(query: str, context: dict) -> Suggestion:
    payload = f"CONTEXT:\n{json.dumps(context, indent=1)}\n\nREQUEST:\n{query}"
    data = _ask(SYSTEM_PROMPT, payload)
    return Suggestion(
        command=data.get("command"),
        explanation=data.get("explanation", ""),
        caution=bool(data.get("caution")),
    )


def suggest_fix(error_text: str, context: dict) -> Suggestion:
    payload = f"CONTEXT:\n{json.dumps(context, indent=1)}\n\nERROR OUTPUT:\n{error_text}"
    data = _ask(FIX_PROMPT, payload)
    return Suggestion(
        command=data.get("command"),
        explanation=data.get("explanation", ""),
        caution=bool(data.get("caution")),
        diagnosis=data.get("diagnosis"),
    )
