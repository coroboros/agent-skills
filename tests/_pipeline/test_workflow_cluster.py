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
    """Each producer's output path convention is documented in the consumer's
    SKILL.md — drift would silently break the pipeline."""

    def test_spec_documents_brainstorm_output_path(self):
        spec_md = read_skill_md(WORKFLOW["consumer"])
        self.assertIn(".claude/output/brainstorm/", spec_md)
        self.assertIn("brainstorm.md", spec_md)

    def test_apex_documents_spec_output_path(self):
        apex_md = read_skill_md(WORKFLOW["tertiary"])
        self.assertIn(".claude/output/spec/", apex_md)
        self.assertIn("spec.md", apex_md)

    def test_brainstorm_documents_canonical_filename(self):
        brainstorm_md = read_skill_md(WORKFLOW["producer"])
        # brainstorm must commit to the canonical filename convention.
        self.assertIn("brainstorm.md", brainstorm_md)


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
