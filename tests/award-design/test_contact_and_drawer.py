"""award-design — the contact round (CLINCH UAT 7.2-7.4). Adversarially built in
three passes: a first refuter proved the medium arbitration was never in the
build's DESIGN.md (the report narrated it — narrated compliance one layer up);
a generalization refuter walked all nine archetypes and the verb space (the
missing taxonomy, DNA subordination, the drawer "toujours" over-fit); an
enforceability refuter read detector.js and proved every draft law escaped (the
hover-only floor cannot see contact or canvas — the CONTACT-GLOBAL-SQUASH
inversion, the open-drawer census, and the two-boundary arbitration anchor are
its closing forms). These lock: the verb-class routing table, the timestamped
arbitration + declared-vs-code check, contact locality, the press/strike input
substrate, the instrument form with its no-cursor carve-out and dual invitation,
and the drawer floor/ceiling split.

Honesty note: prose-presence regression locks. The bite lives in the pre-build
R1 verdict quote, Assessor B's artifact reads, the driven §8 boxes, and the
detector's census — no test here verifies a build obeyed a judgment rule."""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
REFS = SKILL_DIR / "references"


def _read(rel):
    return (REFS / rel).read_text(encoding="utf-8").lower()


class TestVerbClassTaxonomy(unittest.TestCase):
    def test_routing_table_named_once(self):
        si = _read("signature-invention.md")
        self.assertIn("**the verb classes — the routing table.**", si)
        for cls in ("scroll/scrub", "hover/reveal", "drag/steer",
                    "press/strike", "turn/rotate", "type/command",
                    "ambient/no-input"):
            with self.subTest(cls=cls):
                self.assertIn(cls, si)
        self.assertIn("a law applied outside its class is a category error", si)


class TestTimestampedArbitration(unittest.TestCase):
    def test_pre_build_anchor(self):
        si = _read("signature-invention.md")
        self.assertIn("**the arbitration is timestamped:**", si)
        self.assertIn("quoted verbatim in the pre-build r1 verdict", si)
        self.assertIn("a retroactive paste, not a decision", si)

    def test_declared_vs_code_check(self):
        ar = _read("audit-rubric.md")
        self.assertIn("declared-vs-code check", ar)
        self.assertIn("the arbitration is fiction", ar)

    def test_roster_box_never_self_ticked(self):
        pf = _read("preflight.md")
        self.assertIn("**medium arbitration anchored**", pf)
        self.assertIn("this box is never self-ticked alone", pf)

    def test_scrubbed_media_exempt(self):
        self.assertIn(
            "displayed or scrubbed media are exempt",
            _read("signature-invention.md"))


class TestContactLocality(unittest.TestCase):
    def test_the_law(self):
        si = _read("signature-invention.md")
        self.assertIn("**contact locality — the paper-cutout law.**", si)
        self.assertIn("local to the contact point", si)
        self.assertIn("at least one secondary", si)

    def test_register_subordination(self):
        si = _read("signature-invention.md")
        self.assertIn(
            "a raw register's contact is hard, stepped, channel-split", si)

    def test_enforcement_split_is_honest(self):
        si = _read("signature-invention.md")
        self.assertIn(
            "canvas-side deformation fidelity is assessor-a driven judgment", si)
        self.assertIn("contact-global-squash", si)

    def test_media_routing_three_buckets(self):
        si = _read("signature-invention.md")
        self.assertIn("**media routing by verb class**", si)
        self.assertIn("contact-at-arbitrary-point", si)
        self.assertIn("rigidly-turned", si)

    def test_anti_pattern_tell(self):
        self.assertIn("**the paper cutout**", _read("anti-patterns.md"))


class TestInputSubstrate(unittest.TestCase):
    def test_scoped_to_press_strike(self):
        ix = _read("interaction-signatures.md")
        self.assertIn(
            "**the substrate answers a discrete verb's input — press/strike "
            "class only.**", ix)
        self.assertIn(
            "drag/steer and scroll/scrub verbs stay on the signature surface",
            ix)
        self.assertIn("hover remains a first-class substrate verb", ix)

    def test_misfire_guard(self):
        ix = _read("interaction-signatures.md")
        self.assertIn("the quiet verb response never hijacks an activation", ix)

    def test_reviewer_samples_the_census(self):
        pf = _read("preflight.md")
        self.assertIn("sampled by the reviewer from the detector's substrate "
                      "census", pf)
        self.assertIn("never the builder's shortlist", pf)


class TestInstrumentAndInvitation(unittest.TestCase):
    def test_instrument_form_with_carve_out(self):
        ix = _read("interaction-signatures.md")
        self.assertIn("**the instrument form and the dual invitation.**", ix)
        self.assertIn("**verb's instrument form**", ix)
        self.assertIn(
            "the deliberate no-cursor stands where the mechanic is the pointer",
            ix)

    def test_dual_path_invitation(self):
        ix = _read("interaction-signatures.md")
        self.assertIn("a cursor-only invitation abandons the touch audience", ix)
        pf = _read("preflight.md")
        self.assertIn("the beat is also driven under touch emulation", pf)


class TestDrawerFloorCeiling(unittest.TestCase):
    def test_split_in_navigation_patterns(self):
        nav = _read("navigation-patterns.md")
        self.assertIn(
            "**the drawer floor and the scene ceiling — split, never "
            "conflated.**", nav)
        self.assertIn("never a dead list", nav)
        self.assertIn("the floor is the always; the scene is the register's "
                      "call", nav)

    def test_open_drawer_census(self):
        nav = _read("navigation-patterns.md")
        self.assertIn("the detector runs with the drawer open", nav)
        pf = _read("preflight.md")
        self.assertIn("**drawer floor — every link driven, with the drawer "
                      "open**", pf)

    def test_anti_pattern_tell(self):
        self.assertIn("**the dead-list drawer**", _read("anti-patterns.md"))


if __name__ == "__main__":
    unittest.main()
