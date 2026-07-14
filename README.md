# Recall

**The AI brain for your terminal.** It remembers everything, understands your context, and thinks ahead of you.

Every developer loses 30–60 minutes a day to the same loop: stop work → open Google/ChatGPT → re-explain your context → copy a command back → hope it's right. Recall kills that loop. It lives **inside** your terminal, knows **your** history, **your** projects, and **your** past fixes — and answers in English, Urdu, or both.

```
$ recall "kill the port my django app is using"

  Recall: Your Django app runs on port 8000 (I've seen it in your history).

  $ fuser -k 8000/tcp
  Run it? [y/n]
```

<!-- Generate the demo GIF with `vhs demo/demo.tape`, then uncomment: -->
<!-- ![Recall demo](demo/demo.gif) -->

## What it does today (v0.1 — Phase 1 MVP)

| Feature | Command |
|---|---|
| Natural language → exact command, with your context | `recall "your request"` |
| Error diagnosis — checks fixes that worked for *you* first | `recall fix "<error output>"` |
| Project memory — notes, decisions, open issues per project | `recall note "..."` / `recall status` |
| Personal command history, searchable | `recall history docker` |
| Repeatable workflows | `recall workflow save pre-commit "pytest" "flake8 ."` |
| Automatic history capture (zsh/bash hook) | `recall init` |

## Install

```bash
pip install -e .
recall config set api_key sk-ant-...   # or export ANTHROPIC_API_KEY
recall init                             # start capturing history (local only)
```

## Privacy

Everything stays on your machine in `~/.recall/recall.db`. Nothing is uploaded. The only network call is to the Claude API when you explicitly ask a question — and only your recent command history + project notes are sent as context.

## Roadmap

- **Phase 1 (now)** — CLI: ask, fix, memory, workflows ✅
- **Phase 2** — Semantic memory (vector search), auto context on `cd`, passive error detection
- **Phase 3** — Workflow pattern detection ("you always run these 3 commands before commit — automate?")
- **Phase 4** — **Team Recall**: shared team brain, onboarding in days not weeks, analytics dashboard

See [`docs/STRATEGY.md`](docs/STRATEGY.md) for the full product & business plan.

## License

MIT
