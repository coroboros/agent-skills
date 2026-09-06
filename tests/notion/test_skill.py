"""Structural invariants for the notion skill.

The skill is pure-prompt (no scripts/), so the universal `tests/_meta/`
suite covers frontmatter, marketplace parity, README parity, evals shape,
prose-rules classification. This module pins notion-specific invariants
the meta tests can't see:

- The routing contract — MCP is default, the five CLI-only cases are
  enumerated explicitly (file uploads, Workers, headless/CI, raw API
  discovery, shell piping). Drop one and the skill silently bleeds CLI
  load into the MCP-default path.
- The references table covers all seven authoritative sources from the
  SPEC. Drift here means the model has to invent a URL.
- The four empirical gotchas are present. Adding a fifth or removing
  one is a deliberate decision — pinning the count surfaces silent edits.
- Privacy section forbids token echoing — the skill mentions tokens by
  prefix, so a regression that allows logging them must fail loudly.
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_MD = REPO_ROOT / "skills" / "notion" / "SKILL.md"


def _body() -> str:
    text = SKILL_MD.read_text(encoding="utf-8")
    end = text.find("\n---\n", 4)
    return text[end + 5 :] if end >= 0 else text


class TestRoutingContract(unittest.TestCase):
    """The default-MCP / CLI-exceptions split is the skill's core decision.
    Each of the five CLI-required cases must be named explicitly, otherwise
    the routing question 'is this a CLI case?' has no anchor."""

    CLI_REQUIRED_CASES = (
        "File upload",
        "Notion Workers",
        "Headless",
        "Raw API discovery",
        "Shell piping",
    )

    def test_default_mcp_section_present(self):
        body = _body()
        self.assertIn("### Default — MCP", body,
                      "missing '### Default — MCP' subsection in Routing")

    def test_cli_exceptions_section_present(self):
        body = _body()
        self.assertIn("### Use the `ntn` CLI when its capabilities fit", body,
                      "missing CLI exceptions subsection in Routing")

    def test_each_cli_required_case_named(self):
        body = _body()
        for case in self.CLI_REQUIRED_CASES:
            with self.subTest(case=case):
                self.assertIn(case, body,
                              f"CLI-required case '{case}' not named in Routing")

    def test_default_path_disclaimer_present(self):
        """If none of the five CLI cases apply, the skill must say to stay on the MCP."""
        body = _body()
        self.assertRegex(body, r"available MCP supports.*stay on the MCP",
                         "missing the 'else stay on MCP' fallthrough rule")


class TestReferencesTable(unittest.TestCase):
    """The references table is the skill's escape hatch — it carries every
    URL the body would otherwise have to embed. All seven authoritative
    sources from the SPEC must be there."""

    REQUIRED_REFERENCES = (
        "https://developers.notion.com/guides/mcp/overview",
        "https://developers.notion.com/page/changelog",
        "notion://docs/enhanced-markdown-spec",
        "https://developers.notion.com/cli/get-started/installation",
        "https://developers.notion.com/cli/get-started/authentication",
        "https://developers.notion.com/cli/reference/commands",
        "https://developers.notion.com/reference",
    )

    def test_references_section_present(self):
        body = _body()
        self.assertIn("## References", body, "missing '## References' section")

    def test_every_authoritative_source_cited(self):
        body = _body()
        for ref in self.REQUIRED_REFERENCES:
            with self.subTest(ref=ref):
                self.assertIn(ref, body, f"reference '{ref}' missing from References table")

    def test_per_tool_dsl_deferral_present(self):
        """The 'tool descriptions are the source of truth for DSL syntax' rule
        is what keeps the skill from rotting every time the MCP ships a tool."""
        body = _body()
        self.assertRegex(body, r"tool['']s own description", "missing per-tool DSL deferral note")


class TestGotchas(unittest.TestCase):
    """The five empirical gotchas are the highest-density information in the
    skill — each one prevents a class of silent failure observed in production.
    Drift here means future readers re-discover the same traps."""

    def test_gotchas_section_present(self):
        body = _body()
        self.assertRegex(body, r"## Gotchas", "missing '## Gotchas' section")

    def test_exactly_five_gotcha_items(self):
        """An ordered list of exactly five numbered items in the gotchas section.
        Adding a sixth or removing one is a deliberate decision worth
        re-evaluating in PR — this test surfaces silent edits."""
        body = _body()
        m = re.search(r"## Gotchas[^\n]*\n(.*?)(?=\n## |\Z)", body, re.DOTALL)
        if m is None:
            self.fail("could not locate gotchas section")
        gotchas_block = m.group(1)
        # Match list items at the start of a line: '1. ', '2. ', etc.
        items = re.findall(r"^\d+\.\s+\*\*", gotchas_block, re.MULTILINE)
        self.assertEqual(
            len(items), 5,
            f"expected exactly 5 gotcha items, found {len(items)} — "
            "if this is intentional, update the test to the new count",
        )

    def test_each_gotcha_keyword_present(self):
        """Each of the five gotchas has a distinctive keyword that the model
        needs to see to apply the rule. Pinning these prevents a re-write
        from quietly removing the actionable detail."""
        body = _body()
        keywords = (
            "content_updates[].old_str",        # gotcha #1: active exact-match field
            "bottom of the parent page",        # gotcha #2
            "100 rows",                         # gotcha #3
            "current tool set",                 # gotcha #4 (capability discovery)
            "archived ancestor",                # gotcha #5 (write failure on trashed parent)
        )
        for kw in keywords:
            with self.subTest(keyword=kw):
                self.assertIn(kw, body, f"gotcha keyword '{kw}' missing from body")


class TestPreflight(unittest.TestCase):
    """The pre-flight is what prevents the model from guessing the Markdown
    flavour or the data-source schema. Both items must be present, in order."""

    def test_preflight_section_present(self):
        body = _body()
        self.assertRegex(body, r"## Pre-flight", "missing '## Pre-flight' section")

    def test_preflight_mentions_markdown_spec_resource(self):
        body = _body()
        self.assertIn("notion://docs/enhanced-markdown-spec", body,
                      "pre-flight must reference the enhanced-markdown-spec MCP resource")

    def test_preflight_mentions_schema_fetch(self):
        body = _body()
        self.assertIn("notion-fetch", body,
                      "pre-flight must instruct to notion-fetch the target data source")


class TestPrivacySection(unittest.TestCase):
    """The privacy contract is the only line in the skill that touches secrets.
    A regression that allows token echoing must fail loudly here, not in a
    post-mortem after a leak."""

    def test_privacy_section_present(self):
        body = _body()
        self.assertIn("## Privacy", body, "missing '## Privacy' section")

    def test_token_prefixes_named(self):
        """The skill must name the two real token prefixes so the model can
        recognise them in user-pasted content. The trailing `…` (Unicode
        ellipsis) is the redacted form — never embed a literal token."""
        body = _body()
        self.assertIn("ntn_…", body, "missing 'ntn_…' redacted token prefix")
        self.assertIn("secret_…", body, "missing 'secret_…' redacted token prefix")

    def test_no_literal_token_in_skill(self):
        """A real Notion integration token is `secret_` followed by ≥40
        URL-safe characters. The skill body must contain only the redacted
        ellipsis form, never a literal token."""
        body = _body()
        literal = re.search(r"secret_[A-Za-z0-9_-]{20,}", body)
        self.assertIsNone(
            literal,
            f"literal-looking token found in body: '{literal.group(0) if literal else ''}'. "
            "Use the redacted 'secret_…' form only.",
        )
        literal_ntn = re.search(r"ntn_[A-Za-z0-9_-]{20,}", body)
        self.assertIsNone(
            literal_ntn,
            f"literal-looking ntn token found in body: '{literal_ntn.group(0) if literal_ntn else ''}'. "
            "Use the redacted 'ntn_…' form only.",
        )

    def test_envrc_or_config_path_named(self):
        """Tokens belong in `.envrc` or `~/.config/ntn/`. Both must be
        named so the model knows where to point users."""
        body = _body()
        self.assertIn(".envrc", body, "missing '.envrc' as a token home")
        self.assertIn("~/.config/ntn/", body, "missing '~/.config/ntn/' as a token home")


class TestMaintenance(unittest.TestCase):
    """The maintenance philosophy keeps the skill from turning into a
    mirror of the Notion docs. The 'defer everything else' principle must
    be stated, with the changelog URL as the single source of truth for
    capability evolution."""

    def test_maintenance_section_present(self):
        body = _body()
        self.assertIn("## Maintenance", body, "missing '## Maintenance' section")

    def test_changelog_url_in_maintenance(self):
        body = _body()
        m = re.search(r"## Maintenance[^\n]*\n(.*?)(?=\n## |\Z)", body, re.DOTALL)
        if m is None:
            self.fail("could not locate maintenance section")
        self.assertIn("https://developers.notion.com/page/changelog", m.group(1),
                      "maintenance section must link the changelog as SSOT")


if __name__ == "__main__":
    unittest.main()
