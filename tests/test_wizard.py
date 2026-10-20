"""The bare `standards` menu and setup wizard (ADR-0025), driven with scripted answers."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def drive(target: Path, answers: list[str], codes: dict | None = None):
    """Run the menu with these answers; stop at the first prompt past them. `codes`
    maps a command to its exit code, or to an exception the fake run raises."""
    from standards.wizard import run_menu
    calls: list[list[str]] = []
    lines: list[str] = []
    pending = iter(answers)

    def ask(prompt: str) -> str:
        lines.append(prompt)
        try:
            return next(pending)
        except StopIteration:
            raise EOFError from None

    def run(argv: list[str]) -> int:
        calls.append(argv)
        result = (codes or {}).get(argv[0], 0)
        if isinstance(result, BaseException):
            raise result
        return result

    code = run_menu(target, run=run, ask=ask, out=lines.append)
    return code, calls, "\n".join(lines)


def adopted(target: Path, profile: str = "library", kit_version: str | None = None) -> None:
    from standards.init import run_init
    from standards.marker import MARKER_NAME
    run_init(target, profile=profile, adopted="2026-10-20", agents=["claude"])
    if kit_version:
        path = target / MARKER_NAME
        data = json.loads(path.read_text(encoding="utf-8"))
        data["kit_version"] = kit_version
        path.write_text(json.dumps(data), encoding="utf-8")


class SuggestTests(unittest.TestCase):
    def test_file_signals_suggest_profiles(self):
        from standards.wizard import suggest
        self.assertEqual(list(suggest(["Dockerfile", "infra/main.tf"])), ["application"])
        self.assertEqual(list(suggest(["pyproject.toml"])), ["library"])
        self.assertEqual(list(suggest(["dbt_project.yml", "dags/load.py"])), ["data"])
        # Apps carry packaging manifests too, so an app isn't also called a library.
        self.assertEqual(list(suggest(["Dockerfile", "package.json"])), ["application"])
        self.assertEqual(suggest(["README.md"]), {})

    def test_scan_skips_tool_and_dependency_folders(self):
        from standards.wizard import scan
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for rel in ("Dockerfile", "node_modules/x/package.json", ".git/HEAD", "src/app.py"):
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text("x", encoding="utf-8")
            self.assertEqual(sorted(scan(root)), ["Dockerfile", "src/app.py"])


class ParsePicksTests(unittest.TestCase):
    def test_numbers_pick_profiles_and_enter_takes_the_default(self):
        from standards.wizard import parse_picks
        self.assertEqual(parse_picks("1,3", ["library"]), ["application", "data"])
        self.assertEqual(parse_picks(" 3 , 1 ", ["library"]), ["data", "application"])
        self.assertEqual(parse_picks("", ["library"]), ["library"])
        self.assertEqual(parse_picks("0", ["library"]), ["documentation"])

    def test_bad_answers_say_why(self):
        from standards.wizard import parse_picks
        for bad in ("0,1", "4", "x", "1,,x", "²", "99999999999999999999999"):
            with self.subTest(answer=bad), self.assertRaises(ValueError):
                parse_picks(bad, ["library"])


class MenuItemsTests(unittest.TestCase):
    def test_items_follow_the_repo_state(self):
        from standards.wizard import menu_items
        new = menu_items(adopted=False, behind=False)
        self.assertEqual([action for action, _label, _rec in new], ["setup", "check", "skill"])
        self.assertTrue(new[0][2])  # set up is recommended
        current = menu_items(adopted=True, behind=False)
        self.assertEqual([a for a, _l, _r in current], ["check", "change", "skill"])
        self.assertFalse(any(rec for _a, _l, rec in current))
        behind = menu_items(adopted=True, behind=True)
        self.assertEqual([a for a, _l, _r in behind], ["check", "update", "change", "skill"])
        self.assertTrue(behind[1][2])  # update is recommended


class RequirementChangesTests(unittest.TestCase):
    def test_lists_only_the_tiers_that_move(self):
        from standards.wizard import requirement_changes
        changes = requirement_changes(["library"], ["library", "data"])
        self.assertIn(("06-runbook.md", "N/A", "Required"), changes)
        self.assertNotIn("04-api-and-integrations.md", [doc for doc, _old, _new in changes])


class RunMenuTests(unittest.TestCase):
    def test_a_new_repo_is_set_up_through_adopt(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            (target / "Dockerfile").write_text("FROM python\n", encoding="utf-8")
            code, calls, text = drive(target, ["1", "", "1", "y"])
            self.assertEqual(code, 0)
            self.assertEqual(calls, [["adopt", "--profile", "application", "--agents", "claude",
                                      str(target)]])
            self.assertIn("not set up yet", text)
            self.assertIn("<- recommended", text)
            self.assertIn("Suggested from this repo: 1", text)
            self.assertIn("docs/06-runbook.md", text)  # the summary lists the docs to create
            self.assertIn(".claude/settings.json", text)  # and the hook file

    def test_documentation_only_cant_be_combined(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _code, calls, text = drive(target, ["1", "0,1", "0", "2", "y"])
            self.assertIn("can't be combined", text)
            self.assertEqual(calls, [["adopt", "--profile", "documentation", "--agents", "copilot",
                                      str(target)]])

    def test_back_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _code, calls, _text = drive(target, ["1", "1", "1", "b", "q"])
            self.assertEqual(calls, [])

    def test_an_adopted_repo_changes_what_it_contains(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            adopted(target)
            _code, calls, text = drive(target, ["2", "2,3", "y"])
            self.assertIn("set up at kit", text)
            self.assertIn("[2]", text)  # the current answer is the default
            self.assertIn("06-runbook.md: N/A -> Required", text)
            self.assertEqual(calls, [["change", "--profile", "library,data", str(target)]])

    def test_a_repo_behind_the_kit_is_offered_the_update(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            adopted(target, kit_version="1.0.0")
            _code, calls, text = drive(target, ["1", "y"])
            self.assertIn("Update to the installed kit version   <- recommended", text)
            self.assertEqual(calls, [["check", str(target)], ["doctor", str(target)],
                                     ["update", str(target)]])

    def test_creating_a_skill_asks_for_its_name_and_description(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            adopted(target)
            _code, calls, _text = drive(target, ["3", "review-docs", "Review docs before shipping"])
            # `--` keeps an answer such as "--help" from being read as a flag.
            self.assertEqual(calls, [["new-skill", "--", "review-docs",
                                      "Review docs before shipping", str(target)]])

    def test_a_wrong_choice_is_explained_and_end_of_input_quits(self):
        with tempfile.TemporaryDirectory() as d:
            code, calls, text = drive(Path(d), ["9", "²", "99999999999999999999999"])
            self.assertEqual(code, 0)
            self.assertEqual(calls, [])
            self.assertIn("'9' isn't a choice", text)
            self.assertIn("'²' isn't a choice", text)

    def test_a_command_that_exits_returns_to_the_menu(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            adopted(target)
            _code, calls, text = drive(target, ["3", "x", "y", "1"],
                                       codes={"new-skill": SystemExit(2)})
            self.assertIn("exited with code 2", text)
            # The menu kept going: check / fix ran after the failed skill.
            self.assertEqual([argv[0] for argv in calls], ["new-skill", "check", "doctor"])

    def test_a_repo_set_up_by_a_newer_kit_is_not_offered_a_downgrade(self):
        from standards.wizard import is_behind
        self.assertTrue(is_behind("1.0.0", "1.4.0"))
        self.assertTrue(is_behind("1.4.0", "1.10.0"))
        self.assertFalse(is_behind("1.4.0", "1.4.0"))
        self.assertFalse(is_behind("9.9.9", "1.4.0"))
        self.assertFalse(is_behind("dev", "1.4.0"))
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            adopted(target, kit_version="99.0.0")
            _code, _calls, text = drive(target, [])
            self.assertNotIn("Update to the installed kit version", text)

    def test_a_failed_check_is_still_reported_after_an_update(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            adopted(target, kit_version="1.0.0")
            _code, calls, text = drive(target, ["1", "y"], codes={"check": 1})
            self.assertEqual([argv[0] for argv in calls], ["check", "doctor", "update"])
            self.assertIn("exited with code 1", text)


if __name__ == "__main__":
    unittest.main()
