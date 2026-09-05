"""award-design — the post-TILT round (user UAT 6.9). Two user-named gaps, three
adjudicated causes: the skill's own WebGL rule steered a pinball build away from
its playable machine (the delegation was archetype-locked while
signature-invention prescribed the 3D path for real objects — a contradiction);
the verb-derivation had no primacy rule (the build led with the connoisseur's
nudge instead of the plunger the world is built around); and the carry law was
satisfiable by a persistent emblem while the signature mechanic stayed
hero-locked. These lock the closings: the medium-scoped delegation, the
primary-verb rule, the written playable-object decision, the echo-as-mechanic
law, the driven discovery beat, and the committed scroll-texture slot.

Honesty note: these are prose-presence regression locks. The bite lives in the
driven preflight §8 boxes and the next UAT; no test here can verify a build
obeyed a judgment rule."""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
REFS = SKILL_DIR / "references"

ARCHETYPES = ("minimalist", "brutalist", "editorial", "bold-maximal",
              "immersive-cinematic", "experimental", "corporate-luxury",
              "bento-card", "spatial-organic")


def _read(rel):
    return (REFS / rel).read_text(encoding="utf-8").lower()


def _skill():
    return (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").lower()


def _gate(rel):
    return (REFS / "gate" / rel).read_text(encoding="utf-8").lower()


class TestPrimaryVerb(unittest.TestCase):
    def test_rule_in_signature_invention(self):
        si = _read("signature-invention.md")
        self.assertIn("the primary verb, not the cleverest edge", si)
        self.assertIn("the one the world is *built around*", si)
        self.assertIn(
            "an edge-verb signature takes a written justification", si)

    def test_rule_in_the_contract_and_the_method(self):
        self.assertIn("**signature** (verb · medium · trigger", _skill(),
                      "the contract block names the signature by its verb")
        self.assertIn("ask what the world invites the user to **do**",
                      _read("signature-invention.md"))

    def test_r1_check_in_rubric(self):
        ar = _read("audit-rubric.md")
        self.assertIn("the primary-verb check (r1)", ar)
        self.assertIn("an unjustified edge-verb signature is off-track", ar)


class TestPlayableObjectDecision(unittest.TestCase):
    def test_decision_written_with_arbiter(self):
        si = _read("signature-invention.md")
        self.assertIn("the playable-object decision — written, arbitrated", si)
        for arbiter in ("premise veto", "archetype's dna", "measured perf budget"):
            with self.subTest(arbiter=arbiter):
                self.assertIn(arbiter, si)
        self.assertIn(
            "a silent css-metaphor default is a skipped decision", si)

    def test_signature_invention_carries_the_decision(self):
        self.assertIn("**the medium is chosen for desirability, not safety.**",
                      _read("signature-invention.md"))


class TestMediumScopedDelegation(unittest.TestCase):
    def test_steering_is_default_not_prohibition(self):
        mp = _read("motion-palette.md")
        self.assertIn("this steers the *default*, never a prohibition", mp)
        self.assertIn("playable-object decision", mp)

    def test_delegation_contract_names_scope_and_perf(self):
        w = _read("ingredients/web3d-for-sites.md")
        self.assertIn("quoted verbatim plus the matching cheat", w)
        self.assertIn("never co-write a file", w)
        self.assertIn("meets the measured perf budget through the poster-first path", w)
        self.assertIn("via the poster-first path", _read("signature-invention.md"))


class TestEchoLaw(unittest.TestCase):
    def test_echo_is_the_mechanic_transformed(self):
        ix = _read("interaction-signatures.md")
        self.assertIn(
            "an echo is the mechanic transformed, never an emblem re-placed", ix)
        self.assertIn("two non-hero sections", ix)
        self.assertIn("presence alone is not an echo", ix)

    def test_spectacle_is_stateful_and_replayable(self):
        ix = _read("interaction-signatures.md")
        self.assertIn("the spectacle is stateful and replayable", ix)
        self.assertIn(
            "a fire-once spectacle that leaves a static frame after its first "
            "play is an entrance, not a signature", ix)

    def test_echo_law_at_its_home(self):
        si = _read("signature-invention.md")
        self.assertIn("the dominant bespoke moment carries the make-or-break surface", si)
        self.assertIn("recur down the scroll", si)

    def test_richness_is_budget_scoped(self):
        self.assertIn("richness stays inside the budget by construction",
                      _read("interaction-signatures.md"))


class TestDiscoveryBeat(unittest.TestCase):
    def test_driven_at_r2(self):
        ar = _read("audit-rubric.md")
        self.assertIn("the discovery beat is driven fresh", ar)
        self.assertIn("nameable within 10 s", ar)


class TestScrollTextureSlot(unittest.TestCase):
    def test_density_read_names_the_channels(self):
        r = _gate("review.md")
        self.assertIn("selected archetype", r)
        self.assertIn("missing declared choreography", r)

    def test_every_palette_carries_the_rows(self):
        for a in ARCHETYPES:
            body = _read(f"{a}.md")
            with self.subTest(archetype=a):
                # tier 2 loads by heading — each channel row is its own `##` section
                self.assertIn("## scroll texture", body)
                self.assertIn("## idle band", body)
                self.assertIn("channel calibration —", body)


class TestScopedStaticRead(unittest.TestCase):
    def test_static_read_is_archetype_conditional(self):
        ar = _read("audit-rubric.md")
        self.assertIn(
            "the static and driven reads are both taken, scoped by archetype", ar)
        self.assertIn("is the invitation visible at rest?", ar)


if __name__ == "__main__":
    unittest.main()
