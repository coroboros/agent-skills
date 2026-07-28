"""award-design v2 — the component library contract (static checks).

The library's real verification is in-browser (render, interaction, reduced-motion,
a11y) — a JS DOM runner is out of scope for a Python/stdlib repo. What these tests
lock is the drift-prone surface a browser pass cannot re-run on every commit: that
manifest.json and the shipped files stay in sync, and that every component keeps the
structural contract the README promises (one namespaced IIFE, a matching global with
init/destroy, a reduced-motion path, and the DESIGN.md tokens it declares actually
read). A component that quietly drops its reduced-motion branch or renames its global
fails here, not in someone's build."""

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COMPONENTS = REPO_ROOT / "skills" / "award-design" / "assets" / "components"
MANIFEST = COMPONENTS / "manifest.json"


def _manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


class TestManifestShape(unittest.TestCase):
    def test_parses_and_has_components(self):
        m = _manifest()
        self.assertIn("components", m)
        self.assertGreaterEqual(len(m["components"]), 10)

    def test_every_component_has_required_fields(self):
        for c in _manifest()["components"]:
            for field in ("id", "file", "global", "winner", "archetypes",
                          "tokens", "deps", "whenToUse", "init"):
                with self.subTest(component=c.get("id"), field=field):
                    self.assertIn(field, c)


class TestSlotRoles(unittest.TestCase):
    """The anti-monoculture rotation axis: role -> interchangeable component ids.
    The recipe pairs name the winner default; slot_roles is where the next build
    finds a same-role substitute so the reading kit rotates instead of re-shipping
    kinetic-reveal + text-emphasis-fill + semantic-accent + clip-reveal a sixth time.
    Every id must resolve, or the rotation points at a component that doesn't exist."""

    def test_slot_roles_present(self):
        m = _manifest()
        self.assertIn("slot_roles", m)
        for role in ("h1-entrance", "prose-substrate", "media-uncover", "nav"):
            self.assertIn(role, m["slot_roles"])

    def test_every_slot_role_id_resolves(self):
        m = _manifest()
        ids = {c["id"] for c in m["components"]}
        for role, candidates in m["slot_roles"].items():
            if not isinstance(candidates, list):
                continue  # the note string
            for cid in candidates:
                with self.subTest(role=role, component=cid):
                    self.assertIn(cid, ids, f"slot_roles[{role}] names a component with no file")

    def test_reading_kit_slots_have_alternatives(self):
        """A rotation axis with one option cannot rotate — the reading-kit slots
        must offer a real choice."""
        m = _manifest()
        for role in ("h1-entrance", "prose-substrate", "media-uncover"):
            with self.subTest(role=role):
                self.assertGreaterEqual(len(m["slot_roles"][role]), 2)


class TestManifestFilesSync(unittest.TestCase):
    def test_manifest_and_directory_agree(self):
        """No orphan .js on disk and no manifest entry without a file — the two
        must name exactly the same component set."""
        on_disk = {p.name for p in COMPONENTS.glob("*.js")}
        in_manifest = {c["file"] for c in _manifest()["components"]}
        self.assertEqual(on_disk, in_manifest)


class TestComponentContract(unittest.TestCase):
    def setUp(self):
        self.components = _manifest()["components"]

    def test_iife_and_global_export(self):
        for c in self.components:
            src = (COMPONENTS / c["file"]).read_text(encoding="utf-8")
            with self.subTest(component=c["id"]):
                self.assertIn("(function (global)", src)
                # the manifest's declared global is the one the file exports
                self.assertRegex(src, r"global\." + re.escape(c["global"]) + r"\s*=")

    def test_exposes_init_and_destroy(self):
        for c in self.components:
            src = (COMPONENTS / c["file"]).read_text(encoding="utf-8")
            with self.subTest(component=c["id"]):
                self.assertIn("function init", src)
                self.assertIn("destroy", src)

    def test_has_reduced_motion_path(self):
        """Every component that MOVES declares a reduced-motion path. A pure
        surface (glass-card) ships no motion primitive — demanding a dead
        @media block there would violate the no-dead-code rule."""
        motion = ("transition", "animation", "@keyframes", ".animate(",
                  "requestAnimationFrame")
        for c in self.components:
            src = (COMPONENTS / c["file"]).read_text(encoding="utf-8")
            if not any(m in src for m in motion):
                continue
            with self.subTest(component=c["id"]):
                self.assertIn("prefers-reduced-motion", src)

    def test_declared_tokens_are_actually_read(self):
        for c in self.components:
            src = (COMPONENTS / c["file"]).read_text(encoding="utf-8")
            for token in c["tokens"]:
                with self.subTest(component=c["id"], token=token):
                    self.assertIn(token, src)

    def test_has_doc_comment_header(self):
        for c in self.components:
            src = (COMPONENTS / c["file"]).read_text(encoding="utf-8")
            with self.subTest(component=c["id"]):
                self.assertTrue(src.lstrip().startswith("/*"))


class TestSkillWiring(unittest.TestCase):
    """The library is inert unless the build step tells the build to compose
    from it — lock the composition-grammar wiring so a SKILL.md rewrite cannot
    silently strand the components as unused files."""

    def setUp(self):
        self.skill = (REPO_ROOT / "skills" / "award-design" / "SKILL.md").read_text(encoding="utf-8")

    def test_build_step_loads_the_manifest(self):
        self.assertIn("assets/components/manifest.json", self.skill)

    def test_compose_grammar_present(self):
        self.assertIn("Compose with the library", self.skill)
        # the --ad-* token contract and the open-world authoring clause
        self.assertIn("--ad-*", self.skill)
        self.assertIn("author beyond the library at its quality bar", self.skill)


class TestNoAuthoringTraces(unittest.TestCase):
    def test_no_ai_signature(self):
        for p in list(COMPONENTS.glob("*.js")) + [COMPONENTS / "README.md", MANIFEST]:
            text = p.read_text(encoding="utf-8")
            for needle in ("Co-Authored-By", "Generated with", "\U0001f916"):
                with self.subTest(file=p.name, needle=needle):
                    self.assertNotIn(needle, text)


if __name__ == "__main__":
    unittest.main()
