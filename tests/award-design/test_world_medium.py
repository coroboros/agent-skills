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
style), and scoping it off anything the builder writes into the artifact was
gameable. What locks instead, at the judgment/forcing layer:

  L2  the medium decision fires on scroll/scrub/ambient immersive briefs too
  L4  seamless-loop + hero-legibility as driven judgment
  L5' the code-read fingerprint = presence gate only; liveness = driven;
      archetype reviewer-supplied through `--archetype`, never read from the build;
      the unverified-render cap wired to the ARCHETYPE, not the self-classified verb
  L6  R1 refutes the medium's ambition, not only the spine
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
REFS = SKILL_DIR / "references"


def _ref(rel):
    return (REFS / rel).read_text(encoding="utf-8").lower()


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

    def test_medium_decision_extended(self):
        # The medium commitment is mapped by world kind — objects, space and
        # process all route to a driven medium, never to displayed stills.
        sig = _ref("signature-invention.md")
        self.assertIn("a world of objects invites a real-time 3d scene", sig)
        self.assertIn("a world of process invites a scrubbed sequence", sig)

    def test_stills_procession_named_precedent_free(self):
        self.assertIn("a stills procession dressed with décor has zero winner "
                      "precedent on an immersive brief", _ref("signature-invention.md"))


class TestFingerprintPresenceOnly(unittest.TestCase):
    """L5' — the code-read proves presence, not life; the liveness clear is the
    driven box (canvas/video pixels invisible to computed style)."""

    def test_signature_invention_presence_gate(self):
        sig = _ref("signature-invention.md")
        self.assertIn("the code-read is a presence gate, never the liveness clear", sig)

    def test_audit_rubric_presence_gate(self):
        ar = _ref("audit-rubric.md")
        self.assertIn("the code-read fingerprint is a presence gate, not the liveness clear", ar)

    def test_preflight_drives_medium_and_loop(self):
        pf = _ref("preflight.md")
        self.assertIn("looping video watched through ≥2 cycles", pf)
        self.assertIn("no seam jump", pf)


class TestArchetypeReviewerSupplied(unittest.TestCase):
    """L5' — archetype comes from the reviewer through `--archetype`, never from
    anything the audited build writes about itself."""

    def test_audit_rubric_reviewer_supplied(self):
        ar = _ref("audit-rubric.md")
        self.assertIn("archetype is reviewer-supplied, never read from the build", ar)

    def test_preflight_names_the_only_source(self):
        pf = _ref("preflight.md")
        self.assertIn("the archetype is reviewer-supplied — `--archetype` is its only source", pf)


class TestUnverifiedRenderCapArchetypeWired(unittest.TestCase):
    """L5' — the strongest teeth: the NOT-DONE cap wired to the archetype, so a
    build that self-classifies its verb 'non-interactive' cannot duck it."""

    def test_cap_wired_to_archetype(self):
        pf = _ref("gate/review.md")
        self.assertIn("any immersive-cinematic or experimental build, caps at "
                      "**not done — unverified render**", pf.lower())


class TestR1RefutesMediumAmbition(unittest.TestCase):
    """L6 — R1 refutes the medium as well as the spine."""

    def test_audit_rubric_medium_ambition(self):
        ar = _ref("audit-rubric.md")
        self.assertIn("r1 refutes the medium's ambition, not only the spine", ar)


# Adjudicated (v3 stamp retirement): TestStampArchetypeMismatchScanner cross-checked
# `--archetype` against the stamp's own archetype field. With no stamp to read, the
# reviewer's `--archetype` is the sole source and there is nothing left to disagree
# with it — the invariant it protected is held by TestArchetypeReviewerSupplied above.


if __name__ == "__main__":
    unittest.main()
