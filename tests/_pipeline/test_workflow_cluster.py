"""Pipeline contract: forge → apex.

forge documents the path convention it produces; apex documents consuming it
via -f. A realistic spec-shaped fixture (3 workstreams, dep chain) must pass
validate_spec.py — pinning the producer→validator contract end-to-end.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _contracts import CLUSTERS, read_skill_md  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "skills" / "forge" / "scripts"))
from validate_spec import (  # noqa: E402
    build_graph,
    find_cycle,
    split_blocks,
    validate_workstream,
)


WORKFLOW = CLUSTERS["workflow"]


class TestProducerConsumerPaths(unittest.TestCase):
    """v2 contract (repo-conventions.md § Pipeline chaining): a producer
    saves to ~/.claude/output/{project}/{skill}/{skill}-{slug}.md and prints
    that fully-expanded absolute path; the consumer is handed that explicit
    path verbatim — no reconstruction, no inference, no glob. Pinned: forge's
    documented path shape appears in its own bridge to apex, apex's -f example
    consumes it, and the SSOT states the explicit-path rule. Drift in the path
    shape or the rule breaks the chain in this diff."""

    RULE = (
        Path(__file__).resolve().parent.parent.parent
        / ".agents" / "rules" / "repo-conventions.md"
    ).read_text(encoding="utf-8")

    def test_forge_bridges_apex_explicit_path(self):
        forge_md = read_skill_md(WORKFLOW["producer"])
        # forge's bridge inlines the explicit forge artifact path, never a
        # bare reconstructed name.
        self.assertIn("forge/forge-{slug}.md", forge_md)
        self.assertNotIn("-f forge.md", forge_md)

    def test_apex_consumes_forge_explicit_path(self):
        apex_md = read_skill_md(WORKFLOW["consumer"])
        self.assertIn("forge/forge-{slug}.md", apex_md)
        self.assertNotIn("-f forge.md", apex_md)

    def test_forge_documents_canonical_filename(self):
        forge_md = read_skill_md(WORKFLOW["producer"])
        # forge commits to the {skill}-{slug}.md filename convention.
        self.assertIn("forge-{slug}.md", forge_md)

    def test_ssot_documents_explicit_path_contract(self):
        # The keystone is "explicit path, verbatim — no magic", not
        # bare-name resolution.
        self.assertIn("explicit path", self.RULE)
        self.assertIn("verbatim", self.RULE)
        self.assertRegex(self.RULE, r"reconstruct|never magic")
        self.assertIn("fail loud", self.RULE)


class TestSpecValidatorAcceptsRealisticOutput(unittest.TestCase):
    """A forge code-bearing artifact shaped like real output (3 workstreams,
    dep chain, P0/P1 priorities, M/L complexity) must pass validate_spec.py —
    pins the producer→validator contract end-to-end."""

    SPEC_FIXTURE = (
        "# Spec: Auth System\n\n"
        "## Decision\n\n- **Chosen:** session cookies — simplest fit.\n\n"
        "## Workstreams\n\n"
        "### WS-1: Database schema\n\n"
        "| Priority | P0 |\n| Complexity | M |\n| Depends on | — |\n\n"
        "**Acceptance criteria:**\n\n- [ ] Schema migrated\n\n"
        "### WS-2: Auth endpoints\n\n"
        "| Priority | P0 |\n| Complexity | L |\n| Depends on | WS-1 |\n\n"
        "**Acceptance criteria:**\n\n- [ ] Login + logout work\n\n"
        "### WS-3: Integration tests\n\n"
        "| Priority | P1 |\n| Complexity | M |\n| Depends on | WS-2 |\n\n"
        "**Acceptance criteria:**\n\n- [ ] All paths green\n\n"
    )

    def test_split_blocks_recognises_three(self):
        blocks = split_blocks(self.SPEC_FIXTURE)
        self.assertEqual([b[0] for b in blocks], ["WS-1", "WS-2", "WS-3"])

    def test_each_workstream_validates(self):
        blocks = split_blocks(self.SPEC_FIXTURE)
        ids = {b[0] for b in blocks}
        for ws_id, body in blocks:
            with self.subTest(ws=ws_id):
                errors = validate_workstream(ws_id, body, ids)
                self.assertEqual(errors, [], f"WS {ws_id}: {errors}")

    def test_dep_chain_no_cycle(self):
        blocks = split_blocks(self.SPEC_FIXTURE)
        graph = build_graph(blocks)
        # WS-2 → WS-1, WS-3 → WS-2: linear chain, no cycle.
        self.assertEqual(find_cycle(graph), [])


if __name__ == "__main__":
    unittest.main()
