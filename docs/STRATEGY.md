# Recall — Product & Business Strategy

*From zero to a brand every developer needs. Working plan, updated July 2026.*

---

## 1. Positioning (the one sentence that sells)

> **Recall is the memory layer for developers — the AI in your terminal that never forgets.**

Don't position against Google or ChatGPT ("another AI tool"). Position against **forgetting**:
Cursor forgets. Copilot forgets. ChatGPT forgets. Your terminal history forgets your *context*. Recall is the only tool whose entire job is to remember.

**Tagline candidates:** "Your terminal's second brain." / "Never explain your context twice." / "It remembers, so you don't have to."

## 2. Who buys, and in what order

| Stage | User | Why they come | What they pay |
|---|---|---|---|
| 1 | Solo devs, students, indie hackers | Command lookup + error fixes without leaving terminal | Free (growth engine) |
| 2 | Power users / freelancers with many projects | Project memory across context switches | Pro $12/mo |
| 3 | Startups & agencies (5–20 devs) | Onboarding in days, tribal knowledge captured | Team $49/mo |
| 4 | Enterprise (later) | Knowledge retention when devs leave, compliance | Custom |

The free tier is not charity — it's distribution. Terminal tools spread dev-to-dev; every free user demoing `recall fix` at a screen-share is your marketing team.

## 3. Business model

- **Free** — unlimited local memory, N AI queries/day (metered, because Claude API costs are per-query). Local-first = near-zero infra cost per free user.
- **Pro $12/mo** — unlimited AI queries, cross-device sync, full error intelligence, workflow automation.
- **Team $49/mo (up to 20 devs)** — Team Recall shared brain, analytics dashboard, knowledge-decay alerts. **This is where the real revenue is**: one team = 4 Pro users' revenue, and teams don't churn (their knowledge lives inside the product — the moat is the data).

**Unit economics rule:** free-tier query cap must keep average API cost per free user under ~$0.50/mo. Use a cheap/fast model (Haiku-class) for free-tier queries, the strongest model for Pro.

## 4. Moat — why this becomes "need of every user"

1. **Data gravity**: every day of use makes Recall smarter about *you*. Switching cost grows daily.
2. **Team knowledge lock-in**: once a team's tribal knowledge lives in Team Recall, leaving means losing the brain.
3. **Local-first trust**: history stays on-device; competitors that upload everything can't match the privacy story.
4. **Language edge**: first-class Urdu/Hindi/mixed-language support — 1M+ developers in Pakistan/India that Warp and Copilot treat as an afterthought. Own that market first, expand out.

## 5. Go-to-market playbook (in order)

**Months 1–2 — Prove it (50 users)**
- Ship Phase 1 MVP (this repo). Give it to 50 devs you can talk to directly: university friends, local dev communities, Discord/WhatsApp groups.
- Weekly calls. One metric: **do they use it again tomorrow?** (D1/D7 retention). Fix until yes.

**Months 3–4 — Public launch**
- Open-source the CLI core on GitHub (MIT). Open-core: CLI free forever, sync + team = paid. GitHub stars are the dev-tool credibility currency.
- Launches: Hacker News "Show HN", Product Hunt, r/commandline, r/programming, dev.to, X/Twitter build-in-public thread.
- The demo GIF is the product: 15 seconds of `recall "urdu/english query"` → perfect command. Make it the top of the README.

**Months 5–6 — First revenue**
- Turn on Pro ($12/mo) via Stripe. Convert power users (people hitting the free query cap — they're pre-qualified).
- Content engine: every interesting error Recall fixes = a short post/tweet. SEO for "how to fix <error>" queries brings devs who then meet Recall.

**Months 7–12 — Team Recall**
- Build sync backend (FastAPI + Postgres) + team dashboard.
- Sell manually first: 10 design-partner teams at 50% off in exchange for feedback and case studies ("onboarding went from 4 weeks to 3 days" is the headline).
- Case studies → outbound to agencies and startups.

## 6. Brand

- **Name**: Recall. Keep it. Short, means the thing it does.
- **Voice**: talks like a sharp teammate, not a corporate tool. The Urdu/English mixed voice in the product is a *feature* and a differentiator — keep it in marketing for the South Asia market, English-first for global.
- **Build in public**: weekly progress threads, revenue transparency, user stories. Founder brand = product brand at this stage.
- **Visual**: terminal-native aesthetic. Dark, monospace, the `Recall:` prompt as the recognizable mark.

## 7. Metrics that matter (ignore the rest)

| Phase | North-star metric | Target |
|---|---|---|
| MVP | D7 retention of the 50 pilots | > 40% |
| Launch | Weekly active devs | 1,000 in 3 months |
| Pro | Free → Pro conversion | > 3% |
| Team | Team accounts, net revenue retention | 10 teams, NRR > 100% |

## 8. Honest risks & answers

- **"Warp/Copilot adds memory"** → They're editor/UI companies; memory is your *only* job. Move fast, own the personal-data moat, own the Urdu/Hindi market they won't prioritize.
- **API costs eat margin** → Meter free tier, route to cheap models, cache repeated queries locally.
- **Privacy fear ("it reads my terminal")** → Local-first by default, open-source the capture code, auto-redact secrets before anything reaches the API. Say this loudly and first.
- **Solo founder burnout** → Phase discipline: do NOT start Team Recall before Pro has paying users. One phase at a time.

## 9. Next 14 days (do these, nothing else)

1. ~~First commit: working CLI MVP~~ ✅ (this repo)
2. Add secret redaction to the context builder (never send tokens/keys to the API).
3. Record the 15-second demo GIF; put it in the README.
4. Publish to PyPI (`pip install recall-terminal`).
5. Get it into the hands of 10 developers you know. Watch them use it. Write down every point of friction.
