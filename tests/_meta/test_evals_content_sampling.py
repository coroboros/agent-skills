"""Universal content-level invariants for `skills/<name>/evals/evals.json`.

Where `test_evals_shape.py` validates the JSON schema, this module pins
content quality — the "production-grade champion" rubric for evals:

- Each case has a `name` field (kebab-case, unique within the skill)
- Each skill ships ≥ 3 cases (substantive coverage, not a stub set)
- Every skill exercises at least one *refuse / skip / escalate* path
  (the negative-space cases are where pure-prompt skills earn their
  scope discipline — without them an eval set just rubber-stamps the
  happy path)
- For skills with `references/`, ≥ 1 case routes to a reference file in
  its `expected_output` (otherwise the references are orphans the model
  is never forced to consult)

These invariants apply to every shipped evals.json — code-bearing skills
that ship one are held to the same bar as pure-prompt skills.
"""

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

MIN_CASES = 3
KEBAB = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")
# Discriminating phrases — bare "ask" or "stop" leak into generic prose,
# so we require multi-word forms or context-specific verbs only. Tightened
# after a fresh-eyes audit caught false-positive risk on single-token matches.
ESCALATION_KEYWORDS = (
    # Refuse/escalate verbs (single-word OK because they're specific verbs
    # that don't leak into generic prose)
    "skip", "refuse", "refuses",
    "decline", "declines",
    "escalate", "escalates",
    "redirect", "redirects",
    # Negative-space phrases — distinct from generic "skip"
    "out of scope", "not for", "not an",
    "rather than",
    # Clarification — only multi-word forms (bare "ask" matches anything)
    "asks clarifying", "asks focused", "asks targeted", "ask the user",
    # Stop + action (bare "stop" matches anything; require continuation)
    "stops and", "stops,", "and stops",
    # Hand-off forms — require syntax to avoid generic-prose match
    "waits for",
    "recommends `/",
)


def _evals_files():
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        path = skill_dir / "evals" / "evals.json"
        if path.is_file():
            yield skill_dir.name, path


def _has_references(skill_name):
    return (SKILLS_DIR / skill_name / "references").is_dir()


class TestCaseNamesPresent(unittest.TestCase):
    """A `name` field on every case is the human-readable handle for triage —
    `case_id=3` is opaque, `name='circuit-breaker-fires-on-multi-file'` is not."""

    def test_every_case_has_name_field(self):
        for skill, path in _evals_files():
            data = json.loads(path.read_text(encoding="utf-8"))
            for case in data["evals"]:
                with self.subTest(skill=skill, case_id=case.get("id")):
                    self.assertIn("name", case,
                                  f"{path}: case {case.get('id')} missing 'name' field")
                    self.assertIsInstance(case["name"], str)
                    self.assertGreater(len(case["name"]), 0)

    def test_case_names_are_kebab_case(self):
        for skill, path in _evals_files():
            data = json.loads(path.read_text(encoding="utf-8"))
            for case in data["evals"]:
                name = case.get("name", "")
                if not name:
                    continue
                with self.subTest(skill=skill, case_id=case["id"], name=name):
                    self.assertRegex(
                        name, KEBAB,
                        f"{path}: case {case['id']} name '{name}' is not kebab-case",
                    )

    def test_case_names_unique_within_skill(self):
        for skill, path in _evals_files():
            data = json.loads(path.read_text(encoding="utf-8"))
            names = [c.get("name") for c in data["evals"] if c.get("name")]
            with self.subTest(skill=skill):
                self.assertEqual(
                    len(names), len(set(names)),
                    f"{path}: duplicate case names: {names}",
                )


class TestCaseCountFloor(unittest.TestCase):
    """Three cases is the bare minimum for a meaningful eval set —
    one happy, one edge, one refuse. Below that, the set is decorative."""

    def test_each_skill_has_minimum_cases(self):
        for skill, path in _evals_files():
            data = json.loads(path.read_text(encoding="utf-8"))
            with self.subTest(skill=skill):
                self.assertGreaterEqual(
                    len(data["evals"]), MIN_CASES,
                    f"{path}: only {len(data['evals'])} cases (< {MIN_CASES})",
                )


class TestRefuseEscalateCoverage(unittest.TestCase):
    """Every skill must pin its scope discipline — at least one case
    where the expected behaviour is to skip, refuse, decline, or escalate
    rather than execute. Without a negative-space case, the evals only
    prove the skill says yes — never that it knows when to say no."""

    def test_at_least_one_refuse_or_escalate_case(self):
        for skill, path in _evals_files():
            data = json.loads(path.read_text(encoding="utf-8"))
            hits = []
            for case in data["evals"]:
                expected = case.get("expected_output", "").lower()
                if any(kw in expected for kw in ESCALATION_KEYWORDS):
                    hits.append(case.get("name") or case["id"])
            with self.subTest(skill=skill):
                self.assertGreater(
                    len(hits), 0,
                    f"{path}: no case exercises a refuse/skip/escalate path. "
                    f"Add a case where expected_output mentions one of {ESCALATION_KEYWORDS}.",
                )


class TestReferenceRouting(unittest.TestCase):
    """Skills that ship `references/` invest tokens in those files — the
    evals must prove the model is routed to them rather than re-deriving
    the content inline. Otherwise references are orphans."""

    def test_skills_with_references_route_at_least_once(self):
        for skill, path in _evals_files():
            if not _has_references(skill):
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            ref_routes = []
            for case in data["evals"]:
                expected = case.get("expected_output", "")
                # Either explicit `references/<file>.md` or `references/<topic>`
                if "references/" in expected:
                    ref_routes.append(case.get("name") or case["id"])
            with self.subTest(skill=skill):
                self.assertGreater(
                    len(ref_routes), 0,
                    f"{path}: skill ships references/ but no eval case mentions "
                    "routing to a reference file in expected_output. "
                    "Reference files are orphans without at least one routing case.",
                )


if __name__ == "__main__":
    unittest.main()
