"""Closed-world build law — encoding pins + scanner behavior.

The AVALANCHE postmortem's law: builders compose, parameterize, and source —
never author machinery at build time; a missing element is a BLOCKED stop with
its gap order filed, never an improvisation, never a downgrade. These tests pin
the law's letter across SKILL.md / preflight.md / imagery.md (including the
strike of the clauses that used to LICENSE build-time authoring), and the
scanner's provenance partition + CW machinery rules on live fixtures."""

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
SKILL_MD = SKILL_DIR / "SKILL.md"
PREFLIGHT_MD = SKILL_DIR / "references" / "preflight.md"
IMAGERY_MD = SKILL_DIR / "references" / "imagery.md"
SCRIPT = SKILL_DIR / "scripts" / "preflight_scan.py"
COMPONENTS = SKILL_DIR / "assets" / "components"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "preflight" / "closed-world"

_spec = importlib.util.spec_from_file_location("preflight_scan_cw", SCRIPT)
assert _spec is not None and _spec.loader is not None
scan = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(scan)

CW_MACHINERY_IDS = (
    "CW-ENGINE", "CW-SHADER", "CW-RAF-LOOP", "CW-CANVAS-DRAW",
    "CW-INPUT-DRIVE", "CW-OBSERVER", "CW-STYLE-DRIVE", "CW-CSS-BEHAVIOR")


def _rule_ids(findings):
    return {f.rule_id for f in findings}


class TestSkillLetter(unittest.TestCase):
    """The law is a strike, not an addition: the old letter instructed
    build-time authoring in three places, and every improviser could cite the
    skill itself. The struck phrases must never return."""

    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")

    def test_permissive_authoring_clauses_are_struck(self):
        for phrase in ("pre-authorized component build orders",
                       "is authored to the same quality floor",
                       "folding it back"):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, self.skill)

    def test_register_carries_the_closed_world_row(self):
        self.assertIn("Builders never author machinery at build time", self.skill)
        self.assertIn("no client clause can authorize build-time machinery", self.skill)

    def test_register_carries_the_asset_provenance_row(self):
        self.assertIn("**Assets carry provenance**", self.skill)
        self.assertIn("never primitives or a stand-in", self.skill)

    def test_phase1_medium_binding(self):
        self.assertIn("The medium names its covering library piece at commit", self.skill)
        self.assertIn("BLOCKED at Phase 1", self.skill)

    def test_phase4_mapping_table_gate(self):
        self.assertIn("The element-to-library mapping table", self.skill)
        self.assertIn("Three legal row types and no fourth", self.skill)
        self.assertIn("FAIL — false gap", self.skill)
        self.assertIn("five-part closest-component analysis", self.skill)

    def test_webgl_delegation_is_parameterization_only(self):
        self.assertIn("scene authoring — new geometry, materials, shaders, camera machinery "
                      "— is closed-world-banned at build time", self.skill)
        self.assertIn("skin surface", self.skill)


class TestPreflightLetter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.preflight = PREFLIGHT_MD.read_text(encoding="utf-8")

    def test_provenance_diff_box(self):
        self.assertIn("**Provenance diff — shipped vs committed, both directions**",
                      self.preflight)
        self.assertIn("never a silent edit", self.preflight)

    def test_curation_box(self):
        self.assertIn("**Asset curation — campaign-grade, the second gate**", self.preflight)
        self.assertIn("orphan sweep", self.preflight)

    def test_blocked_report_template(self):
        self.assertIn("## BLOCKED builds — the stop's terminal artifact", self.preflight)
        self.assertIn("FAIL — false gap", self.preflight)

    def test_blocked_is_not_fail_ratified(self):
        """User-ratified 2026-07-18: a planning stop burns no universe; the
        banked DESIGN.md feeds the post-growth retry via Phase 2 adoption."""
        self.assertIn("**BLOCKED is not a FAIL**", self.preflight)
        self.assertIn("adopting the banked DESIGN.md", self.preflight)

    def test_verdict_block_carries_the_provenance_line(self):
        self.assertIn("**Provenance:** mapping rows", self.preflight)


class TestImageryLetter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.imagery = IMAGERY_MD.read_text(encoding="utf-8")

    def test_generate_rung_demoted_from_first_choice(self):
        self.assertIn("Generate it — atmospheric and secondary slots only", self.imagery)
        self.assertNotIn("First choice — on-brief and rights-clean", self.imagery)

    def test_provenance_section_present(self):
        self.assertIn("## Provenance — the closed world's asset leg", self.imagery)
        self.assertIn("`reference-scene` · `client-pack` · `licensed-media`", self.imagery)
        self.assertIn("an orphan file is a FAIL", self.imagery)

    def test_signature_product_has_no_marketplace_route(self):
        self.assertIn("Signature product objects have no marketplace route", self.imagery)


class TestScannerClosedWorld(unittest.TestCase):
    """Provenance first, content second — the CW rules apply only to
    build-authored files, catch every machinery class, and clear legal wiring,
    token sheets, verbatim library copies, and vendor engines."""

    @classmethod
    def setUpClass(cls):
        dirty, _ = scan.scan_paths([str(FIXTURES / "build-dirty")])
        clean, _ = scan.scan_paths([str(FIXTURES / "build-clean")])
        cls.dirty_ids = _rule_ids(dirty)
        cls.clean_ids = _rule_ids(clean)

    def test_every_machinery_rule_fires_on_build_authored(self):
        for rule_id in CW_MACHINERY_IDS:
            with self.subTest(rule=rule_id):
                self.assertIn(rule_id, self.dirty_ids,
                              f"{rule_id} did not fire on the machinery fixture")

    def test_lib_edit_fires_on_a_modified_library_basename(self):
        self.assertIn("CW-LIB-EDIT", self.dirty_ids)

    def test_legal_wiring_and_tokens_stay_clean(self):
        cw_hits = {rid for rid in self.clean_ids if rid.startswith("CW-")}
        self.assertEqual(set(), cw_hits,
                         "init/config wiring and a token sheet are the legal-wiring letter")

    def test_verbatim_library_copy_is_exempt(self):
        """A byte-identical copy is library-owned: no CW rule, and none of the
        content rules that made the library re-litigate itself in a build scan
        (the SCROLL-LISTENER false-positive class)."""
        source = COMPONENTS / "show-on-scroll-up-nav.js"
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "js"
            dest.mkdir()
            shutil.copyfile(source, dest / source.name)
            findings, _ = scan.scan_paths([tmp])
        ids = _rule_ids(findings)
        self.assertEqual(set(), {rid for rid in ids if rid.startswith("CW-")})
        self.assertNotIn("SCROLL-LISTENER", ids)

    def test_vendor_named_engine_is_out_of_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "three.module.js").write_text(
                "const renderer = new THREE.WebGLRenderer();\n"
                "requestAnimationFrame(loop);\n", encoding="utf-8")
            findings, _ = scan.scan_paths([tmp])
        self.assertEqual(set(), {rid for rid in _rule_ids(findings) if rid.startswith("CW-")})

    def test_excluded_dirs_never_hide_an_edited_library_copy(self):
        """The MARE lesson: an edited nav component under js/vendor/components/
        was invisible to every scan — a library basename is provenance-checked
        wherever it ships."""
        with tempfile.TemporaryDirectory() as tmp:
            hidden = Path(tmp) / "js" / "vendor" / "components"
            hidden.mkdir(parents=True)
            (hidden / "show-on-scroll-up-nav.js").write_text(
                "export function initNav() { return 'patched'; }\n", encoding="utf-8")
            findings, _ = scan.scan_paths([tmp])
        self.assertIn("CW-LIB-EDIT", _rule_ids(findings))

    def test_library_forms_carry_no_bare_100vh_fallbacks(self):
        """The trilemma killer: the library's own bare-100vh fallback lines
        FAILed the preflight a builder could not legally fix — CALDERA resolved
        it by silently editing its copy. The fallbacks are gone (svh/dvh are
        Baseline); a builder-authored form like the rung-1 name-card must not
        reintroduce them."""
        offenders = []
        for css in sorted((COMPONENTS / "forms").glob("*.css")):
            for line_no, line in enumerate(css.read_text(encoding="utf-8").splitlines(), 1):
                if "100vh" in line:
                    offenders.append(f"{css.name}:{line_no}")
        self.assertEqual([], offenders)


if __name__ == "__main__":
    unittest.main()
