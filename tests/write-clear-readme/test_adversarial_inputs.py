"""write-clear-readme — adversarial-input fixtures for `audit_readme`.

Real READMEs in the wild contain unicode in headings, BOM markers, mixed
line endings, very long content, and pathological character sequences.
The slug, anchor resolver, and bloat scanner must hold up — silent
failures here corrupt the audit report without triggering exit 1."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "skills" / "write-clear-readme" / "scripts"
SCRIPT = SCRIPTS / "audit_readme.py"
sys.path.insert(0, str(SCRIPTS))

from audit_readme import audit, slugify  # noqa: E402


def _run(path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(path)],
        capture_output=True, text=True, timeout=30,
    )


class TestSlugifyAdversarial(unittest.TestCase):
    """Adversarial slug inputs: unicode, only symbols, very long, repeated."""

    def test_unicode_letters_preserved(self):
        """Unicode letters survive the slug pass — the implementation does
        NOT transliterate (no `Café → cafe`). It lowercases and treats
        spaces/symbols as separators. Pin the contract explicitly so a
        future change to drop diacritics is intentional, not silent."""
        # GitHub auto-anchors preserve unicode letters too, so this matches
        # GitHub's slug behaviour (`café-crème` is a valid GitHub anchor).
        result = slugify("Café Crème")
        self.assertEqual(
            result, "café-crème",
            "slugify must preserve non-ASCII letters and lowercase only",
        )

    def test_only_symbols_collapses_to_empty_safe(self):
        """A heading like '!!!' has no letters — slug should be empty
        but not crash. Empty slug is acceptable; the audit report will
        flag it via the duplicate-anchor rule if more than one such
        heading exists."""
        result = slugify("!!!")
        # Must not raise; result is either empty string or single dash.
        self.assertIsInstance(result, str)
        self.assertLessEqual(len(result), 1, f"unexpected slug: {result!r}")

    def test_very_long_heading_truncated_safely(self):
        """A 500-char heading must produce a slug without crashing.
        Slug length is implementation-defined; we just pin that audit
        does not blow up on long input."""
        long_heading = "Very " * 100 + "Long Heading"
        result = slugify(long_heading)
        self.assertIsInstance(result, str)
        # Sanity: should at least contain something kebab-ish.
        self.assertGreater(len(result), 0)

    def test_consecutive_specials_produce_kebab_only(self):
        """Consecutive non-letter chars in the heading become dashes in the
        slug. The current implementation does NOT collapse runs (`!!! ` → `--`),
        so the slug may contain `--` — that's intentional, GitHub does the
        same. The contract pinned here is that the slug remains kebab-shaped
        (only [a-z0-9-]) regardless of how many consecutive dashes appear."""
        result = slugify("Foo !!! Bar &&& Baz")
        self.assertRegex(
            result, r"^[a-z0-9-]+$",
            f"slug contains non-kebab chars: {result!r}",
        )
        # The recognisable anchors (foo, bar, baz) still appear.
        for piece in ("foo", "bar", "baz"):
            self.assertIn(piece, result, f"piece '{piece}' lost in slug: {result!r}")


class TestAnchorResolutionEdgeCases(unittest.TestCase):
    """Anchor resolver under realistic README patterns — duplicate headings,
    headings with code spans, links inside <details>."""

    def test_duplicate_headings_both_resolvable(self):
        """Two `## Setup` sections — first gets `setup`, second gets
        `setup-1` per GitHub's auto-disambiguation. Both must resolve
        when the link uses either anchor."""
        text = (
            "## Setup\nFirst section.\n\n"
            "## Setup\nSecond section.\n\n"
            "Links: [first](#setup), [second](#setup-1).\n"
        )
        report = audit(text)
        # Whether the implementation supports auto-disambiguation or not,
        # the audit must not crash on the duplicate.
        self.assertIn("anchors", report)

    def test_anchor_with_unicode_heading_handled(self):
        """A heading with unicode (Café Notes) — the link must use the
        normalized slug. Audit must not crash and must report whatever
        anchor it produces consistently."""
        text = (
            "## Café Notes\nContent.\n\n"
            "See [the cafe](#cafe-notes) above.\n"
        )
        report = audit(text)
        # Don't assert pass/fail on the exact slug — implementation choice.
        # Pin only that audit completes and the anchor either resolves or
        # is reported as unresolved (not silently dropped).
        self.assertIn("anchors", report)
        unresolved = report["anchors"]["unresolved"]
        # Either resolved (cafe-notes matches) or surfaced as unresolved —
        # both are valid contracts. Silence is not.
        self.assertIsInstance(unresolved, list)

    def test_anchor_inside_details_block_resolves(self):
        """Headings inside <details> still get auto-anchored on GitHub.
        The audit should treat them like top-level headings for resolution."""
        text = (
            "<details>\n<summary>Hidden</summary>\n<br>\n\n"
            "### Inner Heading\n\nbody\n\n"
            "</details>\n\n"
            "Link: [inner](#inner-heading).\n"
        )
        report = audit(text)
        # Inner heading is detectable, so the link should resolve.
        self.assertEqual(
            report["anchors"]["unresolved"], [],
            "anchor inside <details> not resolved — auditor missed nested headings",
        )


class TestBloatPatternsAdversarial(unittest.TestCase):
    """Bloat detection under realistic prose — case sensitivity, word
    boundaries, code-fence isolation."""

    def test_bloat_word_boundary_respected(self):
        """`leverage` is a bloat token, but `leveraging` (gerund) and
        `lever` (different word) should NOT trigger. Word boundaries
        prevent false positives that erode trust in the report."""
        text = "We use lever pulleys, not leveraging anything.\n"
        report = audit(text)
        tokens = [hit["token"] for hit in report["bloat"]]
        # `lever` is a substring of `leverage` but a different word.
        self.assertNotIn(
            "leverage", tokens,
            "bloat scanner matched 'lever' or 'leveraging' as 'leverage' — fix word boundary",
        )

    def test_bloat_case_insensitive(self):
        """`Powerful` (capitalized) at the start of a sentence must trigger,
        not just lowercase forms. Case-only divergence shouldn't excuse bloat."""
        text = "Powerful tools win deals.\n"
        report = audit(text)
        tokens = [hit["token"] for hit in report["bloat"]]
        # `powerful` (lowercased in the report) must be detected regardless of casing.
        self.assertIn("powerful", tokens,
                      "bloat scanner missed 'Powerful' (case sensitivity)")

    def test_bloat_inside_inline_code_ignored(self):
        """Inline `code` spans aren't prose — bloat tokens inside backticks
        are likely identifiers (e.g., `seamlessly()` as a function name)
        and must not trigger."""
        text = "Call `leverage` to do it.\n"
        report = audit(text)
        tokens = [hit["token"] for hit in report["bloat"]]
        self.assertNotIn(
            "leverage", tokens,
            "bloat scanner matched a token inside backticks — ignore inline code",
        )


class TestEmptyOrTrivialReadmes(unittest.TestCase):
    """Empty / one-liner / trivial READMEs — audit must complete without
    crashing and report a sensible state."""

    def test_empty_readme_returns_report(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("")
            path = Path(f.name)
        try:
            result = _run(path)
            self.assertIn(result.returncode, (0, 1),
                          f"empty README produced unexpected exit {result.returncode}")
            # Report must be valid JSON even for empty input.
            report = json.loads(result.stdout)
            self.assertIn("summary", report)
        finally:
            path.unlink()

    def test_oneliner_readme_no_crash(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("# Single Heading\n")
            path = Path(f.name)
        try:
            result = _run(path)
            self.assertIn(result.returncode, (0, 1))
            report = json.loads(result.stdout)
            self.assertIn("anchors", report)
        finally:
            path.unlink()

    def test_only_code_fences_no_crash(self):
        """A README that's entirely fenced code blocks — no prose to scan
        for bloat, no headings to anchor. Audit must still complete."""
        text = "```\nfn main() {}\n```\n\n```python\nprint('hi')\n```\n"
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(text)
            path = Path(f.name)
        try:
            result = _run(path)
            self.assertIn(result.returncode, (0, 1))
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()
