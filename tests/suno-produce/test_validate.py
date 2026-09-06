"""Production-grade tests for skills/suno-produce/scripts/validate.py.

Covers:
- Artifact-type auto-dispatch by filename (TRACK / ALBUM / ARTIST)
- TRACK.md GREEN / YELLOW / RED branches
- ALBUM.md GREEN / YELLOW / RED branches
- ARTIST.md GREEN / RED branches (artist consent contract, slider range)
- Copyright contract: artist-citation patterns RED in Style and Lyrics;
  title-case proper-noun pairs YELLOW in Style with whitelist
- Multi-file directory walk + summary aggregation
- Exit-code contract (0 GREEN, 1 RED, 2 YELLOW)
- JSON report shape (verdict / errors / warnings / info)

Stdlib only. Subprocess-based — exercises the script the way the skill calls it.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[2] / "skills" / "suno-produce"
VALIDATE_SCRIPT = SKILL_DIR / "scripts" / "validate.py"
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def run_validator(*paths):
    """Run validate.py against one or more paths. Returns (returncode, stdout_json, stderr)."""
    proc = subprocess.run(
        [sys.executable, str(VALIDATE_SCRIPT), *[str(p) for p in paths]],
        capture_output=True,
        text=True,
    )
    try:
        report = json.loads(proc.stdout) if proc.stdout.strip() else None
    except json.JSONDecodeError:
        report = None
    return proc.returncode, report, proc.stderr


def find_check(report, check_name):
    """Return the first issue (error or warning) with the given check name, or None."""
    for issue in report.get("errors", []) + report.get("warnings", []):
        if issue.get("check") == check_name:
            return issue
    return None


def find_all_checks(report, check_name):
    """Return every issue (error or warning) with the given check name."""
    return [
        issue
        for issue in report.get("errors", []) + report.get("warnings", [])
        if issue.get("check") == check_name
    ]


class ScriptInvariantsTests(unittest.TestCase):
    """The script itself must be present, executable, and return a useful error on bad input."""

    def test_validate_script_exists(self):
        self.assertTrue(VALIDATE_SCRIPT.exists(), f"missing: {VALIDATE_SCRIPT}")

    def test_missing_path_returns_nonzero(self):
        rc, _, _ = run_validator("/nonexistent/path/that/does/not/exist")
        self.assertNotEqual(rc, 0)

    def test_unsupported_filename_returns_red(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "random.md"
            f.write_text("---\ntitle: x\n---\n", encoding="utf-8")
            rc, report, _ = run_validator(f)
            self.assertEqual(rc, 1)
            self.assertEqual(report["verdict"], "RED")
            self.assertEqual(report["errors"][0]["check"], "unsupported_filename")
            # Expected message must list the three canonical filenames.
            self.assertIn("ARTIST.md", report["errors"][0]["expected"])

    def test_legacy_music_md_filename_is_unsupported(self):
        """MUSIC.md was renamed to ARTIST.md — old filename must not silently work."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "MUSIC.md"
            f.write_text("---\nartist: Legacy\n---\n", encoding="utf-8")
            rc, report, _ = run_validator(f)
            self.assertEqual(rc, 1)
            self.assertEqual(report["verdict"], "RED")
            self.assertEqual(report["errors"][0]["check"], "unsupported_filename")


class TrackValidationTests(unittest.TestCase):
    """TRACK.md validation — Suno v5.5 prompt-bundle rules."""

    def test_track_green_passes(self):
        rc, report, _ = run_validator(FIXTURES_DIR / "track-green" / "TRACK.md")
        self.assertEqual(rc, 0, f"expected GREEN, got {report}")
        self.assertEqual(report["verdict"], "GREEN")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["warnings"], [])
        # info always populates suno_version
        self.assertTrue(any(i["check"] == "suno_version" for i in report["info"]))

    def test_track_yellow_flags_descriptor_count(self):
        rc, report, _ = run_validator(FIXTURES_DIR / "track-yellow" / "TRACK.md")
        self.assertEqual(rc, 2)
        self.assertEqual(report["verdict"], "YELLOW")
        self.assertEqual(report["errors"], [])
        self.assertIsNotNone(find_check(report, "descriptor_count"))

    def test_track_yellow_flags_genre_count(self):
        _, report, _ = run_validator(FIXTURES_DIR / "track-yellow" / "TRACK.md")
        self.assertIsNotNone(find_check(report, "genre_count"))

    def test_track_yellow_flags_conflicting_eras(self):
        _, report, _ = run_validator(FIXTURES_DIR / "track-yellow" / "TRACK.md")
        self.assertIsNotNone(find_check(report, "conflicting_eras"))

    def test_track_yellow_flags_tier3_bracket(self):
        _, report, _ = run_validator(FIXTURES_DIR / "track-yellow" / "TRACK.md")
        self.assertIsNotNone(find_check(report, "tier3_bracket_tag"))

    def test_track_yellow_flags_unrecognized_bracket(self):
        _, report, _ = run_validator(FIXTURES_DIR / "track-yellow" / "TRACK.md")
        # `[My Special Section]` is unrecognized
        unrecognized = find_check(report, "unrecognized_bracket_tag")
        self.assertIsNotNone(unrecognized)
        self.assertIn("special section", unrecognized["value"].lower())

    def test_track_yellow_flags_exclude_count(self):
        _, report, _ = run_validator(FIXTURES_DIR / "track-yellow" / "TRACK.md")
        self.assertIsNotNone(find_check(report, "exclude_count"))

    def test_track_red_blocks_bpm_in_lyrics(self):
        rc, report, _ = run_validator(FIXTURES_DIR / "track-red" / "TRACK.md")
        self.assertEqual(rc, 1)
        self.assertEqual(report["verdict"], "RED")
        self.assertIsNotNone(find_check(report, "bpm_in_lyrics"))

    def test_track_red_blocks_sfx_bracket(self):
        _, report, _ = run_validator(FIXTURES_DIR / "track-red" / "TRACK.md")
        sfx = find_check(report, "sfx_bracket_tag")
        self.assertIsNotNone(sfx)
        self.assertIn("[applause]", sfx["value"])

    def test_track_red_blocks_slider_out_of_range(self):
        _, report, _ = run_validator(FIXTURES_DIR / "track-red" / "TRACK.md")
        self.assertIsNotNone(find_check(report, "slider_range"))

    def test_declared_slider_values_cannot_escape_validation(self):
        base = (FIXTURES_DIR / "track-green" / "TRACK.md").read_text()
        cases = {"-1": "slider_range", "101": "slider_range", "NaN": "slider_value",
                 "inf": "slider_value", "loud": "slider_value", "": "slider_value",
                 "40oops": "slider_value", "9" * 400: "slider_value",
                 "0": None, "100": None, "42.5": None, "+40": None, "40%": None}
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "TRACK.md"
            for value, expected in cases.items():
                with self.subTest(value=value):
                    target.write_text(base.replace("**Weirdness**: 40", f"**Weirdness**: {value}"))
                    rc, report, error = run_validator(target)
                    self.assertEqual(rc, 1 if expected else 0, str(report) + error)
                    if expected:
                        self.assertIsNotNone(find_check(report, expected))
                    else:
                        self.assertEqual(report["errors"], [])


class CopyrightContractTests(unittest.TestCase):
    """Artist-citation patterns are RED. Title-case pairs in Style are YELLOW.

    Both rules trace to article §5.1.5 *Anti-patterns* and SKILL.md Rules
    *Describe the sound, never an artist*. Reasons: (1) legal — copyrighted-
    citation phrasing creates rights exposure, (2) functional — Suno filters
    or ignores artist citations and the model collapses to an averaged tag.
    """

    def test_red_blocks_in_the_style_of_in_style(self):
        rc, report, _ = run_validator(FIXTURES_DIR / "track-citation-red" / "TRACK.md")
        self.assertEqual(rc, 1, f"expected RED, got {report}")
        self.assertEqual(report["verdict"], "RED")
        # At least one citation in Style
        style_hits = find_all_checks(report, "artist_citation_in_style")
        self.assertGreaterEqual(len(style_hits), 1)
        # The phrase wording is captured verbatim in the issue value
        self.assertTrue(
            any("style of" in h["value"].lower() for h in style_hits),
            f"Expected `style of` phrase in: {style_hits}",
        )

    def test_red_blocks_voice_of_in_style(self):
        _, report, _ = run_validator(FIXTURES_DIR / "track-citation-red" / "TRACK.md")
        style_hits = find_all_checks(report, "artist_citation_in_style")
        self.assertTrue(
            any("voice of" in h["value"].lower() or "voice like" in h["value"].lower()
                for h in style_hits),
            f"Expected `voice of` or `voice like` in: {style_hits}",
        )

    def test_red_blocks_a_la_in_style(self):
        _, report, _ = run_validator(FIXTURES_DIR / "track-citation-red" / "TRACK.md")
        style_hits = find_all_checks(report, "artist_citation_in_style")
        self.assertTrue(
            any("la " in h["value"].lower() for h in style_hits),
            f"Expected `à la` or `a la` citation in: {style_hits}",
        )

    def test_red_blocks_citation_in_lyrics(self):
        _, report, _ = run_validator(FIXTURES_DIR / "track-citation-red" / "TRACK.md")
        lyrics_hits = find_all_checks(report, "artist_citation_in_lyrics")
        self.assertGreaterEqual(len(lyrics_hits), 1)

    def test_red_blocks_multiword_possessive_in_style(self):
        """`<Name>'s sound|style|voice|era` is RED when name is multi-word."""
        _, report, _ = run_validator(FIXTURES_DIR / "track-citation-red" / "TRACK.md")
        style_hits = find_all_checks(report, "artist_citation_in_style")
        self.assertTrue(
            any("phil collins" in h["value"].lower() and "sound" in h["value"].lower()
                for h in style_hits),
            f"Expected `Phil Collins's sound` possessive in: {style_hits}",
        )

    def test_singleword_possessive_does_not_fire(self):
        """`London's sound`, `Spring's hit` are not artist citations — must not fire RED.

        The possessive regex requires the captured name to be multi-word so location/
        season/country names with possessives do not trip RED. Real artist names are
        almost always multi-word; single-word artists (Madonna, Drake) get caught by
        the other four citation patterns instead.
        """
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "TRACK.md"
            f.write_text(
                "---\nsuno_version: v5.5\ntitle: London Test\nbpm: 92\n"
                "voice_profile: null\ncustom_model: null\ncreated: 2026-05-10\n"
                "revised: null\n---\n\n# London Test\n\n## Suno prompt block\n\n"
                "### Style of Music\n```text\nIndie folk capturing London's sound, "
                "Spring's mood, fingerpicked acoustic, soft male vocal, 92 BPM\n```\n\n"
                "### Lyrics\n```text\n[Intro]\n[Fingerpicked acoustic]\n```\n\n"
                "### Exclude Styles\n```text\n808s\n```\n\n## Sliders\n"
                "- **Weirdness**: 40\n\n## Voice / Custom Model\nNone.\n\n"
                "## Rationale\nSingle-word possessives must not fire RED.\n\n"
                "## Iteration log\n- v0 (2026-05-10): single-word possessive sanity\n",
                encoding="utf-8",
            )
            _, report, _ = run_validator(f)
            citation_hits = find_all_checks(report, "artist_citation_in_style")
            possessive_hits = [h for h in citation_hits if "'s" in h["value"] or "’s" in h["value"]]
            self.assertEqual(
                possessive_hits, [],
                f"Single-word possessives must not RED. Got: {possessive_hits}",
            )

    def test_expanded_whitelist_phrases_pass_clean(self):
        """`Snare Drum`, `French House`, `Vocal Chop` and friends — must not YELLOW.

        Verifies the expanded NON_ARTIST_PHRASES whitelist covers common Suno
        descriptors capitalized in the wild.
        """
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "TRACK.md"
            f.write_text(
                "---\nsuno_version: v5.5\ntitle: Whitelist Coverage Test\nbpm: 124\n"
                "voice_profile: null\ncustom_model: null\ncreated: 2026-05-10\n"
                "revised: null\n---\n\n# Whitelist Coverage Test\n\n## Suno prompt block\n\n"
                "### Style of Music\n```text\nFrench House, 2020s analog, hypnotic, "
                "Snare Drum, Synth Pad, Vocal Chop, Tape Echo, 124 BPM\n```\n\n"
                "### Lyrics\n```text\n[Intro]\n[Filtered arp]\n```\n\n"
                "### Exclude Styles\n```text\n808s\n```\n\n## Sliders\n"
                "- **Weirdness**: 45\n\n## Voice / Custom Model\nNone.\n\n"
                "## Rationale\nWhitelist expansion smoke test.\n\n"
                "## Iteration log\n- v0 (2026-05-10): expanded whitelist\n",
                encoding="utf-8",
            )
            _, report, _ = run_validator(f)
            self.assertIsNone(
                find_check(report, "artist_name_in_style"),
                f"Expanded whitelist phrases must not YELLOW. Got: {report.get('warnings')}",
            )

    def test_red_fix_message_includes_legal_and_functional_reasons(self):
        _, report, _ = run_validator(FIXTURES_DIR / "track-citation-red" / "TRACK.md")
        style_hits = find_all_checks(report, "artist_citation_in_style")
        joined_fix = " ".join(h["fix"].lower() for h in style_hits)
        # Must mention rights exposure (legal) and Suno filtering (functional)
        self.assertIn("rights", joined_fix)
        self.assertIn("filter", joined_fix)

    def test_yellow_flags_title_case_pair_in_style(self):
        rc, report, _ = run_validator(FIXTURES_DIR / "track-titlecase-yellow" / "TRACK.md")
        self.assertEqual(rc, 2, f"expected YELLOW, got {report}")
        self.assertEqual(report["verdict"], "YELLOW")
        name_hit = find_check(report, "artist_name_in_style")
        self.assertIsNotNone(name_hit)
        self.assertIn("Phil Collins", name_hit["value"])

    def test_whitelisted_phrases_pass_clean(self):
        """`Pedal Steel`, `Sub Bass`, etc. are legitimate descriptors — must not flag."""
        rc, report, _ = run_validator(FIXTURES_DIR / "track-whitelist-green" / "TRACK.md")
        self.assertEqual(rc, 0, f"expected GREEN, got {report}")
        self.assertEqual(report["verdict"], "GREEN")
        self.assertIsNone(find_check(report, "artist_name_in_style"))
        self.assertIsNone(find_check(report, "artist_citation_in_style"))


class AlbumValidationTests(unittest.TestCase):
    """ALBUM.md validation — concept + tracklist consistency."""

    def test_album_green_passes(self):
        rc, report, _ = run_validator(FIXTURES_DIR / "album-green" / "ALBUM.md")
        self.assertEqual(rc, 0, f"expected GREEN, got {report}")
        self.assertEqual(report["verdict"], "GREEN")
        self.assertEqual(report["errors"], [])

    def test_album_green_info_records_tracklist_count(self):
        _, report, _ = run_validator(FIXTURES_DIR / "album-green" / "ALBUM.md")
        info = next((i for i in report["info"] if i["check"] == "tracklist_count"), None)
        self.assertIsNotNone(info)
        self.assertEqual(info["value"], 5)

    def test_album_yellow_flags_arc_label_missing(self):
        rc, report, _ = run_validator(FIXTURES_DIR / "album-yellow" / "ALBUM.md")
        self.assertEqual(rc, 2)
        self.assertEqual(report["verdict"], "YELLOW")
        # Arc lists Opening + Climax only — missing Development and Closing
        arc_warnings = [w for w in report["warnings"] if w["check"] == "arc_label_missing"]
        self.assertGreaterEqual(len(arc_warnings), 2)
        labels_flagged = {w["value"] for w in arc_warnings}
        self.assertIn("Development", labels_flagged)
        self.assertIn("Closing", labels_flagged)

    def test_album_yellow_flags_malformed_tracklist_line(self):
        _, report, _ = run_validator(FIXTURES_DIR / "album-yellow" / "ALBUM.md")
        self.assertIsNotNone(find_check(report, "tracklist_line_format"))

    def test_album_red_blocks_track_count_mismatch(self):
        rc, report, _ = run_validator(FIXTURES_DIR / "album-red" / "ALBUM.md")
        self.assertEqual(rc, 1)
        self.assertEqual(report["verdict"], "RED")
        mismatch = find_check(report, "track_count_mismatch")
        self.assertIsNotNone(mismatch)
        self.assertIn("frontmatter=5", mismatch["value"])
        self.assertIn("tracklist=2", mismatch["value"])

    def test_album_red_blocks_invalid_release_format(self):
        _, report, _ = run_validator(FIXTURES_DIR / "album-red" / "ALBUM.md")
        rf = find_check(report, "release_format")
        self.assertIsNotNone(rf)
        self.assertEqual(rf["value"], "BadFormat")

    def test_album_red_blocks_missing_concept_section(self):
        _, report, _ = run_validator(FIXTURES_DIR / "album-red" / "ALBUM.md")
        missing = [
            e for e in report["errors"]
            if e["check"] == "missing_section" and e["value"] == "Concept"
        ]
        self.assertEqual(len(missing), 1)


class ArtistValidationTests(unittest.TestCase):
    """ARTIST.md validation — artist identity + voice consent contract."""

    def test_artist_green_passes(self):
        rc, report, _ = run_validator(FIXTURES_DIR / "artist-green" / "ARTIST.md")
        self.assertEqual(rc, 0, f"expected GREEN, got {report}")
        self.assertEqual(report["verdict"], "GREEN")
        self.assertEqual(report["errors"], [])

    def test_artist_green_info_records_voice_profile(self):
        _, report, _ = run_validator(FIXTURES_DIR / "artist-green" / "ARTIST.md")
        vp_info = next((i for i in report["info"] if i["check"] == "voice_profile"), None)
        self.assertIsNotNone(vp_info)
        self.assertEqual(vp_info["value"], "studio-a-tenor")

    def test_artist_red_blocks_voice_without_consent(self):
        rc, report, _ = run_validator(FIXTURES_DIR / "artist-red" / "ARTIST.md")
        self.assertEqual(rc, 1)
        self.assertEqual(report["verdict"], "RED")
        self.assertIsNotNone(find_check(report, "voice_consent_required"))

    def test_artist_red_blocks_slider_bias_out_of_range(self):
        _, report, _ = run_validator(FIXTURES_DIR / "artist-red" / "ARTIST.md")
        sb = find_check(report, "slider_bias_range")
        self.assertIsNotNone(sb)
        self.assertIn("weirdness_default", sb["value"])


class DirectoryWalkTests(unittest.TestCase):
    """Multi-file directory walk + summary aggregation."""

    def setUp(self):
        # Stage three GREEN artifacts in an isolated tree.
        self.tmpdir = tempfile.mkdtemp()
        self.tmp = Path(self.tmpdir)
        shutil.copy(FIXTURES_DIR / "track-green" / "TRACK.md", self.tmp / "TRACK.md")
        shutil.copy(FIXTURES_DIR / "album-green" / "ALBUM.md", self.tmp / "ALBUM.md")
        shutil.copy(FIXTURES_DIR / "artist-green" / "ARTIST.md", self.tmp / "ARTIST.md")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_directory_all_green_exits_zero(self):
        rc, report, _ = run_validator(self.tmp)
        self.assertEqual(rc, 0)
        self.assertEqual(report["summary"]["total"], 3)
        self.assertEqual(report["summary"]["green"], 3)
        self.assertEqual(report["summary"]["yellow"], 0)
        self.assertEqual(report["summary"]["red"], 0)

    def test_directory_with_red_exits_one(self):
        # Replace ARTIST.md with the RED fixture
        shutil.copy(FIXTURES_DIR / "artist-red" / "ARTIST.md", self.tmp / "ARTIST.md")
        rc, report, _ = run_validator(self.tmp)
        self.assertEqual(rc, 1)
        self.assertGreaterEqual(report["summary"]["red"], 1)

    def test_directory_with_yellow_only_exits_two(self):
        # Replace TRACK.md with YELLOW fixture (others stay GREEN)
        shutil.copy(FIXTURES_DIR / "track-yellow" / "TRACK.md", self.tmp / "TRACK.md")
        rc, report, _ = run_validator(self.tmp)
        self.assertEqual(rc, 2)
        self.assertGreaterEqual(report["summary"]["yellow"], 1)
        self.assertEqual(report["summary"]["red"], 0)


class JSONReportShapeTests(unittest.TestCase):
    """The JSON report contract is stable for downstream consumers."""

    def test_single_file_shape(self):
        _, report, _ = run_validator(FIXTURES_DIR / "track-green" / "TRACK.md")
        for key in ("verdict", "file", "errors", "warnings", "info"):
            self.assertIn(key, report)
        self.assertIn(report["verdict"], ("GREEN", "YELLOW", "RED"))
        self.assertIsInstance(report["errors"], list)
        self.assertIsInstance(report["warnings"], list)
        self.assertIsInstance(report["info"], list)

    def test_issue_shape_has_required_fields(self):
        _, report, _ = run_validator(FIXTURES_DIR / "track-red" / "TRACK.md")
        for issue in report["errors"]:
            for key in ("check", "line", "value", "expected", "fix"):
                self.assertIn(key, issue, f"issue missing {key}: {issue}")


if __name__ == "__main__":
    unittest.main()
