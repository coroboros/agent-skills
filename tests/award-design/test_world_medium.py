"""award-design — the world-medium round (PICCARD UAT 5/10: "aucune immersion…
le skill n'a pas verrouillé les aspects cruciaux de l'immersive cinématique").

The validation build shipped an immersive-cinematic brief as a static-photo
procession + a decorative 2D particle canvas + a 14s autoplay-looping video —
no rendered/scrubbed medium — and passed every gate. Root cause: the medium
arbitration fired only on "a physical action on a world-object", so a scroll/
descend verb bypassed it and routed to displayed real media.

Two fresh-context Opus refuters (generalization + enforceability) converged:
the drafted mechanical gate (WORLD-FLAT/WORLD-INERT) was dropped — it false-fired
on Siena (no WebGL, splash-gate hero) and Lando, could not tell a decorative
canvas from a rendered world (canvas/video pixels are invisible to computed
style), and its stamp-read scoping was gameable (a CSS comment the CSSOM strips,
builder-written). What locks instead, at the judgment/forcing layer:

  L2  the medium decision fires on scroll/scrub/ambient immersive briefs too
  L4  seamless-loop + hero-legibility as driven judgment
  L5' Assessor B fingerprint = presence gate only; liveness = Assessor A driven;
      archetype reviewer-supplied (STAMP-ARCHETYPE-MISMATCH catches a lying stamp);
      the unverified-render cap wired to the ARCHETYPE, not the self-classified verb
  L6  R1 refutes the medium's ambition, not only the spine
"""

import importlib.util
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
REFS = SKILL_DIR / "references"

_spec = importlib.util.spec_from_file_location(
    "preflight_scan", SKILL_DIR / "scripts" / "preflight_scan.py")
assert _spec is not None and _spec.loader is not None
scan = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(scan)


def _ref(rel):
    return (REFS / rel).read_text(encoding="utf-8").lower()


def _skill():
    return (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").lower()


class TestMediumDrivenLaw(unittest.TestCase):
    """L1/L4 — the DNA 'or' gets a fidelity floor: rendered/scrubbed AND driven,
    never displayed; the decorative-canvas-over-static-photos escape is named."""

    def test_dna_medium_is_driven_not_displayed(self):
        imm = _ref("immersive-cinematic.md")
        self.assertIn("the medium is rendered or scrubbed and driven, never displayed", imm)
        self.assertIn("a live-rendered canvas counts only when it is the world", imm)

    def test_seamless_loop_law(self):
        imm = _ref("immersive-cinematic.md")
        self.assertIn("a looping video loops seamlessly, or it does not loop", imm)
        self.assertIn("/video-loop", imm)

    def test_hero_legible_at_a_glance(self):
        imm = _ref("immersive-cinematic.md")
        self.assertIn("the hero frame reads as one legible idea at a glance", imm)


class TestMediumDecisionUngated(unittest.TestCase):
    """L2 — the load-bearing fix: the medium arbitration fires on an immersive
    scroll/scrub/ambient world, not only a physical action on an object."""

    def test_signature_invention_world_trigger(self):
        sig = _ref("signature-invention.md")
        self.assertIn("an immersive world triggers it too", sig)
        self.assertIn("an immersive world is not a product and is never exempt", sig)

    def test_skill_medium_decision_extended(self):
        s = _skill()
        self.assertIn("the brief commits an immersive world", s)
        # Amended 2026-07-17 (imposed-register verdict): film loops joined the driven
        # set — the ban is on displayed stills, not on any specific driven mechanism.
        self.assertIn("rendered, scrubbed, or looping real footage — never displayed stills", s)
        self.assertIn("cinematic film loop", s)

    def test_delegation_trigger_ungated_from_object(self):
        s = _skill()
        self.assertIn("the rendered environment/world an immersive scroll/scrub brief moves through", s)


class TestFingerprintPresenceOnly(unittest.TestCase):
    """L5' — Assessor B's code-read proves presence, not life; the liveness clear
    is Assessor A's driven box (canvas/video pixels invisible to computed style)."""

    def test_signature_invention_presence_gate(self):
        sig = _ref("signature-invention.md")
        self.assertIn("b's code-read is a presence gate, never the liveness clear", sig)

    def test_audit_rubric_presence_gate(self):
        ar = _ref("audit-rubric.md")
        self.assertIn("b's fingerprint is a presence gate, not the liveness clear", ar)

    def test_preflight_medium_box_splits_presence_and_liveness(self):
        pf = _ref("preflight.md")
        self.assertIn("**immersive medium is live, driven**", pf)
        self.assertIn("**looping video loops seamlessly**", pf)


class TestArchetypeReviewerSupplied(unittest.TestCase):
    """L5' — archetype comes from the reviewer, never the builder-written stamp;
    a lying stamp is caught, not obeyed."""

    def test_audit_rubric_reviewer_supplied(self):
        ar = _ref("audit-rubric.md")
        self.assertIn("archetype is reviewer-supplied, never read from the build's stamp", ar)

    def test_preflight_scanner_tag(self):
        pf = _ref("preflight.md")
        self.assertIn("`(scanner: stamp-archetype-mismatch)`", pf)


class TestUnverifiedRenderCapArchetypeWired(unittest.TestCase):
    """L5' — the strongest teeth: the NOT-DONE cap wired to the archetype, so a
    build that self-classifies its verb 'non-interactive' cannot duck it."""

    def test_cap_wired_to_archetype(self):
        pf = _ref("preflight.md")
        self.assertIn("any immersive-cinematic / experimental build, wired to the archetype "
                      "and not to the self-classified verb", pf)


class TestR1RefutesMediumAmbition(unittest.TestCase):
    """L6 — R1 refutes the medium as well as the spine."""

    def test_audit_rubric_medium_ambition(self):
        ar = _ref("audit-rubric.md")
        self.assertIn("r1 refutes the medium's ambition, not only the spine", ar)


class TestStampArchetypeMismatchScanner(unittest.TestCase):
    """The scanner cross-check: reviewer archetype vs the stamp's own field.
    Fires on disagreement, silent on agreement or when no archetype is supplied."""

    STAMP = "/* award-design · immersive-cinematic · abyssal · Archivo · portrait · nav:a · footer:b */"

    def _scan(self, archetype):
        css = self.STAMP + "\n.x{color:oklch(.5 0 0)}\n"
        html = ('<!doctype html><html><body><main><h1>W</h1>'
                '<p>' + " ".join(f"w{i}" for i in range(40)) + '</p></main></body></html>')
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "s.css").write_text(css, encoding="utf-8")
            (Path(tmp) / "index.html").write_text(html, encoding="utf-8")
            findings, _ = scan.scan_paths([tmp], archetype=archetype)
        return {f.rule_id for f in findings}

    def test_mismatch_fires(self):
        self.assertIn("STAMP-ARCHETYPE-MISMATCH", self._scan("editorial"))

    def test_match_silent(self):
        self.assertNotIn("STAMP-ARCHETYPE-MISMATCH", self._scan("immersive-cinematic"))

    def test_no_archetype_silent(self):
        self.assertNotIn("STAMP-ARCHETYPE-MISMATCH", self._scan(""))

    def test_registered_but_not_expected_on_dirty(self):
        """It is a known rule (checklist lockstep) but conditional — never
        required to fire on the bare dirty fixture."""
        self.assertIn("STAMP-ARCHETYPE-MISMATCH", scan.known_rule_ids())
        self.assertNotIn("STAMP-ARCHETYPE-MISMATCH", scan.PROJECT_RULE_IDS)


if __name__ == "__main__":
    unittest.main()
