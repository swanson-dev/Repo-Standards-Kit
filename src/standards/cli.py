"""Console entry point for the `standards` CLI."""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from standards.__about__ import __version__
from standards.init import run_init

PROFILES = ["application", "library", "infra", "data"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="standards",
                                     description="Adopt and maintain the Repo-Standards-Kit.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Adopt the kit into a target repo.")
    p_init.add_argument("target", nargs="?", default=".", help="Target repo (default: .)")
    p_init.add_argument("--profile", required=True, choices=PROFILES)
    p_init.add_argument("--force", action="store_true", help="Re-init even if already adopted.")

    args = parser.parse_args(argv)

    if args.command == "init":
        try:
            run_init(Path(args.target), profile=args.profile,
                     adopted=date.today().isoformat(), force=args.force)
        except FileExistsError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        print(f"Adopted Repo-Standards-Kit {__version__} ({args.profile}) into {args.target}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
