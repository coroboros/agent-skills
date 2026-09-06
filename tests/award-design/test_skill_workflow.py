"""award-design SKILL.md top-level structure — the path contract.

The skill runs on a fixed division of labor: machines catch defects
(scanner/detector + the mechanical floor), fresh-context gates judge quality
(R1/R2, desire read), and the builder designs freely between the two. A nine-step
path carries the sequence, the roll forces the variance a model's own ranking
cannot, and every reference load is priced in the load map. This module pins the
section spine, the division of labor, the routing boundary, the scoped-run path,
and the judging-criteria numbers."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFS = SKILL_DIR / "references"
PREFLIGHT_MD = REFS / "preflight.md"


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


def _section(name):
    """A `## <name>` section body, up to the next `##`."""
    m = re.search(rf"^## {re.escape(name)}\b(.*?)(?=^##\s)", _body(),
                  re.DOTALL | re.MULTILINE)
    assert m is not None, f"## {name} section missing"
    return m.group(1)


def _ref(rel):
    return (REFS / rel).read_text(encoding="utf-8")


# The core spine — H2 sections, in document order.
EXPECTED_SECTIONS = [
    "## Routing",
    "## The path",
    "## The load map — every load is priced, none is free",
    "## Hard constraints",
    "## Verify, then ship",
    "## Output discipline",
    "## Gotchas",
]


class TestProtocolSpine(unittest.TestCase):
    """Routing → the path → the priced load map → the constraints → verify is
    the load-bearing structure: the sequence is what forces taste commitments
    early, while they cost nothing to change. A missing or reordered section is
    the rebuild half-landing."""

    def test_each_section_present(self):
        body = _body()
        for header in EXPECTED_SECTIONS:
            with self.subTest(section=header):
                self.assertIn(header, body, f"spine section missing: {header}")

    def test_sections_in_document_order(self):
        body = _body()
        positions = [body.find(h) for h in EXPECTED_SECTIONS]
        self.assertTrue(all(p != -1 for p in positions), "a spine section is missing")
        self.assertEqual(positions, sorted(positions),
                         "spine sections are out of the contracted order")

    def test_ambient_substitute_posture_is_gone(self):
        """The old framing — ambient judgment replacing the path — must not
        survive."""
        body = _body().lower()
        for stale in ("ambient forcing, not a checklist", "not phases to clear"):
            with self.subTest(phrase=stale):
                self.assertNotIn(stale, body,
                                 f"the ambient-substitute posture must not survive: {stale!r}")

    def test_builder_keeps_design_authority(self):
        """Machines catch defects, fresh eyes judge quality — and between the
        two the builder designs with full authority. Losing that line
        overcorrects into a checklist-only skill."""
        body = _body()
        self.assertIn("you design with full authority", body)
        self.assertIn("quality is judged beside a live exemplar, never scored by a number",
                      body, "checks are countable facts, never the judgment")


class TestDivisionOfLabor(unittest.TestCase):
    """Three instruments keep the builder's freedom honest — the machine checks,
    the fresh-context gates, and the roll that forces variance — and the two
    gates (R1 before any file, R2 on the render) are where quality is judged."""

    def test_three_instruments_named(self):
        body = _body()
        self.assertIn("Machines catch defects", body)
        self.assertIn("a fresh-context review judges quality", body)
        self.assertIn("scripts/direction_roll.py", body,
                      "the roll is the third instrument — forced variance, not taste")

    def test_gates_are_binary_with_written_overrides(self):
        """The binary-gate discipline lives in the mechanical floor: countable
        or binary, and every override written into the verdict."""
        preflight = PREFLIGHT_MD.read_text(encoding="utf-8")
        self.assertIn("countable or binary", preflight)
        self.assertIn("the override is written into the verdict and tied to the brief",
                      preflight)

    def test_fresh_context_gates_r1_r2(self):
        self.assertIn("A fresh context refutes the concept per `references/gate/concept.md` "
                      "before any build file exists", _section("The path"),
                      "R1 must refute the concept before any build file exists")
        self.assertIn("One driven audit, fresh context", _section("Verify, then ship"),
                      "R2 must be a fresh-context audit of the rendered site")


class TestScopedPath(unittest.TestCase):
    """A bounded change on a healthy DESIGN.md scales the path instead of
    running the full ceremony — without this declared short path, the skill's
    authority dies the first time a model reasonably bails on it."""

    def _scoped(self):
        m = re.search(r"^- \*\*Scoped runs — scale, never skip\.\*\*(.*?)(?=\n- |\n\n)",
                      _body(), re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "the scoped-run clause is missing from Routing")
        return m.group(1)

    def test_scaling_keeps_the_gates(self):
        scoped = self._scoped()
        self.assertIn("preserve established choices", scoped)
        self.assertIn("hand it to the builder, then review the affected pages", scoped)

    def test_thin_document_does_not_authorize_a_redesign(self):
        scoped = self._scoped()
        self.assertIn("documentation gap, not permission to redesign", scoped)
        self.assertIn("only missing decisions needed by the requested surface", scoped)
        self.assertIn("authorized new visual direction", scoped)

    def test_scaling_is_declared(self):
        scoped = self._scoped()
        self.assertIn("scoped run:", scoped,
                      "the scaled run must be declared, or it is a skipped step")


class TestRoutingBoundary(unittest.TestCase):
    """Routing is the discipline that keeps the skill from sprawling: review
    subcommand, single-token tweaks to /design-system, backend never, empty
    directory to /scaffold."""

    def _routing(self):
        return _section("Routing")

    def test_single_token_routes_to_design_system(self):
        routing = self._routing()
        self.assertIn("/design-system", routing)
        self.assertRegex(routing.lower(), r"single[- ]token")

    def test_never_touches_backend(self):
        self.assertIn("backend, data and infra remain with the engineering owner", self._routing().lower())

    def test_empty_dir_routes_to_scaffold(self):
        self.assertIn("/scaffold", self._routing())

    def test_review_subcommand_routed(self):
        self.assertIn("award-design review <url|path>", self._routing())


class TestAutoTriggerInWhenToUse(unittest.TestCase):
    """The auto-trigger-from-line-1 contract lives in the `when_to_use`
    frontmatter (the trigger surface), not the body."""

    def _when_to_use(self):
        m = re.search(r"(?m)^when_to_use:\s*(.+)$", _body())
        self.assertIsNotNone(m, "when_to_use frontmatter field missing")
        return m.group(1)

    def test_auto_triggers_from_line_one(self):
        wtu = self._when_to_use().lower()
        self.assertIn("auto-trigger", wtu)
        self.assertIn("requested scope", wtu)

    def test_routes_single_token_and_ignores_backend(self):
        wtu = self._when_to_use().lower()
        self.assertIn("/design-system", wtu)
        self.assertIn("backend", wtu)

    def test_review_subcommand_advertised(self):
        self.assertIn("award-design review", self._when_to_use())


class TestJudgingCriteria(unittest.TestCase):
    """The Awwwards weighting (40/30/20/10) is the contract the core carries;
    the score floors and the tier's measured ceiling calibrate the rubric. Drift
    means the skill's recommendations stop matching the judging signal."""

    def test_weights_documented(self):
        body = _body()
        for label, pct in [("Design", 40), ("Usability", 30),
                           ("Creativity", 20), ("Content", 10)]:
            with self.subTest(label=label, pct=pct):
                self.assertRegex(body, rf"{label}\s*{pct}\b")

    def test_score_floors_documented(self):
        self.assertIn("7.5+", _body(), "the core must carry the SOTD bar")
        self.assertIn("Honorable Mention starts at 6.5+", _ref("exemplars.md"),
                      "the HM floor calibrates the corpus R1 judges against")


class TestReadTheRoom(unittest.TestCase):
    """Step 0 loads atmosphere-calibration.md and declares the three dial
    values — silent dials cannot arbitrate later choices."""

    def _step_zero(self):
        m = re.search(r"(?m)^0\. \*\*Read the room\.\*\*.*$", _body())
        self.assertIsNotNone(m, "path step 0 (Read the room) missing")
        return m.group(0)

    def test_step_zero_loads_calibration_reference(self):
        self.assertIn("references/atmosphere-calibration.md", self._step_zero())

    def test_dials_declared_not_internal(self):
        self.assertIn("Density / Variance / Motion", self._step_zero(),
                      "step 0 must name the three dials")
        body = _body()
        self.assertIn("The dials live in DESIGN.md Overview prose", body,
                      "the dials must land in the DESIGN.md, never stay silent")
        self.assertIn("never as token groups", body)

    def test_remix_routes_to_reference(self):
        self.assertIn("Hybrid → `references/remixing.md`", _body(),
                      "hybrid briefs must route to references/remixing.md")


class TestTruthSourcing(unittest.TestCase):
    """The truth step is the fact gate: versions and support resolve through
    stack-facts.md's per-row trust/fetch class instead of training memory, and
    assets are secured before the build."""

    def _truth_step(self):
        m = re.search(r"(?m)^7\. \*\*DESIGN\.md and truth\.\*\*.*$", _body())
        self.assertIsNotNone(m, "path step 7 (DESIGN.md and truth) missing")
        return m.group(0)

    def test_loads_the_fact_source_and_imagery(self):
        step = self._truth_step()
        self.assertIn("references/stack-facts.md", step)
        self.assertIn("references/imagery.md", step)

    def test_heavy_layers_never_from_memory(self):
        self.assertIn("never re-derive the Lenis/GSAP wiring from memory", _body())
        facts = _ref("stack-facts.md")
        for layer in ("GSAP", "SplitText", "Three.js", "Lenis", "View Transitions"):
            with self.subTest(layer=layer):
                self.assertIn(layer, facts, f"stack-facts.md must carry the {layer} row")
        self.assertTrue((REFS / "ingredients" / "web-audio.md").is_file(),
                        "the Web Audio layer keeps its own cheat")

    def test_the_fetch_class_is_the_gate(self):
        step = self._truth_step()
        self.assertIn("the authority for versions and support", step)
        self.assertIn("fetch fresh docs only for its fetch-class rows", step,
                      "a fetch-class row is re-verified before its code is written")
        self.assertIn("trust the rest", step)


class TestMechanicalFloor(unittest.TestCase):
    """Verify is the mechanical floor: the scanner with the archetype, then the
    browser payloads, and a FAIL either gets fixed or gets a written line."""

    def _verify(self):
        return _section("Verify, then ship")

    def test_runs_the_scanner_with_the_archetype(self):
        verify = self._verify()
        self.assertIn("scripts/preflight_scan.py", verify)
        self.assertIn("--archetype", verify)

    def test_scanner_catches_never_clears(self):
        body = _body()
        self.assertIn("The scanner is a heuristic, not a judge", body)
        self.assertIn("A clean scan means nothing mechanical was caught", body,
                      "the scanner must be framed as catching, never clearing")

    def test_a_fail_blocks_or_is_justified_in_writing(self):
        verify = self._verify()
        self.assertIn("fix every FAIL or justify it in one written line tied to the brief",
                      verify)
        self.assertIn("fix-only", verify,
                      "detector and render-floor FAILs take no prose override")

    def test_the_review_report_is_the_verdict_artifact(self):
        self.assertIn("its report is the verdict artifact", self._verify())


class TestReviewAntiAnchoring(unittest.TestCase):
    """R2 judges the pixels before it reads the machine output — mechanical
    findings received early anchor the reviewer."""

    def test_reviewer_judges_before_reading_reports(self):
        review = _ref("gate/review.md")
        self.assertIn("**Inventory before anchoring.**", review)
        self.assertIn("before reading the direction contract, the DESIGN.md, "
                      "or any mechanical report", review,
                      "the reviewer must form judgment first, read reports second")

    def test_concept_veto_wired(self):
        self.assertIn("**Premise veto.**", _ref("gate/concept.md"),
                      "R1 must run the premise veto against the concept")
        self.assertIn("concept veto", _ref("audit-rubric.md").lower(),
                      "the rubric keeps the concept veto it scores with")


if __name__ == "__main__":
    unittest.main()
