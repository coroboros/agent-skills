"""Tests for validate_spec.py — schema, dependency graph, cycle detection.

The validator runs as a subprocess for the CLI tests and as imported functions
for graph-level tests (cycle detection, build_graph).
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "skills" / "spec" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_spec import build_graph, find_cycle, split_blocks, validate_workstream  # noqa: E402

SCRIPT = SCRIPTS / "validate_spec.py"


def _spec(workstreams_md, header="# Test spec\n\n## Summary\n\nFoo.\n\n"):
    return f"{header}## Workstreams\n\n{workstreams_md}\n"


def _ws(ws_id, *, priority="P1", complexity="M", deps="—", ac=True):
    block = (
        f"### {ws_id}: example\n\n"
        f"| Priority | {priority} |\n"
        f"| Complexity | {complexity} |\n"
        f"| Depends on | {deps} |\n\n"
    )
    if ac:
        block += "**Acceptance criteria:**\n\n- [ ] something\n\n"
    return block


def _write_temp(text):
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8")
    f.write(text)
    f.close()
    return Path(f.name)


def _run(path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True
    )


class TestSplitBlocks(unittest.TestCase):
    def test_splits_three_workstreams(self):
        content = _spec(_ws("WS-1") + _ws("WS-2") + _ws("WS-3"))
        blocks = split_blocks(content)
        self.assertEqual([b[0] for b in blocks], ["WS-1", "WS-2", "WS-3"])

    def test_no_workstreams_section_returns_empty(self):
        self.assertEqual(split_blocks("# Just a header\n"), [])

    def test_empty_workstreams_section_returns_empty(self):
        content = "## Workstreams\n\n## Other\n"
        self.assertEqual(split_blocks(content), [])

    def test_stops_at_next_h2(self):
        """Workstreams stops at the next ## section."""
        content = _spec(_ws("WS-1")) + "\n## Risks\n\n### WS-99: not a workstream\n"
        blocks = split_blocks(content)
        self.assertEqual([b[0] for b in blocks], ["WS-1"])


class TestValidateWorkstream(unittest.TestCase):
    def test_valid_returns_no_errors(self):
        block = _ws("WS-1")
        errors = validate_workstream("WS-1", block, {"WS-1"})
        self.assertEqual(errors, [])

    def test_missing_priority_flagged(self):
        # Block without Priority row
        block = (
            "### WS-1: bad\n\n"
            "| Complexity | M |\n| Depends on | — |\n\n"
            "**Acceptance criteria:**\n\n- [ ] x\n\n"
        )
        errors = validate_workstream("WS-1", block, {"WS-1"})
        self.assertTrue(any("Priority" in e for e in errors))

    def test_invalid_priority_value_flagged(self):
        block = _ws("WS-1", priority="P9")
        errors = validate_workstream("WS-1", block, {"WS-1"})
        self.assertTrue(any("Priority" in e for e in errors))

    def test_missing_complexity_flagged(self):
        block = (
            "### WS-1: bad\n\n"
            "| Priority | P0 |\n| Depends on | — |\n\n"
            "**Acceptance criteria:**\n\n- [ ] x\n\n"
        )
        errors = validate_workstream("WS-1", block, {"WS-1"})
        self.assertTrue(any("Complexity" in e for e in errors))

    def test_complexity_xl_accepted(self):
        block = _ws("WS-1", complexity="XL")
        errors = validate_workstream("WS-1", block, {"WS-1"})
        self.assertEqual(errors, [])

    def test_missing_acceptance_criteria_flagged(self):
        block = _ws("WS-1", ac=False)
        errors = validate_workstream("WS-1", block, {"WS-1"})
        self.assertTrue(any("Acceptance" in e for e in errors))

    def test_unknown_dependency_flagged(self):
        block = _ws("WS-2", deps="WS-99")
        errors = validate_workstream("WS-2", block, {"WS-1", "WS-2"})
        self.assertTrue(any("WS-99" in e for e in errors))

    def test_no_dependency_dash_accepted(self):
        block = _ws("WS-1", deps="—")
        errors = validate_workstream("WS-1", block, {"WS-1"})
        self.assertEqual(errors, [])


class TestBuildGraph(unittest.TestCase):
    def test_no_deps_empty_lists(self):
        blocks = split_blocks(_spec(_ws("WS-1") + _ws("WS-2")))
        graph = build_graph(blocks)
        self.assertEqual(graph["WS-1"], [])
        self.assertEqual(graph["WS-2"], [])

    def test_single_dep_captured(self):
        blocks = split_blocks(_spec(_ws("WS-1") + _ws("WS-2", deps="WS-1")))
        graph = build_graph(blocks)
        self.assertEqual(graph["WS-2"], ["WS-1"])

    def test_multiple_deps_captured(self):
        blocks = split_blocks(_spec(
            _ws("WS-1") + _ws("WS-2") + _ws("WS-3", deps="WS-1, WS-2")
        ))
        graph = build_graph(blocks)
        self.assertEqual(set(graph["WS-3"]), {"WS-1", "WS-2"})


class TestFindCycle(unittest.TestCase):
    def test_dag_no_cycle(self):
        graph = {"A": ["B"], "B": ["C"], "C": []}
        self.assertEqual(find_cycle(graph), [])

    def test_two_node_cycle_detected(self):
        graph = {"A": ["B"], "B": ["A"]}
        cycle = find_cycle(graph)
        self.assertGreater(len(cycle), 0)

    def test_self_loop_detected(self):
        graph = {"A": ["A"]}
        cycle = find_cycle(graph)
        self.assertGreater(len(cycle), 0)

    def test_three_node_cycle_detected(self):
        graph = {"A": ["B"], "B": ["C"], "C": ["A"]}
        cycle = find_cycle(graph)
        self.assertGreater(len(cycle), 0)

    def test_diamond_no_false_positive(self):
        """A→B, A→C, B→D, C→D — no cycle despite multiple paths to D."""
        graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        self.assertEqual(find_cycle(graph), [])


class TestCLI(unittest.TestCase):
    def test_no_args_exits_1(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("usage", r.stderr)

    def test_missing_file_exits_1(self):
        r = _run("/tmp/_does_not_exist_spec.md")
        self.assertEqual(r.returncode, 1)
        self.assertIn("error=file-missing", r.stdout)

    def test_no_workstreams_section_exits_1(self):
        path = _write_temp("# Header\n\n## Other\n")
        try:
            r = _run(path)
            self.assertEqual(r.returncode, 1)
            self.assertIn("error=no-workstreams-section", r.stdout)
        finally:
            path.unlink()

    def test_too_few_workstreams_exits_1(self):
        path = _write_temp(_spec(_ws("WS-1") + _ws("WS-2")))
        try:
            r = _run(path)
            self.assertEqual(r.returncode, 1)
            self.assertIn("ws-count-out-of-range", r.stdout)
        finally:
            path.unlink()

    def test_too_many_workstreams_exits_1(self):
        ws = "".join(_ws(f"WS-{i}") for i in range(1, 9))  # 8 workstreams
        path = _write_temp(_spec(ws))
        try:
            r = _run(path)
            self.assertEqual(r.returncode, 1)
            self.assertIn("ws-count-out-of-range", r.stdout)
        finally:
            path.unlink()

    def test_valid_spec_exits_0(self):
        ws = _ws("WS-1") + _ws("WS-2", deps="WS-1") + _ws("WS-3", deps="WS-2")
        path = _write_temp(_spec(ws))
        try:
            r = _run(path)
            self.assertEqual(r.returncode, 0, f"stderr: {r.stderr}\nstdout: {r.stdout}")
            self.assertIn("ok=true", r.stdout)
            self.assertIn("workstreams=3", r.stdout)
        finally:
            path.unlink()

    def test_dependency_cycle_exits_2(self):
        ws = _ws("WS-1", deps="WS-2") + _ws("WS-2", deps="WS-3") + _ws("WS-3", deps="WS-1")
        path = _write_temp(_spec(ws))
        try:
            r = _run(path)
            self.assertEqual(r.returncode, 2)
            self.assertIn("dependency-cycle", r.stdout)
        finally:
            path.unlink()

    def test_schema_violation_exits_1(self):
        bad = (
            "### WS-1: ok\n\n| Priority | P0 |\n| Complexity | M |\n| Depends on | — |\n\n"
            "**Acceptance criteria:**\n\n- [ ] x\n\n"
            "### WS-2: bad\n\n| Priority | P1 |\n| Depends on | — |\n\n"  # missing Complexity
            "**Acceptance criteria:**\n\n- [ ] y\n\n"
            "### WS-3: ok\n\n| Priority | P0 |\n| Complexity | S |\n| Depends on | — |\n\n"
            "**Acceptance criteria:**\n\n- [ ] z\n\n"
        )
        path = _write_temp(_spec(bad))
        try:
            r = _run(path)
            self.assertEqual(r.returncode, 1)
            self.assertIn("schema-violations", r.stdout)
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()
