"""The bare `standards` menu and setup wizard (ADR-0025, RFC-0009).

The menu reads the repo's state, asks what it contains, and ends every action in
a real CLI call (`adopt`, `change`, `check`, `doctor`, `update`, `new-skill`)
through `run`, so the terminal menu and the flags can't drift apart. Plain text
only: no screen clearing or colors, so it reads the same in any console or log.
"""
from __future__ import annotations

import os
import re
import shutil
from fnmatch import fnmatch
from pathlib import Path
from typing import Callable

from standards.__about__ import __version__
from standards.manifest import AGENTS, hook_file
from standards.marker import read_marker
from standards.profiles import DOCS_ONLY, EXTRAS, MATRIX, PROFILES, combine, needed_docs

# Wizard choices 1-3, in this order; documentation only is choice 0 and stands alone.
CHOICES = [p for p in PROFILES if p != DOCS_ONLY]
DESCRIPTIONS = {
    "application": "an app, service, or IaC",
    "library": "a reusable package others import",
    "data": "pipelines, models, data contracts",
}
AGENT_DESCRIPTIONS = {"claude": "Claude Code", "copilot": "GitHub Copilot (VS Code, CLI, cloud agent)"}

# ponytail: rough file signals that only suggest; the user confirms every answer.
# A pattern ending in "/" matches a folder anywhere; anything else matches a file name.
SIGNALS = {
    "application": ["Dockerfile", "docker-compose.yml", "compose.yaml", "manage.py",
                    "next.config.*", "vite.config.*", "Program.cs", "Procfile",
                    "*.tf", "*.bicep", "Pulumi.yaml", "cdk.json", "Chart.yaml",
                    "kustomization.yaml"],
    "library": ["pyproject.toml", "setup.py", "Cargo.toml", "*.csproj", "package.json"],
    "data": ["dbt_project.yml", "dags/", "*.ipynb"],
}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__",
             ".mypy_cache", ".ruff_cache", ".pytest_cache", ".claude", ".tox"}

Ask = Callable[[str], str]
Out = Callable[[str], None]
Run = Callable[[list], int]


def detect_agents() -> list[str]:
    """Suggest `agents` from this machine. Finding neither assumes both, which ships
    Claude's hook file: every host reads it."""
    home = Path.home()
    # ponytail: PATH and home-folder sniffing; a Copilot user with none of these is missed
    found = []
    if shutil.which("claude") or (home / ".claude").is_dir():
        found.append("claude")
    if (shutil.which("copilot") or (home / ".copilot").is_dir()
            or any((home / ".vscode" / "extensions").glob("github.copilot*"))):
        found.append("copilot")
    return found or list(AGENTS)


def scan(root: Path) -> list[str]:
    """Relative POSIX paths of the repo's files, skipping tool and dependency folders."""
    paths: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel = Path(dirpath).relative_to(root).as_posix()
        paths += [name if rel == "." else f"{rel}/{name}" for name in filenames]
    return paths


def suggest(paths: list[str]) -> dict[str, list[str]]:
    """Profile -> up to two of the files that suggested it."""
    found: dict[str, list[str]] = {name: [] for name in SIGNALS}
    for path in paths:
        name = path.rsplit("/", 1)[-1]
        for profile, patterns in SIGNALS.items():
            hit = any(
                (path.startswith(p) or f"/{p}" in path) if p.endswith("/") else fnmatch(name, p)
                for p in patterns
            )
            if hit and len(found[profile]) < 2:
                found[profile].append(path)
    if found["application"]:
        found["library"] = []  # apps carry packaging manifests too
    return {profile: files for profile, files in found.items() if files}


def _numbers(answer: str, names: list[str]) -> list[str]:
    """'1,3' -> names[0], names[2], in order, without repeats. Raises ValueError."""
    numbered = {str(i): name for i, name in enumerate(names, 1)}  # exact strings: "²" isn't 2
    picks: list[str] = []
    for part in answer.replace(" ", "").split(","):
        if part not in numbered:
            raise ValueError(f"'{part}' isn't a choice. Use 1-{len(names)}, comma-separated.")
        if numbered[part] not in picks:
            picks.append(numbered[part])
    return picks


def is_behind(recorded: object, installed: str) -> bool:
    """True only when the repo's kit version is older than the installed one. A newer
    repo would be downgraded by an update, and an unreadable version is never "behind"."""
    def parts(version: object) -> list[int] | None:
        if not isinstance(version, str) or not re.fullmatch(r"\d+(\.\d+)*", version):
            return None
        return [int(p) for p in version.split(".")]

    old, new = parts(recorded), parts(installed)
    if old is None or new is None:
        return False
    width = max(len(old), len(new))
    return old + [0] * (width - len(old)) < new + [0] * (width - len(new))


def parse_picks(answer: str, default: list[str]) -> list[str]:
    """'1,3' -> profiles, '' -> default, '0' -> documentation only. Raises ValueError."""
    answer = answer.strip()
    if not answer:
        return default
    if "0" in answer.replace(" ", "").split(","):
        if answer.replace(" ", "") != "0":
            raise ValueError("Documentation only can't be combined with other kinds.")
        return [DOCS_ONLY]
    return _numbers(answer, CHOICES)


def _number_text(names: list[str], options: list[str]) -> str:
    return ",".join("0" if n == DOCS_ONLY else str(options.index(n) + 1) for n in names)


def menu_items(adopted: bool, behind: bool) -> list[tuple[str, str, bool]]:
    """(action, label, recommended) for the repo's state. Update shows only when behind."""
    if not adopted:
        return [("setup", "Set up this repo", True),
                ("check", "Check / fix this repo", False),
                ("skill", "Create an AI skill", False)]
    items = [("check", "Check / fix this repo", False)]
    if behind:
        items.append(("update", "Update to the installed kit version", True))
    return items + [("change", "Change what this repo contains", False),
                    ("skill", "Create an AI skill", False)]


def requirement_changes(old: list[str], new: list[str]) -> list[tuple[str, str, str]]:
    """(doc, old tier, new tier) for every numbered doc whose tier changes."""
    before, after = combine(old), combine(new)
    return [(doc, before[doc], after[doc]) for doc in MATRIX if before[doc] != after[doc]]


def run_menu(target: Path, *, run: Run, ask: Ask = input, out: Out = print) -> int:
    """The interactive menu. Returns 0 when the user quits or input ends."""
    try:
        _loop(Path(target), run, ask, out)
    except EOFError:
        out("")
    return 0


def _loop(target: Path, run: Run, ask: Ask, out: Out) -> None:
    message = ""
    while True:
        marker = read_marker(target)
        behind = marker is not None and is_behind(marker.get("kit_version"), __version__)
        out(f"\nRepo-Standards-Kit {__version__} | {target.resolve()}")
        if marker is None:
            out("This repo: not set up yet")
        else:
            out(f"This repo: set up at kit {marker.get('kit_version')} as "
                f"{' + '.join(marker.get('profiles', []))}")
        if message:
            out(message)
            message = ""
        items = menu_items(marker is not None, behind)
        out("\nWhat do you want to do?")
        for i, (_action, label, recommended) in enumerate(items, 1):
            out(f"  {i}) {label}" + ("   <- recommended" if recommended else ""))
        out(f"[1-{len(items)}] choose  [q] quit")
        answer = ask("> ").strip().lower()
        if answer == "q":
            return
        actions = {str(i): action for i, (action, _label, _rec) in enumerate(items, 1)}
        if answer not in actions:
            message = f"'{answer}' isn't a choice."
            continue
        try:
            code = _act(actions[answer], target, marker, behind, run, ask, out)
        except SystemExit as exc:  # argparse exits on a bad argument; stay in the menu
            code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
        if code:
            message = f"The last step exited with code {code}; see its output above."


def _act(action: str, target: Path, marker: dict | None, behind: bool,
         run: Run, ask: Ask, out: Out) -> int:
    where = str(target)
    if action in ("setup", "change"):
        current = list(marker.get("profiles", [])) if marker else []
        profiles = _ask_profiles(target, current, ask, out)
        if profiles is None:
            return 0
        if action == "change":
            if not _confirm_change(target, current, profiles, ask, out):
                return 0
            return run(["change", "--profile", ",".join(profiles), where])
        agents = _ask_agents(ask, out)
        if agents is None or not _confirm_setup(target, profiles, agents, ask, out):
            return 0
        return run(["adopt", "--profile", ",".join(profiles), "--agents", ",".join(agents),
                    where])
    if action == "check":
        codes = [run(["check", where]), run(["doctor", where])]  # doctor runs even on findings
        code = next((c for c in codes if c), 0)
        if behind and ask("Update to the installed kit version now? [y/N] ").strip().lower() == "y":
            updated = run(["update", where])
            return code or updated  # updating doesn't fix what check found
        return code
    if action == "update":
        return run(["update", where])
    name = ask("Skill name (kebab-case; Enter to go back): ").strip()
    if not name:
        return 0
    # `--` keeps answers such as "--help" from being read as flags.
    return run(["new-skill", "--", name, ask("One-line description: ").strip(), where])


def _ask_profiles(target: Path, current: list[str], ask: Ask, out: Out) -> list[str] | None:
    suggestions = suggest(scan(target))
    default = current or list(suggestions) or [DOCS_ONLY]
    while True:
        out("\nWhat does this repo contain? (pick any, comma-separated)")
        for i, name in enumerate(CHOICES, 1):
            out(f"  {i}) {name:<12} {DESCRIPTIONS[name]}")
        out(f"  0) {'docs only':<12} documentation whose code lives elsewhere")
        if suggestions:
            why = ", ".join(f for files in suggestions.values() for f in files)
            out(f"\n  Suggested from this repo: {_number_text(list(suggestions), CHOICES)}   ({why})")
        out("[Enter] accept the default in brackets  [b] back")
        answer = ask(f"> [{_number_text(default, CHOICES)}] ").strip().lower()
        if answer == "b":
            return None
        try:
            return parse_picks(answer, default)
        except ValueError as exc:
            out(str(exc))


def _ask_agents(ask: Ask, out: Out) -> list[str] | None:
    default = detect_agents()
    names = list(AGENTS)
    while True:
        out("\nWhich agents does the team use? (pick any, comma-separated)")
        for i, name in enumerate(names, 1):
            out(f"  {i}) {name:<8} {AGENT_DESCRIPTIONS[name]}")
        out(f"\n  Suggested from this machine: {_number_text(default, names)}")
        out("[Enter] accept the default in brackets  [b] back")
        answer = ask(f"> [{_number_text(default, names)}] ").strip().lower()
        if answer == "b":
            return None
        if not answer:
            return default
        try:
            picks = _numbers(answer, names)
        except ValueError as exc:
            out(str(exc))
            continue
        return [name for name in names if name in picks]


def _plan_lines(target: Path, profiles: list[str]) -> list[str]:
    tiers = combine(profiles)
    required, expected = needed_docs(profiles)
    wanted = sorted(required + expected)
    create = [doc for doc in wanted if not (target / "docs" / doc).exists()]
    keep = [doc for doc in wanted if (target / "docs" / doc).exists()]
    lines = ["  Docs to create from templates and tick:"]
    lines += [f"    + docs/{doc} ({tiers[doc]})" for doc in create] or ["    (none)"]
    if keep:
        lines.append("  Already there, kept as is: " + ", ".join(f"docs/{d}" for d in keep))
    extras = [EXTRAS[p] for p in profiles if not (target / EXTRAS[p]).exists()]
    if extras:
        lines.append("  Profile extras to add yourself: " + ", ".join(extras))
    return lines


def _confirm(lines: list[str], ask: Ask, out: Out) -> bool:
    for line in lines:
        out(line)
    out("[y] do it  [b] back")
    return ask("> ").strip().lower() == "y"


def _confirm_setup(target: Path, profiles: list[str], agents: list[str],
                   ask: Ask, out: Out) -> bool:
    return _confirm(["\nHere's what setup will do",
                     f"  Contains:   {' + '.join(profiles)}",
                     f"  Agents:     {', '.join(agents)} (hooks in {hook_file(agents)})",
                     *_plan_lines(target, profiles)], ask, out)


def _confirm_change(target: Path, old: list[str], new: list[str], ask: Ask, out: Out) -> bool:
    changes = requirement_changes(old, new)
    return _confirm(["\nHere's what the change will do",
                     f"  Contains:   {' + '.join(new)} (was {' + '.join(old)})",
                     "  Requirement changes:",
                     *([f"    {doc}: {a} -> {b}" for doc, a, b in changes] or ["    (none)"]),
                     *_plan_lines(target, new)], ask, out)
