"""Console entry point for the `standards` CLI."""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Tuple

from standards.__about__ import __version__
from standards.doctor import doctor_lines
from standards.init import run_adopt, run_init
from standards.payload import payload_root
from standards.update import run_update

PROFILES = ["application", "library", "infra", "data", "documentation"]
HELP_TOPICS = ("init", "adopt", "update", "check", "doctor", "new-skill", "commands")

COMMAND_ROWS = (
    ("init", "Adopt the kit into a new or clean repo.", "standards check ."),
    ("adopt", "Adopt the kit into an existing repo without clobbering files.", "standards doctor ."),
    ("update", "Reconcile an adopted repo with this kit version.", "standards check ."),
    ("check", "Run deterministic standards checks.", "standards doctor --recommend ."),
    ("doctor", "Diagnose adoption health and suggest next commands.", "standards update --dry-run ."),
    ("new-skill", "Scaffold paired Claude/Copilot skill files.", "standards check ."),
)


def _parser_kwargs(**kwargs):
    return {"formatter_class": argparse.RawDescriptionHelpFormatter, **kwargs}


def build_parser() -> Tuple[argparse.ArgumentParser, dict[str, argparse.ArgumentParser]]:
    parser = argparse.ArgumentParser(
        prog="standards",
        description="Adopt and maintain the Repo-Standards-Kit.",
        epilog="""Workflows:
  Adopt:
    New or clean repo:     standards init --profile library .
    Existing repo:         standards adopt --profile application .

  Maintain:
    Already adopted repo:  standards update .
    Validate a repo:       standards check .

  Diagnose:
    Adoption health:       standards doctor --recommend .
    Command list:          standards commands

  Author:
    New AI skill:          standards new-skill review-docs "Review docs before shipping"

Use `standards help <command>` for command-specific examples.""",
        **_parser_kwargs(),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    parsers: dict[str, argparse.ArgumentParser] = {}

    p_init = sub.add_parser(
        "init",
        help="Adopt the kit into a new or clean target repo.",
        description="Adopt the kit into a new or clean target repo.",
        epilog="""Examples:
  standards init --profile library .
  standards init --profile documentation .
  standards init --profile application C:\\path\\to\\repo

Use `standards adopt` instead for an existing repo with local files.""",
        **_parser_kwargs(),
    )
    p_init.add_argument("target", nargs="?", default=".", help="Target repo (default: .)")
    p_init.add_argument("--profile", required=True, choices=PROFILES)
    p_init.add_argument("--force", action="store_true", help="Re-init even if already adopted.")
    parsers["init"] = p_init

    p_update = sub.add_parser(
        "update",
        help="Reconcile an already adopted repo with this kit version.",
        description="Reconcile an already adopted repo with this kit version.",
        epilog="""Examples:
  standards update .
  standards update --dry-run C:\\path\\to\\repo

Requires an existing .standards-kit.json marker.""",
        **_parser_kwargs(),
    )
    p_update.add_argument("target", nargs="?", default=".", help="Target repo (default: .)")
    p_update.add_argument("--dry-run", action="store_true",
                          help="Preview changes without writing anything.")
    parsers["update"] = p_update

    p_adopt = sub.add_parser(
        "adopt",
        help="Adopt the kit into an existing repo non-destructively.",
        description="Adopt the kit into an existing repo non-destructively.",
        epilog="""Examples:
  standards adopt --profile application .
  standards adopt --profile documentation .
  standards adopt --profile data C:\\path\\to\\repo

Keeps local files and writes <file>.kit-<version> sidecars on conflicts.""",
        **_parser_kwargs(),
    )
    p_adopt.add_argument("target", nargs="?", default=".", help="Target repo (default: .)")
    p_adopt.add_argument("--profile", required=True, choices=PROFILES)
    parsers["adopt"] = p_adopt

    p_check = sub.add_parser(
        "check",
        help="Run the standards check against a repo.",
        description="Run the standards check against a repo.",
        epilog="""Examples:
  standards check .
  standards check C:\\path\\to\\repo""",
        **_parser_kwargs(),
    )
    p_check.add_argument("target", nargs="?", default=".", help="Target repo (default: .)")
    p_check.add_argument(
        "--external-links",
        action="store_true",
        help="Opt in to networked http(s) external-link liveness checks.",
    )
    p_check.add_argument(
        "--freshness-report",
        action="store_true",
        help="Print ai/ freshness status for current-state, next-actions, and handoff.",
    )
    parsers["check"] = p_check

    p_doctor = sub.add_parser(
        "doctor",
        help="Diagnose adoption health without changing files.",
        description="Diagnose adoption health without changing files.",
        epilog="""Examples:
  standards doctor .
  standards doctor --recommend C:\\path\\to\\repo""",
        **_parser_kwargs(),
    )
    p_doctor.add_argument("target", nargs="?", default=".", help="Target repo (default: .)")
    p_doctor.add_argument(
        "--recommend",
        action="store_true",
        help="Suggest optional discovery, design, and support lanes from repo state.",
    )
    parsers["doctor"] = p_doctor

    p_new_skill = sub.add_parser(
        "new-skill",
        help="Scaffold paired Claude/Copilot skill files.",
        description="Scaffold paired Claude/Copilot skill files.",
        epilog="""Examples:
  standards new-skill review-docs "Review docs before shipping"
  standards new-skill triage-incidents "Triage support incidents" C:\\path\\to\\repo""",
        **_parser_kwargs(),
    )
    p_new_skill.add_argument("name", help="Kebab-case skill name.")
    p_new_skill.add_argument("description", help="One-line skill description.")
    p_new_skill.add_argument("target", nargs="?", default=".", help="Target repo (default: .)")
    parsers["new-skill"] = p_new_skill

    p_commands = sub.add_parser(
        "commands",
        help="List public commands with common next steps.",
        description="List public commands with common next steps.",
        **_parser_kwargs(),
    )
    parsers["commands"] = p_commands

    p_help = sub.add_parser(
        "help",
        help="Show top-level or command-specific help.",
        description="Show top-level or command-specific help.",
        epilog="Examples:\n  standards help\n  standards help init",
        **_parser_kwargs(),
    )
    p_help.add_argument("topic", nargs="?", help="Help topic: init, adopt, update, or check.")

    return parser, parsers


def main(argv: list[str] | None = None) -> int:
    parser, help_parsers = build_parser()
    args = parser.parse_args(argv)

    if args.command == "help":
        if args.topic is None:
            parser.print_help()
            return 0
        topic = args.topic
        if topic in help_parsers:
            help_parsers[topic].print_help()
            return 0
        print(
            f"error: unknown help topic {topic!r}. Valid help topics: "
            + ", ".join(HELP_TOPICS),
            file=sys.stderr,
        )
        return 2

    if args.command == "commands":
        print("Public commands:")
        for name, purpose, next_step in COMMAND_ROWS:
            print(f"  {name:<10} {purpose} Next: {next_step}")
        return 0

    if args.command == "init":
        try:
            run_init(Path(args.target), profile=args.profile,
                     adopted=date.today().isoformat(), force=args.force)
        except FileExistsError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        print(f"Adopted Repo-Standards-Kit {__version__} ({args.profile}) into {args.target}")
        return 0

    if args.command == "update":
        try:
            report = run_update(Path(args.target), dry_run=args.dry_run)
        except FileNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            print(
                "Use `standards init --profile <profile> <target>` for a new or clean repo, "
                "or `standards adopt --profile <profile> <target>` for an existing repo.",
                file=sys.stderr,
            )
            return 2
        prefix = "[dry-run] " if args.dry_run else ""
        summary = ", ".join(f"{k}={len(report[k])}" for k in
                            ("updated", "spliced", "added", "conflicts", "unchanged", "removed"))
        print(f"{prefix}standards update: {summary}")
        if report["conflicts"]:
            print("conflicts (your file kept; kit version written as <path>.kit-"
                  f"{__version__}): " + ", ".join(report["conflicts"]), file=sys.stderr)
        print("Run `python scripts/standards-check/check.py` to re-verify.")
        return 0

    if args.command == "adopt":
        try:
            report = run_adopt(Path(args.target), profile=args.profile,
                               adopted=date.today().isoformat())
        except FileExistsError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        summary = ", ".join(f"{k}={len(report[k])}" for k in
                            ("added", "spliced", "unchanged", "conflicts", "scaffolded"))
        print(f"Adopted Repo-Standards-Kit {__version__} ({args.profile}) into "
              f"{args.target}: {summary}")
        if report["conflicts"]:
            print("conflicts (your file kept; kit version written as <path>.kit-"
                  f"{__version__}): " + ", ".join(report["conflicts"]), file=sys.stderr)
        print("Run `standards check` to verify.")
        return 0

    if args.command == "check":
        # The check modules ship as payload data (not importable from the wheel),
        # so locate the bundled check.py and run it against the target. It detects
        # the repo root from the target and honors the target's severity overrides
        # (ADR-0011).
        check_py = payload_root() / "scripts" / "standards-check" / "check.py"
        if not check_py.is_file():
            print(f"error: bundled check not found at {check_py}", file=sys.stderr)
            return 2
        cmd = [sys.executable, str(check_py)]
        if args.external_links:
            cmd.append("--external-links")
        if args.freshness_report:
            cmd.append("--freshness-report")
        cmd.append(str(args.target))
        return subprocess.run(cmd).returncode

    if args.command == "doctor":
        code, lines = doctor_lines(Path(args.target), recommend=args.recommend)
        for line in lines:
            print(line)
        return code

    if args.command == "new-skill":
        script = payload_root() / "scripts" / "new-doc" / "new-skill.py"
        if not script.is_file():
            print(f"error: bundled new-skill script not found at {script}", file=sys.stderr)
            return 2
        try:
            return subprocess.run(
                [sys.executable, str(script), args.name, args.description],
                cwd=str(Path(args.target)),
            ).returncode
        except OSError as exc:
            print(f"error: could not run new-skill in {args.target}: {exc}", file=sys.stderr)
            return 2

    return 1


if __name__ == "__main__":
    sys.exit(main())
