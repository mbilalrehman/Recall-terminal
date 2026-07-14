#!/usr/bin/env bash
# Self-playing demo of Recall for recording the README GIF.
#
# It simulates a real session (typed keystrokes + Recall's actual output
# style) so the recording is deterministic and needs no API key.
#
# Record it with any of:
#   vhs demo/demo.tape                      -> demo/demo.gif  (recommended)
#   asciinema rec -c "demo/demo.sh" demo.cast
#   or just screen-record your terminal while it plays.

set -u

CYAN=$'\033[36m'; GREEN=$'\033[32m'; DIM=$'\033[2m'; BOLD=$'\033[1m'
YELLOW=$'\033[33m'; RESET=$'\033[0m'

type_cmd() {  # fake human typing at the prompt
  printf "${BOLD}\$ ${RESET}"
  local s="$1"
  for ((i = 0; i < ${#s}; i++)); do
    printf '%s' "${s:i:1}"
    sleep 0.035
  done
  sleep 0.4
  printf '\n'
}

say() { printf '%b\n' "$1"; }
pause() { sleep "${1:-1.2}"; }

clear
pause 0.6

# ── Scene 1: natural language (mixed Urdu/English) → exact command ──────────
type_cmd 'recall "woh port band kar jo meri django app use kar rahi thi"'
pause 0.9
say ""
say "  ${CYAN}Recall:${RESET} Teri Django app port 8000 pe chalti hai — history mein dekha maine."
say ""
say "  ${GREEN}${BOLD}\$ fuser -k 8000/tcp${RESET}"
printf "  Run it? [Y/n]: "
pause 1.1
say "y"
say "  ${DIM}8000/tcp: killed${RESET}"
pause 1.6
say ""

# ── Scene 2: error intelligence — learns from YOUR past fixes ───────────────
type_cmd 'recall fix "Error: Port 8000 is already in use"'
pause 0.9
say ""
say "  ${CYAN}╭─ Recall — from your history ─────────────────────────────╮${RESET}"
say "  ${CYAN}│${RESET} ${BOLD}I've seen this error before.${RESET}                             ${CYAN}│${RESET}"
say "  ${CYAN}│${RESET}                                                          ${CYAN}│${RESET}"
say "  ${CYAN}│${RESET} Fix that worked for you: ${GREEN}\$ fuser -k 8000/tcp${RESET}            ${CYAN}│${RESET}"
say "  ${CYAN}│${RESET} Confidence: ${BOLD}3/3${RESET} times it worked on your machine          ${CYAN}│${RESET}"
say "  ${CYAN}╰──────────────────────────────────────────────────────────╯${RESET}"
pause 2.2
say ""

# ── Scene 3: project memory — pick up where you left off ────────────────────
type_cmd 'recall status'
pause 0.9
say "  ${CYAN}╭─ Recall — project memory ────────────────────────────────╮${RESET}"
say "  ${CYAN}│${RESET} ${BOLD}Project:${RESET} ecommerce-api                                   ${CYAN}│${RESET}"
say "  ${CYAN}│${RESET} ${BOLD}Last activity:${RESET} 47 day(s) ago                             ${CYAN}│${RESET}"
say "  ${CYAN}│${RESET}                                                          ${CYAN}│${RESET}"
say "  ${CYAN}│${RESET} ${BOLD}Notes & decisions:${RESET}                                       ${CYAN}│${RESET}"
say "  ${CYAN}│${RESET}  • [issue] Stripe webhook failing at line 234            ${CYAN}│${RESET}"
say "  ${CYAN}│${RESET}  • [next-step] Test with Stripe CLI before deploy        ${CYAN}│${RESET}"
say "  ${CYAN}│${RESET}  • [decision] Redis for sessions — 10x faster reads      ${CYAN}│${RESET}"
say "  ${CYAN}╰──────────────────────────────────────────────────────────╯${RESET}"
pause 2.4
say ""
say "  ${YELLOW}${BOLD}Recall${RESET} — your terminal's second brain.  ${DIM}pip install recall-terminal${RESET}"
pause 2.5
