"""Pipeline contract: brainstorm → spec → apex.

Each skill documents the path convention it produces or consumes. A realistic
spec.md fixture (3 workstreams, dep chain) must pass validate_spec.py — pinning
the producer→validator contract end-to-end.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _contracts import CLUSTERS, read_skill_md  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "skills" / "spec" / "scripts"))
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
    path verbatim — no reconstruction, no inference, no glob. Pinned: the
    producer's documented path shape appears in the consumer's bridge, and
    the SSOT states the explicit-path rule. Drift in the path shape or the
    rule breaks the chain in this diff."""

    RULE = (
        Path(__file__).resolve().parent.parent.parent
        / ".claude" / "rules" / "repo-conventions.md"
    ).read_text(encoding="utf-8")

    def test_spec_bridges_brainstorm_explicit_path(self):
        spec_md = read_skill_md(WORKFLOW["consumer"])
        # spec's bridge inlines the brainstorm explicit path shape, never a
        # bare reconstructed name.
        self.assertIn("brainstorm/brainstorm-{slug}.md", spec_md)
        self.assertNotIn("-f brainstorm.md", spec_md)

    def test_apex_bridges_spec_explicit_path(self):
        apex_md = read_skill_md(WORKFLOW["tertiary"])
        self.assertIn("spec/spec-{slug}.md", apex_md)
        self.assertNotIn("-f spec.md", apex_md)

    def test_brainstorm_documents_canonical_filename(self):
        brainstorm_md = read_skill_md(WORKFLOW["producer"])
        # brainstorm commits to the {skill}-{slug}.md filename convention.
        self.assertIn("brainstorm-{slug}.md", brainstorm_md)

    def test_ssot_documents_explicit_path_contract(self):
        # The keystone is "explicit path, verbatim — no magic", not
        # bare-name resolution.
        self.assertIn("explicit path", self.RULE)
        self.assertIn("verbatim", self.RULE)
        self.assertRegex(self.RULE, r"reconstruct|never magic")
        self.assertIn("fail loud", self.RULE)


class TestSpecValidatorAcceptsRealisticOutput(unittest.TestCase):
    """A spec.md shaped like real consumer output (3 workstreams, dep chain,
    P0/P1 priorities, M/L complexity) must pass validate_spec.py — pins the
    producer→validator contract end-to-end."""

    SPEC_FIXTURE = (
        "# Auth System Spec\n\n"
        "## Summary\n\nBuild authentication infrastructure.\n\n"
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
