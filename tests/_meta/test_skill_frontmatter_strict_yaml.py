"""Strict YAML 2.x parse-safety for every SKILL.md frontmatter.

The skills.sh CLI (`npx skills`) parses each SKILL.md frontmatter with
the JS `yaml@2.x` package in strict mode. Plain (unquoted) scalar values
containing `": "` (colon followed by whitespace) trip the strict parser
with "Nested mappings are not allowed in compact mappings" — and the
affected skill silently drops from the install list, breaking
`npx skills add <repo> --skill <name>`.

This regression test enforces that every frontmatter line of the form
`key: value` either:
  - wraps `value` in a quoted scalar (`'…'` or `"…"`), OR
  - uses a block scalar (`|`, `>`, `>-`, `|-`), OR
  - uses a flow collection (`[…]`, `{…}`), OR
  - contains no `": "` sequence inside the value.

Scoped to top-level frontmatter. Nested metadata strings are checked for
their field type by test_skill_frontmatter; this guard is not a full YAML parser.

History: 1.25.0 shipped with two violations (scaffold's `description`
and code-ultrareview's `when_to_use`), causing both skills to fail
discovery on `npx skills add coroboros/agent-skills --skill <name>`.
1.25.1 added the quotes and this test to prevent the regression.
"""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import get_skill_dirs  # noqa: E402

# A top-level frontmatter line — key starts at column 0, then `: `, then value.
_TOP_LEVEL_KV = re.compile(r"^([A-Za-z][\w-]*): (.*)$")


def _extract_frontmatter(skill_md_text: str) -> str:
    if not skill_md_text.startswith("---\n"):
        return ""
    end = skill_md_text.find("\n---\n", 4)
    if end == -1:
        return ""
    return skill_md_text[4:end]


def _is_safe_value(value: str) -> bool:
    """A plain scalar value is safe iff it contains no `": "` (colon-space).

    Quoted, block-scalar, and flow-collection openers are always safe —
    the strict parser disambiguates them by their leading character."""
    v = value.rstrip()
    if not v:
        return True
    head = v[0]
    if head in ("'", '"'):
        return True
    if head in ("|", ">"):
        return True
    if head in ("[", "{"):
        return True
    return ": " not in v


class TestFrontmatterStrictYamlParse(unittest.TestCase):
    """Every top-level plain-scalar value must be strict-YAML-safe.

    A failure here means `npx skills add <repo> --skill <name>` will
    silently drop the skill from discovery."""

    def test_argument_hints_are_not_yaml_collections(self):
        """Bracketed usage text needs quotes to remain a string in real YAML."""
        for skill in get_skill_dirs():
            frontmatter = _extract_frontmatter((skill / "SKILL.md").read_text())
            for line in frontmatter.splitlines():
                match = _TOP_LEVEL_KV.match(line)
                if match and match.group(1) == "argument-hint":
                    with self.subTest(skill=skill.name):
                        self.assertFalse(match.group(2).lstrip().startswith(("[", "{")),
                                         "Quote argument-hint to prevent a YAML collection")

    def test_no_unquoted_colon_space_in_plain_scalars(self):
        for skill in get_skill_dirs():
            with self.subTest(skill=skill.name):
                text = (skill / "SKILL.md").read_text(encoding="utf-8")
                fm = _extract_frontmatter(text)
                self.assertTrue(fm, f"{skill.name}/SKILL.md missing frontmatter")
                offenders = []
                for lineno, line in enumerate(fm.splitlines(), start=2):
                    m = _TOP_LEVEL_KV.match(line)
                    if not m:
                        continue
                    key, value = m.group(1), m.group(2)
                    if not _is_safe_value(value):
                        offenders.append(f"line {lineno} ({key}): contains unquoted ': '")
                self.assertEqual(
                    offenders, [],
                    f"{skill.name}/SKILL.md has strict-YAML-unsafe plain scalars — wrap each value "
                    f"in single quotes (escape internal apostrophes as ''):\n  "
                    + "\n  ".join(offenders),
                )


if __name__ == "__main__":
    unittest.main()
