"""Tests for skills/code-ultrareview/scripts/tier_router.py.

Pins the weight table, the half-open threshold boundaries (0.35 enters Deep,
0.70 enters Ultra), the rationale contract (non-zero contributors enumerated,
zero-only rationale uses the documented fallback line), and the Ultra
confirmation gate (mocked `input()` exercising the four paths: not-ultra,
apply-safe bypass, yes-to-all bypass, prompt accept/reject).
"""

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "code-ultrareview" / "scripts" / "tier_router.py"
FIXTURES = REPO_ROOT / "tests" / "code-ultrareview" / "fixtures" / "audit"


def _load_module():
    spec = importlib.util.spec_from_file_location("tier_router", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tier_router = _load_module()


class TestWeightTable(unittest.TestCase):
    def test_weights_sum_to_one(self):
        self.assertAlmostEqual(sum(tier_router.WEIGHTS.values()), 1.0, places=4)

    def test_weight_values_per_spec(self):
        self.assertEqual(tier_router.WEIGHTS["loc_changed"], 0.20)
        self.assertEqual(tier_router.WEIGHTS["files_touched"], 0.10)
        self.assertEqual(tier_router.WEIGHTS["public_api_touched"], 0.20)
        self.assertEqual(tier_router.WEIGHTS["normative_spec_mentioned"], 0.20)
        self.assertEqual(tier_router.WEIGHTS["manifest_graph_delta"], 0.10)
        self.assertEqual(tier_router.WEIGHTS["pre_1_0_or_freeze"], 0.05)
        self.assertEqual(tier_router.WEIGHTS["test_coverage_delta"], 0.10)
        self.assertEqual(tier_router.WEIGHTS["security_sensitive_paths"], 0.05)


class TestThresholdBoundaries(unittest.TestCase):
    def test_034_routes_standard(self):
        self.assertEqual(tier_router.pick_tier(0.34), "standard")

    def test_035_routes_deep(self):
        self.assertEqual(tier_router.pick_tier(0.35), "deep")

    def test_069_routes_deep(self):
        self.assertEqual(tier_router.pick_tier(0.69), "deep")

    def test_070_routes_ultra(self):
        self.assertEqual(tier_router.pick_tier(0.70), "ultra")

    def test_zero_routes_standard(self):
        self.assertEqual(tier_router.pick_tier(0.0), "standard")

    def test_one_routes_ultra(self):
        self.assertEqual(tier_router.pick_tier(1.0), "ultra")


class TestNormalizers(unittest.TestCase):
    def test_loc_normalization_saturates_at_500(self):
        self.assertEqual(tier_router.normalize_loc(0), 0.0)
        self.assertEqual(tier_router.normalize_loc(250), 0.5)
        self.assertEqual(tier_router.normalize_loc(500), 1.0)
        self.assertEqual(tier_router.normalize_loc(5000), 1.0)

    def test_files_normalization_saturates_at_20(self):
        self.assertEqual(tier_router.normalize_files(0), 0.0)
        self.assertEqual(tier_router.normalize_files(10), 0.5)
        self.assertEqual(tier_router.normalize_files(20), 1.0)
        self.assertEqual(tier_router.normalize_files(100), 1.0)

    def test_test_gap_inverts(self):
        self.assertEqual(tier_router.normalize_test_gap(0.0), 1.0)
        self.assertEqual(tier_router.normalize_test_gap(0.5), 0.5)
        self.assertEqual(tier_router.normalize_test_gap(1.0), 0.0)
        self.assertEqual(tier_router.normalize_test_gap(2.0), 0.0)
        self.assertEqual(tier_router.normalize_test_gap(None), 0.0)


class TestRationaleContents(unittest.TestCase):
    def test_nonzero_contributors_are_listed(self):
        signals = {
            "loc_changed": 200,
            "files_touched": 4,
            "public_api_touched": True,
            "normative_spec_mentioned": False,
            "manifest_graph_delta": True,
            "pre_1_0_or_freeze": False,
            "test_coverage_delta": 0.5,
            "security_sensitive_paths": False,
        }
        result = tier_router.route(signals)
        for key in ("loc_changed", "files_touched", "public_api_touched",
                    "manifest_graph_delta", "test_coverage_delta"):
            self.assertIn(key, result["rationale"], f"{key} missing from rationale")
        self.assertNotIn("normative_spec_mentioned", result["rationale"])
        self.assertNotIn("security_sensitive_paths", result["rationale"])

    def test_all_zero_rationale_uses_fallback(self):
        signals = {
            "loc_changed": 0, "files_touched": 0,
            "public_api_touched": False, "normative_spec_mentioned": False,
            "manifest_graph_delta": False, "pre_1_0_or_freeze": False,
            "test_coverage_delta": 1.0, "security_sensitive_paths": False,
        }
        result = tier_router.route(signals)
        self.assertIn("all signals at zero", result["rationale"])

    def test_rationale_includes_threshold_line(self):
        signals = {"loc_changed": 100, "files_touched": 1, "test_coverage_delta": 1.0}
        result = tier_router.route(signals)
        self.assertIn("Thresholds:", result["rationale"])
        self.assertIn("0.35", result["rationale"])
        self.assertIn("0.7", result["rationale"])


class TestEstimatedTokens(unittest.TestCase):
    def test_per_tier_budget(self):
        self.assertEqual(tier_router.ESTIMATED_TOKENS["standard"], 50000)
        self.assertEqual(tier_router.ESTIMATED_TOKENS["deep"], 150000)
        self.assertEqual(tier_router.ESTIMATED_TOKENS["ultra"], 400000)

    def test_route_attaches_correct_token_budget(self):
        signals = {"loc_changed": 0}
        self.assertEqual(tier_router.route(signals)["estimated_tokens"], 50000)
        signals = {"public_api_touched": True, "manifest_graph_delta": True,
                   "test_coverage_delta": 0.3, "loc_changed": 200, "files_touched": 4}
        self.assertEqual(tier_router.route(signals)["estimated_tokens"], 150000)
        signals = {
            "loc_changed": 500, "files_touched": 10, "public_api_touched": True,
            "normative_spec_mentioned": True, "manifest_graph_delta": True,
            "test_coverage_delta": 0.2,
        }
        self.assertEqual(tier_router.route(signals)["estimated_tokens"], 400000)


class TestFixtures(unittest.TestCase):
    EXPECTED = {
        "small-low-risk.json": "standard",
        "manifest-only-delta.json": "standard",
        "public-api-change.json": "deep",
        "spec-claim.json": "ultra",
        "pre-1.0-large-refactor.json": "ultra",
    }

    def test_each_fixture_routes_to_expected_tier(self):
        for name, expected_tier in self.EXPECTED.items():
            with self.subTest(fixture=name):
                signals = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
                result = tier_router.route(signals)
                self.assertEqual(
                    result["tier"], expected_tier,
                    f"{name}: expected {expected_tier}, got {result['tier']} (score {result['score']})"
                )


class TestConfirmUltra(unittest.TestCase):
    def test_non_ultra_proceeds_without_prompt(self):
        with mock.patch("builtins.input") as m:
            self.assertTrue(tier_router.confirm_ultra(
                tier="standard", rationale="r", estimated_tokens=50000,
                apply_safe=False, yes=False,
            ))
            m.assert_not_called()

    def test_apply_safe_bypasses_prompt(self):
        with mock.patch("builtins.input") as m:
            self.assertTrue(tier_router.confirm_ultra(
                tier="ultra", rationale="r", estimated_tokens=400000,
                apply_safe=True, yes=False,
            ))
            m.assert_not_called()

    def test_yes_bypasses_prompt(self):
        with mock.patch("builtins.input") as m:
            self.assertTrue(tier_router.confirm_ultra(
                tier="ultra", rationale="r", estimated_tokens=400000,
                apply_safe=False, yes=True,
            ))
            m.assert_not_called()

    def test_ultra_prompts_and_accepts(self):
        with contextlib.redirect_stdout(io.StringIO()), \
                mock.patch("builtins.input", return_value="y") as m:
            self.assertTrue(tier_router.confirm_ultra(
                tier="ultra", rationale="r", estimated_tokens=400000,
                apply_safe=False, yes=False,
            ))
            m.assert_called_once()

    def test_ultra_prompts_and_rejects(self):
        with contextlib.redirect_stdout(io.StringIO()), \
                mock.patch("builtins.input", return_value="n") as m:
            self.assertFalse(tier_router.confirm_ultra(
                tier="ultra", rationale="r", estimated_tokens=400000,
                apply_safe=False, yes=False,
            ))
            m.assert_called_once()

    def test_ultra_prompts_empty_input_rejects(self):
        with contextlib.redirect_stdout(io.StringIO()), \
                mock.patch("builtins.input", return_value="") as m:
            self.assertFalse(tier_router.confirm_ultra(
                tier="ultra", rationale="r", estimated_tokens=400000,
                apply_safe=False, yes=False,
            ))
            m.assert_called_once()


class TestCLI(unittest.TestCase):
    def _run(self, *args, stdin: str = "") -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            input=stdin, capture_output=True, text=True, timeout=10,
        )

    def test_stdin_input(self):
        payload = (FIXTURES / "small-low-risk.json").read_text(encoding="utf-8")
        r = self._run(stdin=payload)
        self.assertEqual(r.returncode, 0, r.stderr)
        result = json.loads(r.stdout)
        self.assertEqual(result["tier"], "standard")
        self.assertIn("score", result)
        self.assertIn("rationale", result)
        self.assertIn("estimated_tokens", result)

    def test_input_flag(self):
        r = self._run("--input", str(FIXTURES / "public-api-change.json"))
        self.assertEqual(r.returncode, 0, r.stderr)
        result = json.loads(r.stdout)
        self.assertEqual(result["tier"], "deep")

    def test_gate_mode_bypassed_by_apply_safe(self):
        router_out = json.dumps({
            "tier": "ultra", "rationale": "r", "estimated_tokens": 400000, "score": 0.8,
        })
        r = self._run("--gate", "--apply-safe", stdin=router_out)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_gate_mode_bypassed_by_yes(self):
        router_out = json.dumps({
            "tier": "ultra", "rationale": "r", "estimated_tokens": 400000, "score": 0.8,
        })
        r = self._run("--gate", "-y", stdin=router_out)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_gate_mode_non_ultra_proceeds(self):
        router_out = json.dumps({
            "tier": "standard", "rationale": "r", "estimated_tokens": 50000, "score": 0.1,
        })
        r = self._run("--gate", stdin=router_out)
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
