"""Parity tests for the canonical blocks embedded in declared skills.

Five canonical rules share this suite — `writing-rules` (style), `label-hygiene`
(internal-label vocabulary leakage), `execution-discipline` (how the skill changes
code), `adversarial-verification` (how the skill trusts its own findings), and
`quality-lens` (the implementation workflows' review rubric, shipped as a whole
`references/quality-lens.md` file). Each lives in its own `.agents/rules/skill-*.md`
file with its own marker pair and declared-skill list, and propagates via
`scripts/sync_writing_rules.py`. These tests
enforce byte-level parity, exclusion of non-declared skills,
and absence of personal/brand-voice path leaks — once per rule.
"""

from __future__ import annotations

import json
import re
import shutil
import tempfile
import subprocess
import sys
import unittest
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import REPO_ROOT, SKILLS_DIR  # noqa: E402

SYNC_SCRIPT = REPO_ROOT / "scripts" / "sync_writing_rules.py"
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"


class Rule(NamedTuple):
    id: str
    canonical_file: Path
    start_marker: str
    end_marker: str
    declared_header: str
    excluded_header: str
    target: str = "SKILL.md"


CANONICAL_RULES: tuple[Rule, ...] = (
    Rule(
        id="writing-rules",
        canonical_file=REPO_ROOT / ".agents" / "rules" / "skill-prose-rules.md",
        start_marker="<!-- canonical:writing-rules:start -->",
        end_marker="<!-- canonical:writing-rules:end -->",
        declared_header="## Declared prose-emitting skills",
        excluded_header="## Excluded skills (with reason)",
    ),
    Rule(
        id="label-hygiene",
        canonical_file=REPO_ROOT / ".agents" / "rules" / "skill-label-hygiene-rules.md",
        start_marker="<!-- canonical:label-hygiene:start -->",
        end_marker="<!-- canonical:label-hygiene:end -->",
        declared_header="## Declared label-hygiene skills",
        excluded_header="## Excluded skills (with reason)",
    ),
    Rule(
        id="execution-discipline",
        canonical_file=REPO_ROOT
        / ".agents"
        / "rules"
        / "skill-execution-discipline-rules.md",
        start_marker="<!-- canonical:execution-discipline:start -->",
        end_marker="<!-- canonical:execution-discipline:end -->",
        declared_header="## Declared execution-discipline skills",
        excluded_header="## Excluded skills (with reason)",
    ),
    Rule(
        id="adversarial-verification",
        canonical_file=REPO_ROOT
        / ".agents"
        / "rules"
        / "skill-adversarial-verification-rules.md",
        start_marker="<!-- canonical:adversarial-verification:start -->",
        end_marker="<!-- canonical:adversarial-verification:end -->",
        declared_header="## Declared adversarial-verification skills",
        excluded_header="## Excluded skills (with reason)",
    ),
    Rule(
        id="quality-lens",
        canonical_file=REPO_ROOT / ".agents" / "rules" / "skill-quality-lens-rules.md",
        start_marker="<!-- canonical:quality-lens:start -->",
        end_marker="<!-- canonical:quality-lens:end -->",
        declared_header="## Declared quality-lens skills",
        excluded_header="## Excluded skills (with reason)",
        target="references/quality-lens.md",
    ),
)

def _parse_canonical(rule: Rule) -> tuple[str, list[str], list[str]]:
    """Return (canonical_block, declared_list, excluded_list) for one rule."""
    text = rule.canonical_file.read_text(encoding="utf-8")
    s = text.find(rule.start_marker)
    e = text.find(rule.end_marker)
    if s == -1 or e == -1 or e <= s:
        raise AssertionError(
            f"{rule.id}: canonical markers missing or malformed in {rule.canonical_file}"
        )
    block = text[s : e + len(rule.end_marker)]

    def _list_under(header: str) -> list[str]:
        m = re.search(
            rf"^{re.escape(header)}\s*$(.*?)^## ",
            text,
            re.MULTILINE | re.DOTALL,
        )
        if not m:
            raise AssertionError(f"{rule.id}: section {header!r} not found")
        out: list[str] = []
        for line in m.group(1).splitlines():
            bm = re.match(r"^- `?([a-z][a-z0-9-]*)`?", line.strip())
            if bm:
                out.append(bm.group(1))
        return out

    declared = _list_under(rule.declared_header)
    excluded = _list_under(rule.excluded_header)
    return block, declared, excluded


def _extract_block(skill_md: Path, start_marker: str, end_marker: str) -> str | None:
    text = skill_md.read_text(encoding="utf-8")
    s = text.find(start_marker)
    e = text.find(end_marker)
    if s == -1 or e == -1 or e <= s:
        return None
    return text[s : e + len(end_marker)]


class TestCanonicalFiles(unittest.TestCase):
    def test_claude_entrypoint_loads_canonical_instructions(self):
        self.assertEqual((REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8"), "@AGENTS.md\n")
        self.assertTrue((REPO_ROOT / "AGENTS.md").is_file())

    def test_claude_behavior_adapters_match_owners(self):
        """Both hosts must receive the same general behavior rules."""
        for suffix in ("", "-frontier"):
            with self.subTest(rule=suffix or "core"):
                source = REPO_ROOT / ".agents" / "rules" / f"behavior{suffix}.md"
                adapter = REPO_ROOT / ".claude" / "rules" / f"behave{suffix}.md"
                self.assertEqual(source.read_bytes(), adapter.read_bytes())

class TestDeclaredSkillsCarryBlock(unittest.TestCase):
    def test_every_declared_skill_carries_canonical_block_verbatim(self):
        for rule in CANONICAL_RULES:
            block, declared, _ = _parse_canonical(rule)
            for name in declared:
                with self.subTest(rule=rule.id, skill=name):
                    skill_md = SKILLS_DIR / name / rule.target
                    self.assertTrue(skill_md.is_file(), f"missing {skill_md}")
                    got = _extract_block(skill_md, rule.start_marker, rule.end_marker)
                    self.assertIsNotNone(
                        got, f"{name} ({rule.id}): canonical markers absent"
                    )
                    self.assertEqual(
                        got,
                        block,
                        f"{name} ({rule.id}): canonical block drift — "
                        f"run scripts/sync_writing_rules.py",
                    )
                    if rule.target != "SKILL.md":
                        self.assertEqual(
                            skill_md.read_text(encoding="utf-8"),
                            block + "\n",
                            f"{name} ({rule.id}): content outside the canonical block — "
                            f"run scripts/sync_writing_rules.py",
                        )

    def test_canonical_block_markers_unique_per_file(self):
        for rule in CANONICAL_RULES:
            _, declared, _ = _parse_canonical(rule)
            for name in declared:
                with self.subTest(rule=rule.id, skill=name):
                    text = (SKILLS_DIR / name / rule.target).read_text(encoding="utf-8")
                    self.assertEqual(
                        text.count(rule.start_marker),
                        1,
                        f"{name} ({rule.id}): start marker not unique",
                    )
                    self.assertEqual(
                        text.count(rule.end_marker),
                        1,
                        f"{name} ({rule.id}): end marker not unique",
                    )


class TestExcludedSkills(unittest.TestCase):
    def test_excluded_skills_have_no_canonical_block(self):
        for rule in CANONICAL_RULES:
            _, _, excluded = _parse_canonical(rule)
            for name in excluded:
                with self.subTest(rule=rule.id, skill=name):
                    skill_md = SKILLS_DIR / name / "SKILL.md"
                    self.assertTrue(skill_md.is_file(), f"missing {skill_md}")
                    target = SKILLS_DIR / name / rule.target
                    if rule.target != "SKILL.md":
                        self.assertFalse(
                            target.exists(),
                            f"{name} ({rule.id}): excluded skill carries {rule.target}",
                        )
                    text = target.read_text(encoding="utf-8") if target.is_file() else ""
                    self.assertNotIn(
                        rule.start_marker,
                        text,
                        f"{name} ({rule.id}): should not carry canonical block",
                    )
                    self.assertNotIn(
                        rule.end_marker,
                        text,
                        f"{name} ({rule.id}): should not carry canonical block",
                    )


class TestMarketplaceClassification(unittest.TestCase):
    def test_every_marketplace_skill_classified_per_rule(self):
        """Every skill in marketplace.json is classified by each canonical rule
        — declared XOR excluded."""
        data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        listed = {
            entry.removeprefix("./skills/")
            for plugin in data["plugins"]
            for entry in plugin.get("skills", [])
        }
        for rule in CANONICAL_RULES:
            with self.subTest(rule=rule.id):
                _, declared, excluded = _parse_canonical(rule)
                classified = set(declared) | set(excluded)
                unclassified = listed - classified
                self.assertFalse(
                    unclassified,
                    f"{rule.id}: marketplace skills missing classification "
                    f"in {rule.canonical_file.name}: {sorted(unclassified)}",
                )


class TestPrivacy(unittest.TestCase):
    BANNED = (
        "BRAND-VOICE",
        "/.claude/brand-voices",
        "/Users/",
        "/home/",
        "C:\\Users\\",
        "$HOME/.claude",
    )

    def test_no_brand_voice_path_leak_in_canonical_block(self):
        for rule in CANONICAL_RULES:
            with self.subTest(rule=rule.id):
                block, _, _ = _parse_canonical(rule)
                for pat in self.BANNED:
                    self.assertNotIn(
                        pat, block, f"{rule.id}: canonical block leaks {pat!r}"
                    )

class TestSyncIdempotent(unittest.TestCase):
    def test_sync_repairs_drift_and_preserves_bytes_on_rerun(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / "scripts" / SYNC_SCRIPT.name
            script.parent.mkdir()
            shutil.copyfile(SYNC_SCRIPT, script)
            expected = {}
            for rule in CANONICAL_RULES:
                canonical = root / rule.canonical_file.relative_to(REPO_ROOT)
                canonical.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(rule.canonical_file, canonical)
                block, declared, _ = _parse_canonical(rule)
                for name in declared:
                    for source in {SKILLS_DIR / name / "SKILL.md", SKILLS_DIR / name / rule.target}:
                        relative = source.relative_to(REPO_ROOT)
                        target = root / relative
                        if relative not in expected:
                            expected[relative] = source.read_bytes()
                            target.parent.mkdir(parents=True, exist_ok=True)
                            target.write_bytes(expected[relative])
                target = root / "skills" / declared[0] / rule.target
                if rule.target == "SKILL.md":
                    content = target.read_text(encoding="utf-8")
                    self.assertIn(block, content)
                    target.write_text(content.replace(
                        block, rule.start_marker + "\nStale guidance.\n" + rule.end_marker, 1,
                    ), encoding="utf-8")
                else:
                    target.unlink()

            for run in range(2):
                result = subprocess.run(
                    [sys.executable, str(script)], cwd=root,
                    capture_output=True, text=True, timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                for relative, content in expected.items():
                    with self.subTest(run=run, path=str(relative)):
                        self.assertEqual((root / relative).read_bytes(), content)


if __name__ == "__main__":
    unittest.main()
