"""Every lens section a workflow cites must exist in the shared quality lens.

The implementation workflows bind their checkpoints to named lens sections
(`Mechanical changes`, `Reviewing`, `Security floor`, ...). A renamed or missing
section silently breaks that binding, so each citation is checked against the
canonical lens headings.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import REPO_ROOT, SKILLS_DIR  # noqa: E402

CANONICAL = REPO_ROOT / ".agents" / "rules" / "skill-quality-lens-rules.md"
DECLARED = ("apex", "ultrapex", "oneshot")
CITATION = re.compile(
    r"lens's `([^`]+)`|lens's ([A-Z][a-z]+(?: [a-z]+)*) (?:rule|list)|lens § ([A-Z][a-z]+(?: [a-z]+)*)"
)


def _lens_headings() -> set[str]:
    text = CANONICAL.read_text(encoding="utf-8")
    start = text.index("<!-- canonical:quality-lens:start -->")
    end = text.index("<!-- canonical:quality-lens:end -->")
    names = {line[3:].strip() for line in text[start:end].splitlines() if line.startswith("## ")}
    # A citation may drop the parenthetical: `Minimum structure` names "Minimum structure (KISS, YAGNI)".
    return names | {name.split(" (")[0] for name in names}


class TestLensCitations(unittest.TestCase):
    def test_every_cited_section_exists(self):
        headings = _lens_headings()
        self.assertIn("Mechanical changes", headings)
        cited = 0
        for skill in DECLARED:
            files = [SKILLS_DIR / skill / "SKILL.md", *sorted((SKILLS_DIR / skill / "steps").glob("*.md"))]
            for path in files:
                if not path.is_file():
                    continue
                for match in CITATION.finditer(path.read_text(encoding="utf-8")):
                    name = match.group(1) or match.group(2) or match.group(3)
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
