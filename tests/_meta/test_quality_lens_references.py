"""Every lens section a workflow cites must exist in the shared quality lens.

The implementation workflows bind their checkpoints to named lens sections
(`Reviewing`, `Security floor`, ...). A renamed or missing section silently
breaks that binding, so each citation is checked against the canonical lens
headings.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import REPO_ROOT, SKILLS_DIR  # noqa: E402

sys.path.insert(0, str(REPO_ROOT / "scripts"))
import sync_writing_rules as sync  # noqa: E402

RULE = next(rule for rule in sync.RULES if rule.id == "quality-lens")
BLOCK, DECLARED = sync.parse_canonical_file(
    RULE.canonical_file.read_text(encoding="utf-8"), RULE.start_marker, RULE.end_marker, RULE.declared_header
)
CITATION = re.compile(r"lens's `([^`]+)`")


def _lens_headings() -> set[str]:
    names = {line[3:].strip() for line in BLOCK.splitlines() if line.startswith("## ")}
    # A citation may drop the parenthetical: `Minimum structure` names "Minimum structure (KISS, YAGNI)".
    return names | {name.split(" (")[0] for name in names}


class TestLensCitations(unittest.TestCase):
    def test_every_cited_section_exists(self):
        headings = _lens_headings()
        cited = 0
        for skill in DECLARED:
            files = [SKILLS_DIR / skill / "SKILL.md", *sorted((SKILLS_DIR / skill / "steps").glob("*.md"))]
            for path in files:
                if not path.is_file():
                    continue
                for match in CITATION.finditer(path.read_text(encoding="utf-8")):
                    name = match.group(1)
                    cited += 1
                    with self.subTest(file=str(path.relative_to(REPO_ROOT)), section=name):
                        self.assertIn(name, headings)
        self.assertGreater(cited, 0, "no lens citations found; the pattern no longer matches")

    def test_declared_workflows_route_to_their_copy(self):
        for skill in DECLARED:
            with self.subTest(skill=skill):
                self.assertIn(
                    "references/quality-lens.md",
                    (SKILLS_DIR / skill / "SKILL.md").read_text(encoding="utf-8"),
                )


if __name__ == "__main__":
    unittest.main()
