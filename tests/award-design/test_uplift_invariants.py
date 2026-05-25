"""award-design uplift invariants — pin the contracts introduced by the
taste-skill comparative audit. These tests catch silent drift on the
new sub-features added in the uplift PR: output discipline, brief signal
routing, premium-patterns numbering, retrofit playbook, pre-DESIGN.md
plan, spring physics canonical values, composition variety mandates.

Each invariant exists because the previous review surfaced a real
failure mode that would re-emerge if the section drifted. Test names
describe the contract being pinned, not the implementation."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFS = SKILL_DIR / "references"


def _read(path):
    return path.read_text(encoding="utf-8")


# Mirrors the archetype list in test_archetypes.py — kept duplicated rather
# than imported to keep this test file self-contained and readable.
ARCHETYPES_DISPLAY = [
    "Minimalist",
    "Brutalist",
    "Editorial",
    "Bold / Maximal",
    "Immersive / Cinematic",
    "Experimental",
    "Corporate Luxury",
    "Bento / Card",
    "Spatial Organic",
]


class TestOutputDisciplineSection(unittest.TestCase):
    """SKILL.md ## Output discipline pins the banned-phrase floor and the
    continuation-marker contract. Both are easily lost in a refactor that
    treats the section as boilerplate; the test ensures they survive."""

    def setUp(self):
        body = _read(SKILL_MD)
        m = re.search(
            r"^## Output discipline\s*\n(.*?)(?=^##\s|\Z)",
            body, re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, "## Output discipline section missing from SKILL.md")
        self.section = m.group(1)

    def test_no_placeholder_shortcuts_rule_present(self):
        # Any of these phrases proves the rule is stated, not just hinted.
        for marker in ("[remaining sections similar]", "// TODO", "for brevity"):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.section,
                              f"output discipline must name banned phrase: {marker}")

    def test_continuation_marker_documented(self):
        self.assertIn("PAUSED", self.section,
                      "output discipline must document the [PAUSED — N of 8 ...] marker")
        self.assertIn("continue", self.section,
                      "output discipline must instruct resume via 'continue'")

    def test_routes_to_anti_patterns_full_list(self):
        # The SKILL.md section is the summary; the full ban catalog lives
        # in anti-patterns.md so it stays loaded only when validating.
        self.assertIn("anti-patterns.md", self.section,
                      "output discipline must cross-reference anti-patterns.md")


class TestAntiPatternsOutputDiscipline(unittest.TestCase):
    """anti-patterns.md must carry the full output-discipline ban catalog
    referenced from SKILL.md. Three categories (code / prose / structural)
    cover the empirically-observed truncation patterns."""

    def setUp(self):
        body = _read(REFS / "anti-patterns.md")
        m = re.search(
            r"^## Output discipline\s*\n(.*?)(?=^##\s|\Z)",
            body, re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, "anti-patterns.md missing ## Output discipline section")
        self.section = m.group(1)

    def test_three_ban_categories_present(self):
        """Code-level, prose-level, structural — three categories of truncation
        with distinct failure modes; collapsing them loses signal."""
        for category in ("Banned in code blocks", "Banned in prose", "Banned structural"):
            with self.subTest(category=category):
                self.assertIn(category, self.section,
                              f"output discipline must keep ban category: {category}")

    def test_continuation_marker_format_pinned(self):
        # Pin the exact marker shape — any drift breaks the resume contract
        # documented in SKILL.md.
        self.assertRegex(
            self.section,
            r"\[PAUSED\s*[—\-]\s*N\s+of\s+8\s+sections\s+complete",
            "anti-patterns.md must pin the [PAUSED — N of 8 sections complete] marker",
        )


class TestBriefSignalRouting(unittest.TestCase):
    """The Brief signal → first-pass routing table must list all 9 archetypes,
    one row each. Drift here means a brief-vocabulary lookup silently routes
    the user to a missing/renamed archetype."""

    def setUp(self):
        body = _read(SKILL_MD)
        # Grab from the routing intro to the next bold heading or section break.
        m = re.search(
            r"\*\*Brief signal → first-pass routing\.\*\*(.*?)(?=^\*\*Handoff|^##|\Z)",
            body, re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, "Brief signal routing section missing")
        self.section = m.group(1)

    def test_each_archetype_appears_in_routing(self):
        for archetype in ARCHETYPES_DISPLAY:
            with self.subTest(archetype=archetype):
                self.assertIn(
                    f"**{archetype}**", self.section,
                    f"routing table must include archetype row for: {archetype}",
                )


class TestPreDesignMdPlan(unittest.TestCase):
    """Phase 3 (Tokens) requires a five-bullet pre-plan as the contract for
    what follows. The pre-plan is the gate that catches a misaligned brief
    before tokens get committed; losing it returns the skill to the
    silent-drift failure mode. (Was anchored to step 6 pre-refactor.)"""

    def test_phase_3_carries_pre_plan_contract(self):
        body = _read(SKILL_MD)
        m = re.search(
            r"^### Phase 3 — Tokens(.*?)(?=^### Phase|\Z|^##\s)",
            body, re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, "Phase 3 (Tokens) missing")
        section = m.group(1)
        # The "five-bullet" / "pre-plan" terminology is the contract.
        self.assertRegex(
            section, r"(five[- ]bullet|5[- ]bullet|pre[- ]plan)",
            "Phase 3 must mandate a five-bullet pre-plan",
        )
        # And the five contract elements must be named — at minimum
        # signature moment + atmosphere scores, the two that anchor the rest.
        self.assertIn("signature moment", section.lower())
        self.assertIn("atmosphere", section.lower())


class TestPremiumPatternsNumbering(unittest.TestCase):
    """premium-patterns.md numbers patterns 1..N at H2 (`## N. Title`).
    The numbering is referenced from SKILL.md ('pattern 9', 'pattern 4 hero')
    and from cross-links in other reference files — gaps or duplicates
    silently break those references."""

    def test_patterns_numbered_sequentially(self):
        body = _read(REFS / "premium-patterns.md")
        # Match `## <N>. <Title>` headings only; sub-headings (`###`) are
        # excluded so e.g. "## 4. Hero Architecture" counts but its
        # "### Hero Scale taxonomy" sub-heading does not.
        nums = [int(m) for m in re.findall(r"^##\s+(\d+)\.\s+", body, re.MULTILINE)]
        self.assertGreaterEqual(len(nums), 8,
                                "premium-patterns.md must keep ≥8 numbered patterns")
        # Sequential, no gaps, no duplicates — 1..N
        expected = list(range(1, len(nums) + 1))
        self.assertEqual(nums, expected,
                         f"pattern numbers must be sequential 1..N, got {nums}")

    def test_uplift_patterns_present(self):
        """The three patterns the uplift added — pattern 9 (Liquid Glass),
        10 (Inline Typography Images), 11 (Perpetual Micro-Interactions) —
        must each ship with their named title."""
        body = _read(REFS / "premium-patterns.md")
        for num, title_substr in [
            (9, "Liquid Glass Refraction"),
            (10, "Inline Typography Images"),
            (11, "Perpetual Micro-Interactions"),
        ]:
            with self.subTest(pattern=num):
                # assertRegex applies re.search without flags; use re.search
                # explicitly so `^` matches a line start (MULTILINE), not just
                # the start of the file.
                pattern = rf"^##\s+{num}\.\s+{re.escape(title_substr)}"
                self.assertIsNotNone(
                    re.search(pattern, body, re.MULTILINE),
                    f"pattern {num} ({title_substr}) missing from premium-patterns.md",
                )


class TestRetrofitPlaybook(unittest.TestCase):
    """retrofit.md is the seven-step priority order for upgrading existing
    sites. The step order is the core IP — losing or reordering steps breaks
    the playbook's logic (font swap before color is intentional, color before
    hover states is intentional, etc.)."""

    EXPECTED_STEP_TITLES = [
        "Font swap",
        "Color palette cleanup",
        "Hover and active states",
        "Layout and spacing",
        "Replace generic components",
        "Empty / error / loading states",
        "Typography polish",
    ]

    def setUp(self):
        path = REFS / "retrofit.md"
        self.assertTrue(path.is_file(), "retrofit.md must exist")
        self.body = _read(path)

    def test_seven_steps_in_order(self):
        # Match `### N. Title` headings — step ordering is encoded by N.
        steps = re.findall(r"^###\s+(\d+)\.\s+(.+?)$", self.body, re.MULTILINE)
        self.assertEqual(len(steps), 7,
                         f"retrofit.md must have 7 steps, found {len(steps)}")
        for (num_str, title), expected_num, expected_title in zip(
            steps, range(1, 8), self.EXPECTED_STEP_TITLES,
        ):
            with self.subTest(step=expected_num):
                self.assertEqual(int(num_str), expected_num,
                                 f"step {expected_num} mis-numbered as {num_str}")
                self.assertIn(
                    expected_title, title,
                    f"step {expected_num} title drift: expected '{expected_title}', got '{title}'",
                )

    def test_what_not_to_retrofit_section_present(self):
        """The negative-space section is what makes the playbook honest —
        it tells the agent when retrofit isn't the right tool."""
        self.assertIn("What NOT to retrofit", self.body,
                      "retrofit.md must keep the 'What NOT to retrofit' boundary section")


class TestRetrofitCrossLinks(unittest.TestCase):
    """retrofit.md is reachable from SKILL.md step 1 and from
    brand-extraction.md. If these cross-links break, the file becomes
    unreachable from the agent's loading path."""

    def test_skill_md_links_to_retrofit(self):
        self.assertIn("references/retrofit.md", _read(SKILL_MD),
                      "SKILL.md must cross-reference references/retrofit.md")

    def test_brand_extraction_links_to_retrofit(self):
        self.assertIn("references/retrofit.md", _read(REFS / "brand-extraction.md"),
                      "brand-extraction.md must cross-reference retrofit.md for legacy-site flows")


class TestSpringPhysicsCanonicalValues(unittest.TestCase):
    """foundations.md pins the Framer Motion canonical spring values
    (stiffness: 100, damping: 20). Ad-hoc spring values per component
    betray the system — pinning the canonical numbers in the reference
    forces every consumer to match."""

    def test_canonical_spring_values_present(self):
        body = _read(REFS / "foundations.md")
        # Both numbers must appear together — proximity matters for the
        # contract; a stray "100" elsewhere wouldn't satisfy the rule.
        self.assertRegex(
            body, r"stiffness:\s*100",
            "foundations.md must pin canonical Framer Motion spring stiffness: 100",
        )
        self.assertRegex(
            body, r"damping:\s*20",
            "foundations.md must pin canonical Framer Motion spring damping: 20",
        )

    def test_spring_section_links_to_motion_tokens(self):
        body = _read(REFS / "foundations.md")
        # The spring physics section must instruct consumers to bind the
        # values to motion.* extension tokens — otherwise the rule is
        # discoverable but not enforceable.
        m = re.search(
            r"###\s+Spring physics(.*?)(?=^###\s|^##\s|\Z)",
            body, re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, "foundations.md missing 'Spring physics' subsection")
        self.assertIn("motion.", m.group(1),
                      "spring physics section must reference motion.* tokens")


class TestCompositionVarietyMandates(unittest.TestCase):
    """foundations.md ships four composition-variety mandates that together
    prevent the templated-rhythm failure mode on multi-section pages.
    Losing any single mandate weakens the rule."""

    REQUIRED_MANDATES = (
        "Composition Anchor diversity",
        "Background Mode variation",
        "CTA variation",
        "Section size variety",
    )

    def test_all_four_mandates_present(self):
        body = _read(REFS / "foundations.md")
        m = re.search(
            r"###\s+Composition variety mandates(.*?)(?=^###\s|^##\s|\Z)",
            body, re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, "foundations.md missing 'Composition variety mandates' subsection")
        section = m.group(1)
        for mandate in self.REQUIRED_MANDATES:
            with self.subTest(mandate=mandate):
                self.assertIn(mandate, section,
                              f"composition variety mandates must keep: {mandate}")


if __name__ == "__main__":
    unittest.main()
