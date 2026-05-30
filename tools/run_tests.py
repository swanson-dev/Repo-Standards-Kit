#!/usr/bin/env python3
"""Run every kit test suite in its own subprocess and aggregate pass/fail.

Each test file is a standalone stdlib `unittest` module (it has a `__main__`
guard and inserts its own import paths), so we execute the files as subprocesses
rather than relying on `unittest`/`pytest` discovery — which collides on the
duplicate `test_cli.py` basename across `tests/` and `scripts/new-doc/`. No
third-party dependency; runs identically on GitHub Actions, an ADO pipeline, or
locally on Windows.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def discover(root: Path) -> list[Path]:
    """Return every test file: tests/test_*.py + scripts/**/test_*.py, sorted."""
    root = Path(root)
    return sorted(root.glob("tests/test_*.py")) + sorted(root.glob("scripts/**/test_*.py"))


def run(paths: list[Path]) -> int:
    """Run each test file in a subprocess. Return 1 if any fail, else 0."""
    failed: list[str] = []
    for tf in paths:
        result = subprocess.run([sys.executable, str(Path(tf))])
        ok = result.returncode == 0
        print(f"{'OK  ' if ok else 'FAIL'}  {Path(tf).as_posix()}")
        if not ok:
            failed.append(str(tf))
    print(f"\n{len(paths) - len(failed)}/{len(paths)} suites passed.")
    return 1 if failed else 0


def main() -> int:
    return run(discover(REPO_ROOT))


if __name__ == "__main__":
    sys.exit(main())
