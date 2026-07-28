"""Tooling gates — the campaign's red-team scanner round.

Two orders on the pre-flight scanner, each a static proxy with the scanner's
standing bias (it catches, it never clears; REVIEW never FAILs on a guess):
IMG-NATIVE-RES measures every referenced image's shipped px from its file
header and flags a full-bleed / cover-fit / sizes-slot / scrub-sequence
surface under its layout floor — the CALDERA defect (1280×720 frames rendered
up to 2880×1800 device px behind a self-graded asset table); EASE-OVERSHOOT
names every overshoot/elastic easing in build code for the reviewer to judge
against the ONE declared motion register."""

import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
SCRIPT = SKILL_DIR / "scripts" / "preflight_scan.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "preflight" / "tooling"

_spec = importlib.util.spec_from_file_location("preflight_scan_tooling", SCRIPT)
assert _spec is not None and _spec.loader is not None
scan = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(scan)


def _rule_ids(findings):
    return {f.rule_id for f in findings}


def _of_rule(findings, rule_id):
    return [f for f in findings if f.rule_id == rule_id]


class TestImageDimsParsers(unittest.TestCase):
    """The header parsers are the rule's evidence chain — a wrong number here
    turns a machine readout back into an asserted one. Each format is pinned
    on crafted bytes; AVIF is the stated skip (ISOBMFF box-walking exceeds
    stdlib parsing; builds ship a same-dims WebP/JPEG sibling)."""

    def _dims(self, name, data):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / name
            path.write_bytes(data)
            return scan._image_dims(path)

    def test_png_ihdr(self):
        import zlib
        def chunk(tag, body):
            return (struct.pack(">I", len(body)) + tag + body
                    + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF))
        data = (b"\x89PNG\r\n\x1a\n"
                + chunk(b"IHDR", struct.pack(">IIBBBBB", 2400, 1350, 8, 0, 0, 0, 0)))
        self.assertEqual(self._dims("a.png", data), (2400, 1350))

    def test_jpeg_sof(self):
        data = (b"\xff\xd8"
                + b"\xff\xc0" + struct.pack(">HBHHB", 11, 8, 720, 1280, 1) + b"\x01\x11\x00"
                + b"\xff\xd9")
        self.assertEqual(self._dims("a.jpg", data), (1280, 720))

    def test_gif_header(self):
        self.assertEqual(
            self._dims("a.gif", b"GIF89a" + struct.pack("<HH", 640, 360)),
            (640, 360))

    def test_webp_vp8(self):
        payload = b"\x00\x00\x00" + b"\x9d\x01\x2a" + struct.pack("<HH", 1280, 720)
        data = (b"RIFF" + struct.pack("<I", 4 + 8 + len(payload)) + b"WEBP"
                + b"VP8 " + struct.pack("<I", len(payload)) + payload)
        self.assertEqual(self._dims("a.webp", data), (1280, 720))

    def test_webp_vp8l(self):
        bits = (1920 - 1) | ((1080 - 1) << 14)
        dims = bytes([bits & 0xFF, (bits >> 8) & 0xFF, (bits >> 16) & 0xFF,
                      (bits >> 24) & 0x0F])
        payload = b"\x2f" + dims
        data = (b"RIFF" + struct.pack("<I", 4 + 8 + len(payload) + 1) + b"WEBP"
                + b"VP8L" + struct.pack("<I", len(payload)) + payload + b"\x00")
        self.assertEqual(self._dims("a.webp", data), (1920, 1080))

    def test_webp_vp8x(self):
        payload = (b"\x00\x00\x00\x00"
                   + (2880 - 1).to_bytes(3, "little") + (1800 - 1).to_bytes(3, "little"))
        data = (b"RIFF" + struct.pack("<I", 4 + 8 + len(payload)) + b"WEBP"
                + b"VP8X" + struct.pack("<I", len(payload)) + payload)
        self.assertEqual(self._dims("a.webp", data), (2880, 1800))

    def test_avif_is_the_stated_skip(self):
        data = struct.pack(">I", 24) + b"ftypavif" + b"\x00" * 12
        self.assertIsNone(self._dims("a.avif", data))


class TestImgNativeRes(unittest.TestCase):
    """The dirty fixture rebuilds the CALDERA defect in miniature: a low-res
    scrub sequence referenced only through a JS directory literal, a cover-fit
    CSS poster, a full-bleed-figure picture, and an under-shipped sizes slot.
    Every finding is REVIEW (a static proxy never FAILs on a guess) and every
    excerpt carries the px measured from the header — machine numbers for the
    §7 asset-fidelity box, never the builder's own table."""

    @classmethod
    def setUpClass(cls):
        cls.dirty, _ = scan.scan_paths([str(FIXTURES / "img-dirty")])
        cls.hits = _of_rule(cls.dirty, "IMG-NATIVE-RES")

    def test_all_four_underfloor_surfaces_flagged(self):
        self.assertEqual(len(self.hits), 4)

    def test_review_only_never_fail(self):
        self.assertTrue(all(f.severity == scan.REVIEW for f in self.hits))
        self.assertFalse(any(f.severity == scan.FAIL for f in self.dirty),
                         "the img-dirty fixture must carry no FAIL — REVIEW is the ceiling")

    def test_js_directory_sequence_is_caught(self):
        """The CALDERA escape: frames reachable only through a quoted directory
        literal in JS — img/src extraction alone is structurally blind to it."""
        seq = [f for f in self.hits if "scrub sequence" in f.excerpt]
        self.assertEqual(len(seq), 1)
        self.assertIn("12-frame", seq[0].excerpt)
        self.assertIn("320×180", seq[0].excerpt)
        self.assertRegex(seq[0].location, r"main\.js:\d+$")

    def test_findings_carry_measured_px_and_floor(self):
        blob = "\n".join(f.excerpt for f in self.hits)
        for measured in ("320×180", "640×360", "900×506", "400×300"):
            with self.subTest(measured=measured):
                self.assertIn(measured, blob)
        self.assertIn("1920", blob)
        self.assertIn("960", blob, "the sizes-slot floor is computed, not the full-bleed default")

    def test_srcset_variants_group_and_largest_governs(self):
        rim = [f for f in self.hits if "rim" in f.excerpt]
        self.assertEqual(len(rim), 1, "rim.png + rim.webp are one group, one finding")
        self.assertIn("2 variant(s) measured", rim[0].excerpt)
        self.assertIn("900×506", rim[0].excerpt, "the largest shipped variant is the number cited")

    def test_clean_fixture_is_silent(self):
        """Same shapes at or above their floors — the legal high-res case,
        boundary included (the 1920 cover poster does not flag at exactly 1920)."""
        findings, _ = scan.scan_paths([str(FIXTURES / "img-clean")])
        self.assertEqual([], [(f.rule_id, f.excerpt) for f in findings])

    def test_unresolvable_and_remote_refs_stay_silent(self):
        """A hotlink or a missing file cannot be measured — honest silence,
        never a guessed number (UNSPLASH owns the hotlink complaint)."""
        html = ('<!doctype html><html><body>'
                '<section data-ad-form="full-bleed-figure"><figure data-slot="media">'
                '<img src="https://cdn.example.com/big.jpg" width="4000" height="2000" alt="x">'
                '<img src="assets/img/missing.png" width="4000" height="2000" alt="y">'
                '</figure></section></body></html>')
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "index.html").write_text(html, encoding="utf-8")
            findings, _ = scan.scan_paths([tmp])
        self.assertNotIn("IMG-NATIVE-RES", _rule_ids(findings))

    def test_sizes_floor_computation(self):
        """The slot math the AVALANCHE srcsets legalize: media-capped 100vw and
        a vw share of the 1920 audit ceiling."""
        self.assertEqual(scan._sizes_floor("(max-width: 768px) 100vw, 42vw"), 806)
        self.assertEqual(scan._sizes_floor("(max-width: 768px) 100vw, 40vw"), 768)
        self.assertEqual(scan._sizes_floor("100vw"), 1920)
        self.assertEqual(scan._sizes_floor("300px"), 300)


class TestEaseOvershoot(unittest.TestCase):
    """The register verdict is imposed (ONE register page-wide) but lives in
    the DESIGN.md the scanner excludes — so every overshoot/elastic curve is
    named as REVIEW for the reviewer to judge, and nothing FAILs."""

    @classmethod
    def setUpClass(cls):
        cls.dirty, _ = scan.scan_paths([str(FIXTURES / "ease-dirty")])
        cls.hits = _of_rule(cls.dirty, "EASE-OVERSHOOT")

    def test_every_curve_and_token_named(self):
        self.assertEqual(len(self.hits), 6)
        blob = "\n".join(f.excerpt for f in self.hits)
        for named in ("cubic-bezier(0.34, 1.56, 0.64, 1)",
                      "cubic-bezier(0.6, -0.28, 0.735, 0.045)",
                      "cubic-bezier(0.68, -0.55, 0.265, 1.55)",
                      "back.out", "elastic.out", 'type: "spring"'):
            with self.subTest(named=named):
                self.assertIn(named, blob)

    def test_character_is_computed_not_generic(self):
        blob = "\n".join(f.excerpt for f in self.hits)
        self.assertIn("overshoot (travels past the target", blob)
        self.assertIn("anticipation (pulls back", blob)
        self.assertIn("elastic (winds up, then overshoots)", blob)

    def test_review_only_fails_nothing(self):
        self.assertTrue(all(f.severity == scan.REVIEW for f in self.hits))
        self.assertFalse(any(f.severity == scan.FAIL for f in self.dirty))

    def test_register_legal_curves_stay_silent(self):
        """y1/y2 on the [0, 1] boundary are decelerating-register curves —
        the clean fixture holds four, zero findings."""
        findings, _ = scan.scan_paths([str(FIXTURES / "ease-clean")])
        self.assertEqual([], [(f.rule_id, f.excerpt) for f in findings])


class TestToolingRegistration(unittest.TestCase):
    """Both rules are registered — known_rule_ids() feeds the scanner↔checklist
    lockstep test in test_preflight_scan.py, which enforces the preflight.md
    side."""

    def test_new_rules_are_known(self):
        self.assertLessEqual({"IMG-NATIVE-RES", "EASE-OVERSHOOT"},
                             scan.known_rule_ids())


if __name__ == "__main__":
    unittest.main()
