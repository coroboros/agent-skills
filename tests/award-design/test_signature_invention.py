"""award-design — the signature must be bespoke, not a category pick.

The skill already demands a memorable signature and compares to the winner, yet
plateaus at a competent scroll-reveal: it supplied a *menu* of categories and let
a generic signature be filed as a known gap. This hardening forces the invention —
a method (derive the mechanic from the world's verb), a hard R1 gate (a category
signature regenerates, never files), two-altitude forcing on the signature itself,
and buildability removed as an excuse.

Each assertion would FAIL before this hardening."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFS = SKILL_DIR / "references"


def _read(name):
    return (REFS / name).read_text(encoding="utf-8")


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


def _phase(n):
    m = re.search(rf"^## Phase {n} — .*?\n(.*?)(?=^## )", _body(), re.DOTALL | re.MULTILINE)
    assert m is not None, f"## Phase {n} section missing"
    return m.group(1)


def _review_mode():
    m = re.search(r"^## Review mode.*?(?=^## )", _body(), re.DOTALL | re.MULTILINE)
    assert m is not None, "Review mode section missing"
    return m.group(0)


class TestSignatureInventionReference(unittest.TestCase):
    def setUp(self):
        self.sig = _read("signature-invention.md")
        self.low = self.sig.lower()

    def test_file_exists(self):
        self.assertTrue((REFS / "signature-invention.md").is_file(),
                        "references/signature-invention.md missing")

    def test_category_vs_bespoke_distinction(self):
        self.assertTrue("category" in self.low and "bespoke" in self.low,
                        "the reference must draw the category vs bespoke distinction")

    def test_bespoke_test_is_binding(self):
        self.assertIn("bespoke test", self.low)
        self.assertTrue("regenerate" in self.low and ("never file" in self.low or "not file" in self.low),
                        "a category signature regenerates, it is never filed as a gap")

    def test_worlds_verb_method(self):
        self.assertIn("verb", self.low,
                      "the derivation method is the verb the world invites the user to do")
        # names the object→turn mapping (the fragrance-bottle case, and more)
        self.assertTrue("turn" in self.low and "move through" in self.low,
                        "the taxonomy maps world kinds to verbs (turn, move through, run, disturb, use)")

    def test_ambition_before_buildability(self):
        self.assertTrue("before buildability" in self.low or "ambition is set" in self.low,
                        "ambition is fixed at concept; a heavy mechanic routes through the WebGL delegation")


class TestSignatureWiring(unittest.TestCase):
    def test_imperative_one_is_bespoke_not_a_menu(self):
        imp = _read("award-imperatives.md").lower()
        self.assertIn("bespoke test", imp,
                      "imperative #1 must carry the bespoke test")
        self.assertIn("category", imp,
                      "imperative #1 must name scroll-reveal/parallax/magnetic as categories, not signatures")
        self.assertIn("signature-invention.md", imp,
                      "imperative #1 must route to the invention method")

    def test_phase1_loads_and_forces_the_signature(self):
        p1 = _phase(1)
        self.assertIn("signature-invention.md", p1,
                      "Phase 1 must load the signature-invention method")
        low = p1.lower()
        self.assertIn("bespoke test", low,
                      "the Phase 1 signature step must apply the bespoke test")
        self.assertIn("verb", low,
                      "the signature is derived from the world's verb")

    def test_phase1_artifact_includes_signature_rejected_default(self):
        p1 = _phase(1).lower()
        # the artifact line names the signature's own rejected default + its verb
        self.assertTrue("signature's own rejected default" in p1 or "rejected default" in p1,
                        "the Phase 1 artifact must include the signature's rejected default")

    def test_r1_gates_a_category_signature(self):
        review = _review_mode().lower()
        self.assertIn("bespoke test", review,
                      "R1 must refute the signature against the bespoke test")
        self.assertTrue("off-track" in review and "regenerate" in review,
                        "a category signature is OFF-TRACK at R1 — regenerate, never file")


class TestLetterMonogramTell(unittest.TestCase):
    def test_letter_monogram_beside_wordmark_is_a_tell(self):
        ap = _read("anti-patterns.md").lower()
        self.assertIn("letter-monogram", ap,
                      "a letter-monogram glued to the spelled-out wordmark must be named as a tell")
        self.assertTrue("stands alone" in ap or "standing alone" in ap or "not both" in ap,
                        "the fix: the monogram stands alone or the wordmark does, never both locked together")


if __name__ == "__main__":
    unittest.main()
