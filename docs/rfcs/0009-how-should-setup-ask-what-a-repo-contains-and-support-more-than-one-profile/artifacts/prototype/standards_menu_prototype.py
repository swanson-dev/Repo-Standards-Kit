"""PROTOTYPE of RFC-0009's menu and setup wizard. Throwaway; nothing is written.

Question: does a state-aware menu plus "What does this repo contain?" make
setting up the kit easy without knowing commands, flags, or profile names, and
do combined profiles produce sensible requirements? See NOTES.md.

Run from the repo root (the repo argument is only read, never written):
    python docs/rfcs/0009-how-should-setup-ask-what-a-repo-contains-and-support-more-than-one-profile/artifacts/prototype/standards_menu_prototype.py [repo] [--as new|adopted|behind]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import setup_logic as logic

KIT_VERSION = "1.4.0"  # pretend installed kit version
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__",
             ".mypy_cache", ".ruff_cache", ".pytest_cache", ".claude", ".archify"}
BOLD, DIM, RESET = "\x1b[1m", "\x1b[2m", "\x1b[0m"


def scan(root: Path) -> list[str]:
    """Relative POSIX paths under root. Read-only."""
    paths: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel = Path(dirpath).relative_to(root).as_posix()
        paths += [name if rel == "." else f"{rel}/{name}" for name in filenames]
    return paths


def initial_state(root: Path, mode: str | None) -> dict:
    marker_file = root / ".standards-kit.json"
    data = json.loads(marker_file.read_text(encoding="utf-8")) if marker_file.is_file() else None
    paths = scan(root)
    state = {
        "repo": str(root.resolve()),
        "adopted": data is not None,
        "repo_version": data.get("kit_version") if data else None,
        "profiles": (data.get("profiles") or [data["profile"]]) if data else [],
        "paths": paths,
        "existing": {p for p in paths if p.startswith("docs/")},
        "message": "",
    }
    if mode == "new":
        state.update(adopted=False, repo_version=None, profiles=[])
    elif mode in ("adopted", "behind"):
        state.update(adopted=True, profiles=state["profiles"] or ["application"],
                     repo_version=KIT_VERSION if mode == "adopted" else "1.2.0")
    return state


def ask(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        return "q"


def frame(state: dict, title: str, body: list[str], keys: list[tuple[str, str]]) -> None:
    """Clear the screen and draw: repo state, the screen's content, then its keys."""
    print("\x1b[2J\x1b[H", end="")
    print(f"{BOLD}Repo-Standards-Kit {KIT_VERSION}{RESET} "
          f"{DIM}| {state['repo']} | PROTOTYPE, nothing is written{RESET}")
    if state["adopted"]:
        repo = f"set up at kit {state['repo_version']} as {' + '.join(state['profiles'])}"
    else:
        repo = "not set up yet"
    print(f"{BOLD}This repo:{RESET} {repo}")
    if state["message"]:
        print(f"{DIM}{state['message']}{RESET}")
        state["message"] = ""
    print(f"\n{BOLD}{title}{RESET}")
    for line in body:
        print(line)
    print("\n" + "  ".join(f"{BOLD}[{key}]{RESET} {DIM}{label}{RESET}" for key, label in keys))


def main_menu(state: dict) -> str:
    behind = state["adopted"] and state["repo_version"] != KIT_VERSION
    items = logic.menu(state["adopted"], behind)
    body = [f"  {i}) {label}" + ("   <- recommended" if rec else "")
            for i, (_, label, rec) in enumerate(items, 1)]
    frame(state, "What do you want to do?", body, [(f"1-{len(items)}", "choose"), ("q", "quit")])
    answer = ask("> ").strip().lower()
    if answer == "q":
        return "quit"
    if answer.isdigit() and 1 <= int(answer) <= len(items):
        return items[int(answer) - 1][0]
    state["message"] = f"'{answer}' isn't a choice."
    return "menu"


def wizard(state: dict, current: list[str]) -> list[str] | None:
    suggestions = logic.suggest(state["paths"])
    default = current or list(suggestions) or [logic.DOCS_ONLY]
    default_text = ",".join(
        "0" if p == logic.DOCS_ONLY else str(logic.CHOICES.index(p) + 1) for p in default
    )
    while True:
        body = [f"  {i}) {name:<12} {DIM}{desc}{RESET}"
                for i, (name, desc) in enumerate(logic.PROFILES.items(), 1)]
        body.append(f"  0) {'docs only':<12} {DIM}documentation whose code lives elsewhere{RESET}")
        if suggestions:
            nums = ", ".join(str(logic.CHOICES.index(p) + 1) for p in suggestions)
            why = ", ".join(f for files in suggestions.values() for f in files)
            body.append(f"\n  Suggested from this repo: {nums}   {DIM}({why}){RESET}")
        frame(state, "What does this repo contain? (pick any, comma-separated)", body,
              [("Enter", "accept the default in brackets"), ("b", "back")])
        answer = ask(f"> [{default_text}] ").strip().lower()
        if answer in ("b", "q"):
            return None
        try:
            return logic.parse_picks(answer, default)
        except ValueError as exc:
            state["message"] = str(exc)


def confirm(state: dict, profiles: list[str], previous: list[str] | None) -> bool:
    plan = logic.plan_setup(profiles, state["existing"])
    body = [f"  {BOLD}Contains:{RESET}  {' + '.join(profiles)}",
            f"  {BOLD}Checklist:{RESET} {logic.checklist_header(profiles)}",
            f"  {BOLD}Marker:{RESET}    {json.dumps(logic.marker(profiles, KIT_VERSION))}"]
    if previous:
        changes = logic.requirement_changes(previous, profiles)
        body.append(f"  {BOLD}Changes from {' + '.join(previous)}:{RESET}")
        body += [f"    {doc}: {old} -> {new}" for doc, old, new in changes] or ["    (none)"]
    body.append(f"  {BOLD}Docs to create from templates and tick:{RESET}")
    body += [f"    + docs/{doc} {DIM}({plan['tiers'][doc]}){RESET}" for doc in plan["create"]] \
        or ["    (none)"]
    if plan["keep"]:
        body.append(f"  {BOLD}Already there, kept as is:{RESET} " + ", ".join(plan["keep"]))
    if plan["extras"]:
        body.append(f"  {BOLD}Profile extras to add:{RESET} " + ", ".join(plan["extras"]))
    frame(state, "Here's what setup would do", body, [("y", "do it (simulated)"), ("b", "back")])
    return ask("> ").strip().lower() == "y"


def run(state: dict) -> None:
    while True:
        action = main_menu(state)
        if action == "quit":
            return
        if action in ("setup", "change"):
            previous = state["profiles"] if action == "change" else None
            profiles = wizard(state, state["profiles"])
            if profiles and confirm(state, profiles, previous):
                plan = logic.plan_setup(profiles, state["existing"])
                state["existing"] |= {f"docs/{doc}" for doc in plan["create"]}
                state.update(adopted=True, profiles=profiles, repo_version=KIT_VERSION)
                state["message"] = (f"Simulated: would write the marker, the checklist, and "
                                    f"{len(plan['create'])} docs. Nothing was written.")
        elif action == "check":
            behind = state["adopted"] and state["repo_version"] != KIT_VERSION
            offer = f", then offer an update ({state['repo_version']} -> {KIT_VERSION})" if behind else ""
            state["message"] = f"Would run `standards check .` and `standards doctor .`{offer}."
        elif action == "update":
            state["message"] = f"Would run `standards update .` ({state['repo_version']} -> {KIT_VERSION})."
            state["repo_version"] = KIT_VERSION
        elif action == "skill":
            state["message"] = ("Would ask for a name and a one-line description, then run "
                                '`standards new-skill NAME "DESCRIPTION"`.')


def main() -> int:
    parser = argparse.ArgumentParser(
        description="PROTOTYPE of RFC-0009's menu and setup wizard. Nothing is written.")
    parser.add_argument("repo", nargs="?", default=".", help="repo to read (default: .)")
    parser.add_argument("--as", dest="mode", choices=["new", "adopted", "behind"],
                        help="pretend the repo is in this state")
    parser.add_argument("--assume-tty", action="store_true",
                        help="show the menu even without a terminal (for scripted runs)")
    args = parser.parse_args()
    if not sys.stdin.isatty() and not args.assume_tty:
        print("No interactive terminal, so no menu. The real `standards` prints its help here "
              "and exits 2, so CI and pipes never hang.")
        return 2
    sys.stdout.reconfigure(errors="replace")  # type: ignore[attr-defined]
    run(initial_state(Path(args.repo), args.mode))
    return 0


if __name__ == "__main__":
    sys.exit(main())
