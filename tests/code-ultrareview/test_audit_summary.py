"""Tests for skills/code-ultrareview/scripts/audit_summary.py.

Pins the deterministic header-formatter contract: scope-string assembly from
audit signals, wall-clock estimate from signals + environment flags, rationale
listing every contributor, and the CLI surface (stdin / --input / --build /
--fuzz).
"""

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "code-ultrareview" / "scripts" / "audit_summary.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("audit_summary", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


audit_summary = _load_module()


class TestScopeAssembly(unittest.TestCase):
    def test_empty_signals_produce_trivial_scope(self):
        result = audit_summary.format_header({})
        self.assertEqual(result["scope"], "trivial diff")

    def test_files_touched_appears_in_scope(self):
        result = audit_summary.format_header({"files_touched": 12})
        self.assertIn("12 files", result["scope"])

    def test_single_file_uses_singular(self):
        result = audit_summary.format_header({"files_touched": 1})
        self.assertIn("1 file", result["scope"])
        self.assertNotIn("1 files", result["scope"])

    def test_public_api_token_present(self):
        result = audit_summary.format_header(
            {"files_touched": 3, "public_api_touched": True}
        )
        self.assertIn("public API", result["scope"])

    def test_normative_spec_includes_named_specs(self):
        result = audit_summary.format_header({
            "normative_spec_mentioned": True,
            "normative_specs_list": ["RFC 6874"],
        })
        self.assertIn("RFC 6874", result["scope"])

    def test_normative_spec_without_list_uses_generic_label(self):
        result = audit_summary.format_header({"normative_spec_mentioned": True})
        self.assertIn("normative spec", result["scope"])
        self.assertNotIn("(", result["scope"])

    def test_manifest_delta_token(self):
        result = audit_summary.format_header({"manifest_graph_delta": True})
        self.assertIn("manifest", result["scope"])

    def test_security_paths_token(self):
        result = audit_summary.format_header({"security_sensitive_paths": True})
        self.assertIn("security paths", result["scope"])

    def test_pre_1_0_token(self):
        result = audit_summary.format_header({"pre_1_0_or_freeze": True})
        self.assertIn("pre-1.0", result["scope"])

    def test_multiple_tokens_joined_by_separator(self):
        result = audit_summary.format_header({
            "files_touched": 5,
            "public_api_touched": True,
            "manifest_graph_delta": True,
        })
        self.assertIn("·", result["scope"])


class TestWallClockEstimate(unittest.TestCase):
    def test_base_only_for_empty_signals(self):
        result = audit_summary.format_header({})
        self.assertEqual(
            result["estimated_wall_clock_seconds"], audit_summary.BASE_SECONDS
        )

    def test_files_touched_add_seconds(self):
        result = audit_summary.format_header({"files_touched": 10})
        expected = audit_summary.BASE_SECONDS + 10 * audit_summary.PER_FILE_SECONDS
        self.assertEqual(result["estimated_wall_clock_seconds"], expected)

    def test_public_api_adds_seconds(self):
        without = audit_summary.format_header({})
        with_api = audit_summary.format_header({"public_api_touched": True})
        delta = (with_api["estimated_wall_clock_seconds"]
                 - without["estimated_wall_clock_seconds"])
        self.assertEqual(delta, audit_summary.PUBLIC_API_SECONDS)

    def test_normative_spec_adds_seconds(self):
        without = audit_summary.format_header({})
        with_spec = audit_summary.format_header({"normative_spec_mentioned": True})
        delta = (with_spec["estimated_wall_clock_seconds"]
                 - without["estimated_wall_clock_seconds"])
        self.assertEqual(delta, audit_summary.NORMATIVE_SPEC_SECONDS)

    def test_manifest_delta_adds_seconds(self):
        without = audit_summary.format_header({})
        with_mfd = audit_summary.format_header({"manifest_graph_delta": True})
        delta = (with_mfd["estimated_wall_clock_seconds"]
                 - without["estimated_wall_clock_seconds"])
        self.assertEqual(delta, audit_summary.MANIFEST_DELTA_SECONDS)

    def test_security_paths_adds_seconds(self):
        without = audit_summary.format_header({})
        with_sec = audit_summary.format_header({"security_sensitive_paths": True})
        delta = (with_sec["estimated_wall_clock_seconds"]
                 - without["estimated_wall_clock_seconds"])
        self.assertEqual(delta, audit_summary.SECURITY_PATHS_SECONDS)

    def test_build_tool_adds_loc_proportional_seconds(self):
        signals = {"loc_changed": 1000}
        without = audit_summary.format_header(signals, build_tool_available=False)
        with_build = audit_summary.format_header(signals, build_tool_available=True)
        delta = (with_build["estimated_wall_clock_seconds"]
                 - without["estimated_wall_clock_seconds"])
        self.assertGreaterEqual(delta, audit_summary.BUILD_BASE_SECONDS)
        self.assertGreaterEqual(delta, int(1000 * audit_summary.BUILD_PER_LOC))

    def test_build_tool_minimum_floor(self):
        signals = {"loc_changed": 1}
        without = audit_summary.format_header(signals, build_tool_available=False)
        with_build = audit_summary.format_header(signals, build_tool_available=True)
        delta = (with_build["estimated_wall_clock_seconds"]
                 - without["estimated_wall_clock_seconds"])
        self.assertEqual(delta, audit_summary.BUILD_BASE_SECONDS)

    def test_property_fuzz_adds_seconds(self):
        signals = {"loc_changed": 100}
        without = audit_summary.format_header(signals)
        with_fuzz = audit_summary.format_header(signals, property_fuzz_available=True)
        delta = (with_fuzz["estimated_wall_clock_seconds"]
                 - without["estimated_wall_clock_seconds"])
        self.assertEqual(delta, audit_summary.PROPERTY_FUZZ_SECONDS)

    def test_deterministic_same_inputs_same_output(self):
        signals = {"loc_changed": 500, "files_touched": 8, "public_api_touched": True}
        r1 = audit_summary.format_header(signals, build_tool_available=True)
        r2 = audit_summary.format_header(signals, build_tool_available=True)
        self.assertEqual(r1, r2)


class TestRationale(unittest.TestCase):
    def test_rationale_starts_with_estimated_wall_clock(self):
        result = audit_summary.format_header({})
        self.assertTrue(result["rationale"].startswith("Estimated wall-clock:"))

    def test_rationale_includes_base_contribution(self):
        result = audit_summary.format_header({})
        self.assertIn("base", result["rationale"])

    def test_rationale_lists_files_contribution(self):
        result = audit_summary.format_header({"files_touched": 4})
        self.assertIn("4 files", result["rationale"])

    def test_rationale_lists_public_api_when_set(self):
        result = audit_summary.format_header({"public_api_touched": True})
        self.assertIn("public API", result["rationale"])

    def test_rationale_includes_total_in_minutes_when_large(self):
        result = audit_summary.format_header(
            {"loc_changed": 1000, "files_touched": 10,
             "public_api_touched": True, "normative_spec_mentioned": True,
             "manifest_graph_delta": True},
            build_tool_available=True, property_fuzz_available=True,
        )
        self.assertIn("m", result["rationale"])

    def test_rationale_excludes_unset_signals(self):
        result = audit_summary.format_header({"files_touched": 3})
        self.assertNotIn("public API", result["rationale"])
        self.assertNotIn("normative spec", result["rationale"])
        self.assertNotIn("manifest delta", result["rationale"])


class TestCLI(unittest.TestCase):
    def _run(self, *args, stdin: str = "") -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            input=stdin, capture_output=True, text=True, timeout=10,
        )

    def test_help_flag_succeeds(self):
        r = self._run("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("audit_summary", r.stdout.lower() + r.stderr.lower())

    def test_stdin_input_produces_canonical_keys(self):
        payload = json.dumps({"loc_changed": 100, "files_touched": 3,
                              "public_api_touched": True})
        r = self._run(stdin=payload)
        self.assertEqual(r.returncode, 0, r.stderr)
        result = json.loads(r.stdout)
        self.assertIn("scope", result)
        self.assertIn("estimated_wall_clock_seconds", result)
        self.assertIn("rationale", result)
        self.assertIn("public API", result["scope"])

    def test_input_flag_reads_file(self):
        with self._tmp_file('{"files_touched": 5}') as path:
            r = self._run("--input", path)
        self.assertEqual(r.returncode, 0, r.stderr)
        result = json.loads(r.stdout)
        self.assertIn("5 files", result["scope"])

    def test_build_flag_increases_estimate(self):
        payload = json.dumps({"loc_changed": 200})
        without = json.loads(self._run(stdin=payload).stdout)
        with_build = json.loads(self._run("--build", stdin=payload).stdout)
        self.assertGreater(
            with_build["estimated_wall_clock_seconds"],
            without["estimated_wall_clock_seconds"],
        )

    def test_fuzz_flag_increases_estimate(self):
        payload = json.dumps({"loc_changed": 100})
        without = json.loads(self._run(stdin=payload).stdout)
        with_fuzz = json.loads(self._run("--fuzz", stdin=payload).stdout)
        self.assertGreater(
            with_fuzz["estimated_wall_clock_seconds"],
            without["estimated_wall_clock_seconds"],
        )

    def _tmp_file(self, content):
        import contextlib
        import tempfile

        @contextlib.contextmanager
        def _ctx():
            with tempfile.NamedTemporaryFile(
                "w", suffix=".json", delete=False, encoding="utf-8"
            ) as f:
                f.write(content)
                f.flush()
                path = f.name
            try:
                yield path
            finally:
                Path(path).unlink(missing_ok=True)

        return _ctx()


class TestRepoKindScopeToken(unittest.TestCase):
    """Pin the WS-2 contract: repo_kind prepends a kind label, competing
    signals append "(+ ...)", override_source appends "(override: ...)".
    "unknown" emits no token so legacy fixtures still render trivial-diff."""

    def test_skills_kind_prepends_token(self):
        result = audit_summary.format_header({
            "files_touched": 2,
            "repo_kind": "skills",
            "repo_kind_signals": {"competing_signals": [], "override_source": None},
        })
        self.assertTrue(result["scope"].startswith("skills repo · "))

    def test_app_kind_token(self):
        result = audit_summary.format_header({
            "files_touched": 3,
            "repo_kind": "app",
            "repo_kind_signals": {"competing_signals": [], "override_source": None},
        })
        self.assertTrue(result["scope"].startswith("app · "))

    def test_competing_signals_render_as_suffix(self):
        result = audit_summary.format_header({
            "files_touched": 1,
            "repo_kind": "app",
            "repo_kind_signals": {
                "competing_signals": ["workspaces"],
                "override_source": None,
            },
        })
        self.assertIn("app (+ workspaces)", result["scope"])

    def test_competing_signals_capped_at_two(self):
        result = audit_summary.format_header({
            "repo_kind": "skills",
            "repo_kind_signals": {
                "competing_signals": ["npm tooling", "workspaces", "Python tooling"],
                "override_source": None,
            },
        })
        self.assertIn("npm tooling, workspaces", result["scope"])
        self.assertNotIn("Python tooling", result["scope"])

    def test_flag_override_surfaces(self):
        result = audit_summary.format_header({
            "repo_kind": "app",
            "repo_kind_signals": {
                "competing_signals": [],
                "override_source": "--repo-kind flag",
            },
        })
        self.assertIn("(override: --repo-kind)", result["scope"])

    def test_config_override_surfaces(self):
        result = audit_summary.format_header({
            "repo_kind": "library",
            "repo_kind_signals": {
                "competing_signals": [],
                "override_source": "config:.code-ultrareview.yaml",
            },
        })
        self.assertIn("(override: .code-ultrareview.yaml)", result["scope"])

    def test_unknown_kind_omits_token_and_preserves_trivial_diff(self):
        # No other signals — empty kind + unknown → "trivial diff".
        result = audit_summary.format_header({
            "repo_kind": "unknown",
            "repo_kind_signals": {"competing_signals": [], "override_source": None},
        })
        self.assertEqual(result["scope"], "trivial diff")

    def test_legacy_signals_without_repo_kind_render_as_before(self):
        # Pre-classifier callers don't emit repo_kind — scope must not crash
        # and must omit any kind token.
        result = audit_summary.format_header({"files_touched": 4})
        self.assertEqual(result["scope"], "4 files")

    def test_kind_token_precedes_dirty_tree(self):
        result = audit_summary.format_header({
            "dirty_tree": True,
            "files_touched": 2,
            "repo_kind": "skills",
            "repo_kind_signals": {"competing_signals": [], "override_source": None},
        })
        # `skills repo` precedes `dirty tree` in the token list.
        self.assertLess(
            result["scope"].index("skills repo"),
            result["scope"].index("dirty tree"),
        )


class TestWallClockUnchangedByClassifier(unittest.TestCase):
    """The classifier is free — adding repo_kind/repo_kind_signals to the
    payload MUST NOT shift the wall-clock estimate. Pins WS-2 AC."""

    def test_wall_clock_byte_equal_with_and_without_repo_kind(self):
        base_signals = {
            "loc_changed": 500, "files_touched": 8,
            "public_api_touched": True, "manifest_graph_delta": True,
        }
        with_kind = audit_summary.format_header({
            **base_signals,
            "repo_kind": "skills",
            "repo_kind_signals": {
                "competing_signals": ["npm tooling"],
                "override_source": "--repo-kind flag",
            },
        }, build_tool_available=True)
        without_kind = audit_summary.format_header(
            base_signals, build_tool_available=True,
        )
        self.assertEqual(
            with_kind["estimated_wall_clock_seconds"],
            without_kind["estimated_wall_clock_seconds"],
        )

    def test_constants_unchanged_post_classifier(self):
        # The cost-model constants stay untouched by the classifier.
        self.assertEqual(audit_summary.BASE_SECONDS, 60)
        self.assertEqual(audit_summary.PER_FILE_SECONDS, 5)
        self.assertEqual(audit_summary.PUBLIC_API_SECONDS, 60)
        self.assertEqual(audit_summary.NORMATIVE_SPEC_SECONDS, 90)
        self.assertEqual(audit_summary.MANIFEST_DELTA_SECONDS, 60)
        self.assertEqual(audit_summary.SECURITY_PATHS_SECONDS, 60)
        self.assertEqual(audit_summary.BUILD_BASE_SECONDS, 60)


class TestA2Rationale(unittest.TestCase):
    """Boundary marker — A2 (sub-80 routing) is the synthesizer's concern.

    The substantive A2 tests live in tests/code-ultrareview/test_aggregation.py.
    audit_summary.py owns header-formatting only; it must not encode A2 logic.
    """

    def test_audit_summary_does_not_encode_a2_strings(self):
        result = audit_summary.format_header({})
        self.assertNotIn("Unverified", result["rationale"])
        self.assertNotIn("Deep pass", result["rationale"])


if __name__ == "__main__":
    unittest.main()
