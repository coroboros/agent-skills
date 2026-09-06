"""Real CLI artifact handoffs; synthetic axis replies test transport, not review quality."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills/code-ultrareview/scripts"
sys.path.insert(0, str(SCRIPTS))
from manifest import file_identity, set_phase  # noqa: E402


class TestReconcileContract(unittest.TestCase):
    def run_cli(self, root, script, *args):
        env = dict(os.environ, DERIVATION_SKIP_GH="1")
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *map(str, args)],
            cwd=root, env=env, capture_output=True, text=True, timeout=20,
        )

    def prepare(self, root, *, reconcile=True, axes=None):
        scope = root / "scope.json"
        scope.write_text(json.dumps({
            "files_touched_list": ["retry.py"], "languages": ["python"],
            "tools_missing": [], "tools_skipped": [], "activates_coherence": False,
            "repo_kind": "python", "base": "BASE", "target": "HEAD", "instruction_chain": [],
        }))
        tools = root / "tool-findings.jsonl"
        tools.write_text("")
        patch = root / "diff.patch"
        patch.write_text("diff --git a/retry.py b/retry.py\n--- a/retry.py\n+++ b/retry.py\n@@ -1 +1 @@\n-old\n+new\n")
        set_phase(scope, "tool", {"complete": True, "selected_axes": []}, tools)
        if reconcile:
            spec = root / "forge-retry.md"
            spec.write_text("# Spec: retry\n## Acceptance criteria\n- [ ] Retry once\n- [ ] Preserve errors\n")
            result = self.run_cli(root, "derivation/run.py", "--repo", root, "--scope", scope,
                                  "--output", root / "reconcile.json", "--reconcile", spec)
            self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli(root, "axis_dispatch.py", "prepare", "--scope", scope,
                              "--findings", tools, "--diff", patch, "--output-dir", root / "run",
                              *(["--axes", axes] if axes else []))
        self.assertEqual(result.returncode, 0, result.stderr)
        prepared = json.loads(result.stdout)
        results = root / "axis-results"
        results.mkdir()
        for axis in prepared["axes"]:
            (results / f"{axis}.jsonl").write_text(json.dumps({
                "run_id": prepared["run_id"], "axis": axis, "no_findings": True,
            }) + "\n")

    def ingest(self, root):
        return self.run_cli(root, "axis_dispatch.py", "ingest", "--scope", root / "scope.json",
                            "--results-dir", root / "axis-results", "--output", root / "axis-findings.jsonl")

    def synthesize(self, root, *extra):
        return self.run_cli(root, "synthesize.py", "--scope", root / "scope.json",
                            "--findings", root / "axis-findings.jsonl",
                            "--tool-findings", root / "tool-findings.jsonl", "--repo-root", root,
                            "--owner-repo", "example/project", "--sha", "1" * 40, *extra)

    def test_documented_path_renders_verified_artifact_coverage_without_summary_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root)
            result = self.ingest(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = self.synthesize(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("## 📐 Derivation coverage", result.stdout)
            self.assertIn("forge-retry.md", result.stdout)
            self.assertIn("Artifacts supplied: 1. Claims extracted: 2. Claims submitted to Intent: 2.", result.stdout)
            self.assertIn("CONSISTENT totals are unavailable", result.stdout)
            legacy = root / "summary.md"
            legacy.write_text("Fabricated verified ACs: 100%")
            result = self.synthesize(root, "--reconcile-summary", legacy)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("Fabricated", result.stdout)

    def test_no_reconcile_omits_section_and_rejects_legacy_summary_as_substitute(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root, reconcile=False)
            self.assertEqual(self.ingest(root).returncode, 0)
            result = self.synthesize(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("## 📐 Derivation coverage", result.stdout)
            summary = root / "summary.md"
            summary.write_text("## 📐 Derivation coverage\nAll done.")
            result = self.synthesize(root, "--reconcile-summary", summary)
            self.assertEqual(result.returncode, 4)
            self.assertNotIn("## ⚖️ Verdict", result.stdout)

    def test_reconcile_rejects_subset_without_intent_before_writing_bundles(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root)
            target = root / "correctness-only"
            result = self.run_cli(
                root, "axis_dispatch.py", "prepare", "--scope", root / "scope.json",
                "--findings", root / "tool-findings.jsonl", "--diff", root / "diff.patch",
                "--output-dir", target, "--axes", "correctness",
            )
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("include intent in --axes", result.stderr)
            self.assertFalse(target.exists())

    def test_scoped_reconcile_with_intent_keeps_actual_submission_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root, axes="correctness,intent")
            self.assertEqual(self.ingest(root).returncode, 0)
            result = self.synthesize(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Claims submitted to Intent: 2", result.stdout)
            self.assertIn("Scoped findings only", result.stdout)

    def test_persisted_reconcile_without_intent_cannot_ingest_or_synthesize(self):
        for stage in ("ingest", "synthesize"):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.prepare(root)
                if stage == "synthesize":
                    self.assertEqual(self.ingest(root).returncode, 0)
                path = root / "scope.json"
                scope = json.loads(path.read_text())
                scope["axis_coverage"].update({
                    "full": False, "explicit_scope": True, "requested": ["correctness"],
                    "completed": ["correctness"] if stage == "synthesize" else [],
                })
                path.write_text(json.dumps(scope))
                result = self.ingest(root) if stage == "ingest" else self.synthesize(root)
                self.assertEqual(result.returncode, 4, result.stdout + result.stderr)
                self.assertIn("intent", result.stderr)
                self.assertNotIn("Claims submitted to Intent", result.stdout)

    def test_ingestion_and_synthesis_reject_deleted_changed_or_substituted_reconcile(self):
        for stage in ("ingest", "synthesize"):
            for change in ("delete", "modify", "substitute"):
                with self.subTest(stage=stage, change=change), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    self.prepare(root)
                    if stage == "synthesize":
                        result = self.ingest(root)
                        self.assertEqual(result.returncode, 0, result.stderr)
                    payload = root / "reconcile.json"
                    if change == "delete":
                        payload.unlink()
                    elif change == "modify":
                        payload.write_text(payload.read_text() + "\n")
                    else:
                        replacement = root / "other-reconcile.json"
                        replacement.write_bytes(payload.read_bytes())
                        scope_path = root / "scope.json"
                        scope = json.loads(scope_path.read_text())
                        scope["reconcile_coverage"].update({
                            "output": str(replacement.resolve()),
                            "sha256": file_identity(replacement)["sha256"],
                        })
                        scope_path.write_text(json.dumps(scope))
                    result = self.ingest(root) if stage == "ingest" else self.synthesize(root)
                    self.assertEqual(result.returncode, 4, result.stdout + result.stderr)
                    self.assertNotIn("## ⚖️ Verdict", result.stdout)


if __name__ == "__main__":
    unittest.main()
