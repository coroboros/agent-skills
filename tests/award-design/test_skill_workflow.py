"""award-design SKILL.md top-level structure — the phase-spine contract.

The rebuilt skill runs on a fixed division of labor: machines catch defects
(scanner/detector + the mechanical floor), fresh-context reviews judge quality
(R1/R2, desire read), and the builder designs freely between the two. Seven
phases (0–6) remain the load-bearing sequence, each closing on a stated
artifact, with per-phase reference loads and the R1/R2 gates. This module pins
the phase spine, the working-header contract, the routing boundary, the
scoped-run path, and the judging-criteria numbers."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_MD = REPO_ROOT / "skills" / "award-design" / "SKILL.md"
PREFLIGHT_MD = REPO_ROOT / "skills" / "award-design" / "references" / "preflight.md"


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


def _phase(n):
    m = re.search(rf"^## Phase {n} — .*?\n(.*?)(?=^## )", _body(), re.DOTALL | re.MULTILINE)
    assert m is not None, f"## Phase {n} section missing"
    return m.group(1)


# The protocol spine — H2/H3 sections, in document order.
EXPECTED_SECTIONS = [
    "## How this skill works",
    "### Routing",
    "### Scoped changes — scale, never skip",
    "## Phase 0 — Read the room",
    "## Phase 1 — Conceive the universe",
    "## Phase 2 — Write the universe as DESIGN.md",
    "## Phase 3 — Source the truth",
    "## Phase 4 — Commit, then build",
    "## Phase 5 — Verify: the mechanical floor",
    "## Phase 6 — Review, then ship",
    "## Hard constraints",
    "## Review mode",
    "## Judging criteria",
    "## Output discipline",
    "## Gotchas",
]


class TestProtocolSpine(unittest.TestCase):
    """Phases 0–6 in order is the load-bearing structure: the sequence is what
    forces taste commitments early, while they cost nothing to change. A
    missing or reordered phase is the rebuild half-landing."""

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
        self.assertIn("none is a script", body,
                      "references, library, and playbooks are evidence, never scripts")


class TestHowThisSkillWorks(unittest.TestCase):
    """The working header states the contract the phases enforce: every phase
    runs on every build, each closes on a stated artifact, and three
    instruments keep the builder's freedom honest."""

    def _header(self):
        m = re.search(r"^## How this skill works\b(.*?)(?=^##\s)", _body(),
                      re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "## How this skill works section missing")
        return m.group(1)

    def test_every_phase_runs_on_every_build(self):
        header = self._header()
        self.assertIn("Every phase runs on every build", header)
        self.assertIn("each closing on a small stated artifact", header)

    def test_three_instruments_named(self):
        header = self._header()
        self.assertIn("Scanner + detector", header)
        self.assertIn("Fresh-context reviews", header)
        self.assertIn("rotation stamp", header.lower())

    def test_gates_are_binary_with_written_overrides(self):
        """The binary-gate discipline lives in the mechanical floor: countable
        or binary, and every override written into the verdict."""
        preflight = PREFLIGHT_MD.read_text(encoding="utf-8")
        self.assertIn("countable or binary", preflight)
        self.assertIn("the override is written into the verdict and tied to the brief",
                      preflight)

    def test_every_phase_has_load_and_artifact(self):
        """Phases 0–5 each name their reference loads; phases 0–6 each end with
        a stated artifact. A phase without either is unenforceable."""
        for n in range(6):
            with self.subTest(phase=n, clause="Load"):
                self.assertIn("**Load:**", _phase(n),
                              f"Phase {n} must name its reference loads")
        for n in range(7):
            with self.subTest(phase=n, clause="Artifact"):
                self.assertIn("**Artifact:**", _phase(n),
                              f"Phase {n} must end with a stated artifact")

    def test_fresh_context_gates_r1_r2(self):
        self.assertIn("**Gate (R1):**", _phase(1),
                      "Phase 1 must gate on a fresh-context refutation of the universe")
        self.assertIn("**Gate (R2):**", _phase(6),
                      "Phase 6 must gate on a fresh-context review of the rendered site")


class TestScopedPath(unittest.TestCase):
    """A bounded change on a healthy DESIGN.md scales the phases instead of
    running the full ceremony — without this declared short path, the protocol's
    authority dies the first time a model reasonably bails on it."""

    def _scoped(self):
        m = re.search(r"^### Scoped changes — scale, never skip\b(.*?)(?=^##\s)",
                      _body(), re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "### Scoped changes section missing")
        return m.group(1)

    def test_scaling_keeps_every_phase(self):
        scoped = self._scoped()
        self.assertIn("every phase at the scale of the touched surface", scoped)
        self.assertIn("never silently regenerate", scoped)

    def test_full_protocol_triggers_enumerated(self):
        scoped = self._scoped()
        for trigger in ("redesign brief", "missing or thin DESIGN.md", "new page family"):
            with self.subTest(trigger=trigger):
                self.assertIn(trigger, scoped)

    def test_scaling_is_declared(self):
        scoped = self._scoped()
        self.assertIn("scoped run:", scoped,
                      "the scaled run must be declared, or it is a skipped phase")


class TestRoutingBoundary(unittest.TestCase):
    """Routing is the discipline that keeps the skill from sprawling: review
    subcommand, single-token tweaks to /design-system, backend never, empty
    directory to /scaffold."""

    def _routing(self):
        m = re.search(r"^### Routing\b(.*?)(?=^##\s)", _body(),
                      re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "### Routing section missing")
        return m.group(1)

    def test_single_token_routes_to_design_system(self):
        routing = self._routing()
        self.assertIn("/design-system", routing)
        self.assertRegex(routing.lower(), r"single[- ]token")

    def test_never_touches_backend(self):
        routing = self._routing().lower()
        self.assertIn("backend", routing)
        self.assertIn("frontend only", routing)

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
        self.assertIn("take the lead", wtu)

    def test_routes_single_token_and_ignores_backend(self):
        wtu = self._when_to_use().lower()
        self.assertIn("/design-system", wtu)
        self.assertIn("backend", wtu)

    def test_review_subcommand_advertised(self):
        self.assertIn("award-design review", self._when_to_use())


class TestJudgingCriteria(unittest.TestCase):
    """The Awwwards weighting (40/30/20/10) and the score floors (6.5+ HM,
    7.5+ SOTD) are the contract — drift means the skill's recommendations stop
    matching the judging signal."""

    def test_weights_documented(self):
        body = _body()
        for label, pct in [("Design", 40), ("Usability", 30),
                           ("Creativity", 20), ("Content", 10)]:
            with self.subTest(label=label, pct=pct):
                self.assertRegex(body, rf"{label}\s*{pct}%")

    def test_score_floors_documented(self):
        body = _body()
        self.assertIn("6.5+", body)
        self.assertIn("7.5", body)


class TestPhase0Calibration(unittest.TestCase):
    """Phase 0 loads atmosphere-calibration.md and DECLARES the three dial
    values — silent dials cannot arbitrate later choices."""

    def test_phase_0_loads_calibration_reference(self):
        self.assertIn("references/atmosphere-calibration.md", _phase(0))

    def test_dials_declared_not_internal(self):
        phase0 = _phase(0)
        self.assertRegex(phase0, r"Density / Variance / Motion",
                         "Phase 0 must name the three dials")
        self.assertIn("land in the DESIGN.md Overview prose", phase0,
                      "the dials must land in the DESIGN.md, never stay silent")
        self.assertIn("declared in output", _body().lower(),
                      "the dials are declared in output, never calibrated silently")

    def test_remix_routes_to_reference(self):
        self.assertIn("references/remixing.md", _phase(0),
                      "hybrid briefs must route to references/remixing.md at Phase 0")


class TestPhase3ExternalTruth(unittest.TestCase):
    """Phase 3 is the truth gate: heavy layers resolve through the ladder
    (installed skill → offered install → current docs) before any of their code
    is written, and assets are secured before the build."""

    def test_loads_external_truth_and_imagery(self):
        phase3 = _phase(3)
        self.assertIn("references/external-truth.md", phase3)
        self.assertIn("references/imagery.md", phase3)

    def test_heavy_layers_never_from_memory(self):
        phase3 = _phase(3)
        self.assertIn("never written from training memory", phase3)
        for layer in ("GSAP", "Three.js/R3F", "Lenis", "View Transitions", "Web Audio"):
            with self.subTest(layer=layer):
                self.assertIn(layer, phase3, f"Phase 3 must name the {layer} heavy layer")

    def test_ladder_is_the_gate(self):
        phase3 = _phase(3)
        self.assertRegex(
            phase3, r"installed skill → offered install .* → current docs",
            "Phase 3 must state the three-rung resolution ladder in order")
        self.assertIn("name the source", phase3,
                      "each heavy layer's resolved source must be named")


class TestPhase5Preflight(unittest.TestCase):
    """Phase 5 is the mechanical floor: scanner and detector first, then every
    box, and an unticked box blocks 'done'."""

    def test_loads_preflight_and_runs_scanner(self):
        phase5 = _phase(5)
        self.assertIn("references/preflight.md", phase5)
        self.assertIn("preflight_scan.py", phase5)
        self.assertIn("--archetype", phase5)

    def test_scanner_catches_never_clears(self):
        self.assertIn("it never clears", _phase(5),
                      "the scanner must be framed as catching, never clearing")

    def test_unticked_box_blocks_done(self):
        phase5 = _phase(5)
        self.assertIn("An unticked box means not done", phase5)
        self.assertIn("fix and re-run", phase5)

    def test_verdict_block_is_the_artifact(self):
        self.assertIn("verdict block", _phase(5))


class TestPhase6AntiAnchoring(unittest.TestCase):
    """R2 judges the pixels before it reads the machine output — mechanical
    findings received early anchor the reviewer."""

    def test_reviewer_judges_before_reading_scanner(self):
        phase6 = _phase(6)
        self.assertIn("Anti-anchoring order", phase6)
        self.assertRegex(phase6.lower(), r"pixels first.*mechanical reports second",
                         "the reviewer must form judgment first, read reports second")

    def test_concept_veto_wired(self):
        self.assertIn("concept veto included", _body().lower(),
                      "R2 scoring must include the rubric's concept veto")


if __name__ == "__main__":
    unittest.main()
