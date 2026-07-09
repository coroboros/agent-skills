"""award-design — the Ninety-North-test hardening: the distributed signature over a
live low-amplitude substrate, the interaction/text-effects palettes, the hide-reveal
secondary, native-control + cursor bans, OKLCH/rem forcing, the footer seam, and the
final code-craft review gate.

The Ninety North build was a beautiful hero over a page that went static below it, with
a native <select>, a not-allowed cursor, a hard image-cut into a grey footer, and a
restating eyebrow. Its DESIGN.md prescribed the native control and the cursor itself.
These lock the fixes, and the research that reframed 'one signature' into a distributed
signature over a live substrate (amplitude, not coverage, is what restraint lowers)."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFS = SKILL_DIR / "references"


def _read(rel):
    return (REFS / rel).read_text(encoding="utf-8").lower()


def _skill():
    return SKILL_MD.read_text(encoding="utf-8").lower()


def _phase(n):
    body = SKILL_MD.read_text(encoding="utf-8")
    m = re.search(rf"^## Phase {n} — .*?\n(.*?)(?=^## )", body, re.DOTALL | re.MULTILINE)
    assert m is not None, f"## Phase {n} section missing"
    return m.group(1).lower()


class TestNewPalettesExist(unittest.TestCase):
    def test_three_new_reference_files_exist(self):
        for f in ("interaction-signatures.md", "text-effects.md", "code-review.md"):
            self.assertTrue((REFS / f).is_file(), f"references/{f} missing")


class TestDistributedSignature(unittest.TestCase):
    def test_signature_invention_carries_distributed_model(self):
        si = _read("signature-invention.md")
        self.assertIn("distributed signature over a live interaction substrate", si)
        self.assertIn("two or three quieter section-tied echoes", si)

    def test_interaction_file_states_two_layers(self):
        ix = _read("interaction-signatures.md")
        self.assertIn("distributed signature over a live substrate", ix)
        self.assertIn("low-amplitude interaction substrate", ix)

    def test_restraint_lowers_amplitude_not_coverage(self):
        ix = _read("interaction-signatures.md")
        self.assertIn("restraint lowers amplitude, never coverage", ix)

    def test_skill_judging_criteria_reframed(self):
        body = _skill()
        self.assertIn("distributed signature", body)
        # the old "one signature interaction (not scattered micro-animations)" is gone
        self.assertNotIn("one signature interaction (not scattered micro-animations)", body)

    def test_skill_phase4_motion_has_coverage_not_amplitude(self):
        p4 = _phase(4)
        self.assertIn("full coverage at minimal amplitude", p4)

    def test_anti_pattern_bans_dead_after_hero(self):
        ap = _read("anti-patterns.md")
        self.assertIn("never let the page die after it", ap)


class TestHideRevealSecondary(unittest.TestCase):
    def test_interaction_file_forces_earned_secondary(self):
        ix = _read("interaction-signatures.md")
        self.assertIn("never left static", ix)
        self.assertIn("@media (hover: hover)", ix)
        self.assertIn("never left permanently unreachable", ix)

    def test_anti_pattern_static_decorative_secondary(self):
        ap = _read("anti-patterns.md")
        self.assertIn("static decorative secondary", ap)


class TestTextEffects(unittest.TestCase):
    def test_safe_framing(self):
        tx = _read("text-effects.md")
        self.assertIn("emphasize already-legible text", tx)
        self.assertIn("the finished state is the css default", tx)

    def test_browser_reality(self):
        tx = _read("text-effects.md")
        self.assertIn("not baseline", tx)
        self.assertIn("gsap splittext + scrolltrigger", tx)

    def test_semantic_accent_layer(self):
        tx = _read("text-effects.md")
        self.assertIn("semantic accent", tx)

    def test_preflight_gates_text_emphasis_legible_first(self):
        pf = _read("preflight.md")
        self.assertIn("text emphasis is legible-first", pf)


class TestNativeControlsAndCursor(unittest.TestCase):
    def test_ship_ready_floor_uplifts_controls_and_bans_not_allowed(self):
        sr = _read("ship-ready-floor.md")
        self.assertIn("form controls uplifted", sr)
        self.assertIn("never `not-allowed`", sr)

    def test_anti_pattern_bans_native_controls_and_cursor(self):
        ap = _read("anti-patterns.md")
        self.assertIn("native form controls left unstyled", ap)
        self.assertIn("native blocked/disabled cursor", ap)

    def test_design_md_never_prescribes_a_tell(self):
        dm = _read("design-md-anatomy.md")
        self.assertIn("never prescribes a tell", dm)

    def test_preflight_gates_uplift_and_cursor(self):
        # the mechanical control/cursor check lives once, in the §9 code-craft home
        pf = _read("preflight.md")
        self.assertIn("native-control + cursor lint", pf)


class TestOklchAndRem(unittest.TestCase):
    def test_ship_ready_floor_forces_oklch_and_rem(self):
        sr = _read("ship-ready-floor.md")
        self.assertIn("colour in oklch, sizing in rem", sr)


class TestFooterSeam(unittest.TestCase):
    def test_imagery_extends_seam_to_footer(self):
        im = _read("imagery.md")
        self.assertIn("footer boundary is the one most often missed", im)


class TestEyebrowRestatesH1(unittest.TestCase):
    def test_anti_pattern_and_preflight(self):
        ap = _read("anti-patterns.md")
        self.assertIn("restates the h1", ap)
        self.assertIn("the default is no kicker", ap)


class TestMotifFiller(unittest.TestCase):
    def test_anti_pattern_motif_two_sided(self):
        ap = _read("anti-patterns.md")
        self.assertIn("motif repeated into filler", ap)


class TestCodeReviewGate(unittest.TestCase):
    def test_code_review_file_overrides_design_md(self):
        cr = _read("code-review.md")
        self.assertIn("override the design.md", cr)

    def test_five_checks_present(self):
        cr = _read("code-review.md")
        self.assertIn("token-drift / ssot", cr)
        self.assertIn("oklch + rem enforcement", cr)
        self.assertIn("native-control + cursor lint", cr)
        self.assertIn("lifecycle refutation", cr)
        self.assertIn("in the viewport", cr)

    def test_skill_phase5_runs_code_craft(self):
        p5 = _phase(5)
        self.assertIn("code-craft review", p5)
        self.assertIn("overrides the design.md", p5)

    def test_preflight_has_code_craft_section(self):
        pf = _read("preflight.md")
        self.assertIn("code-craft review", pf)
        self.assertIn("native-control + cursor lint", pf)


class TestPalettesWiredIntoProtocol(unittest.TestCase):
    def test_phase3_and_phase4_load_new_palettes(self):
        for n in (3, 4):
            body = _phase(n)
            self.assertIn("references/interaction-signatures.md", body, f"phase {n}")
            self.assertIn("references/text-effects.md", body, f"phase {n}")

    def test_motion_palette_cross_links_siblings(self):
        mp = _read("motion-palette.md")
        self.assertIn("text-effects.md", mp)
        self.assertIn("interaction-signatures.md", mp)


if __name__ == "__main__":
    unittest.main()
