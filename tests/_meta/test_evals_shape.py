"""Universal validator for `skills/<name>/evals/evals.json` files.

Per skill-creator's documented schema (skill-creator/SKILL.md § "Test Cases"
+ references/schemas.md), every evals.json must have:
  - skill_name (string, matches folder name)
  - evals (array of cases)
  - each case: id (int, unique), prompt (string), expected_output (string), files (array)

Skills without evals/evals.json are tolerated — evals are not mandatory for
every skill (code-bearing skills rely on unit tests). But when present, the
file must conform.
"""

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = REPO_ROOT / "skills"


def _evals_files():
    """Yield (skill_name, path) for every evals.json shipped."""
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        evals_path = skill_dir / "evals" / "evals.json"
        if evals_path.is_file():
            yield skill_dir.name, evals_path


class TestEvalsShape(unittest.TestCase):
    """Every shipped evals.json conforms to skill-creator's documented schema."""

    def test_at_least_one_skill_has_evals(self):
        files = list(_evals_files())
        self.assertGreater(
            len(files), 0,
            "no evals/evals.json shipped — at least the pure-prompt skills should have one",
        )

    def test_every_evals_json_is_valid_json(self):
        for skill, path in _evals_files():
            with self.subTest(skill=skill):
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                except json.JSONDecodeError as exc:
                    self.fail(f"{path}: invalid JSON — {exc}")
                self.assertIsInstance(data, dict)

    def test_every_evals_json_has_required_keys(self):
        for skill, path in _evals_files():
            with self.subTest(skill=skill):
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertIn("skill_name", data)
                self.assertIn("evals", data)
                self.assertEqual(
                    data["skill_name"], skill,
                    f"{path}: skill_name '{data['skill_name']}' does not match folder '{skill}'",
                )

    def test_every_eval_case_has_required_fields(self):
        for skill, path in _evals_files():
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertIsInstance(data["evals"], list)
            self.assertGreater(
                len(data["evals"]), 0,
                f"{path}: evals array is empty",
            )
            for case in data["evals"]:
                with self.subTest(skill=skill, case_id=case.get("id")):
                    for key in ("id", "prompt", "expected_output", "files"):
                        self.assertIn(key, case, f"missing key: {key}")
                    self.assertIsInstance(case["id"], int)
                    self.assertIsInstance(case["prompt"], str)
                    self.assertIsInstance(case["expected_output"], str)
                    self.assertIsInstance(case["files"], list)
                    # Substantive prompt (>10 chars — short refs like
                    # "/oneshot #42" are real users use-cases) and expected
                    # output (>50 chars — must describe a verifiable result).
                    self.assertGreater(
                        len(case["prompt"]), 10,
                        f"prompt too short — likely a stub",
                    )
                    self.assertGreater(
                        len(case["expected_output"]), 50,
                        f"expected_output too short — likely a stub",
                    )

    def test_eval_ids_unique_within_skill(self):
        for skill, path in _evals_files():
            with self.subTest(skill=skill):
                data = json.loads(path.read_text(encoding="utf-8"))
                ids = [case["id"] for case in data["evals"]]
                self.assertEqual(len(ids), len(set(ids)),
                                 f"{path}: duplicate eval ids: {ids}")

    def test_pure_prompt_skills_have_evals(self):
        """The 5 pure-prompt skills must ship evals — that's how their behaviour
        is pinned beyond unit-test structural checks."""
        pure_prompt = {
            "agent-creator", "award-design", "brainstorm",
            "fix-grammar", "oneshot",
        }
        with_evals = {name for name, _ in _evals_files()}
        missing = pure_prompt - with_evals
        self.assertEqual(
            missing, set(),
            f"pure-prompt skills missing evals/evals.json: {sorted(missing)}",
        )


if __name__ == "__main__":
    unittest.main()
