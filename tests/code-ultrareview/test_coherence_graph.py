"""Tests for the coherence-graph lens (skills/code-ultrareview/scripts/coherence/).

Each fixture under `fixtures/coherence-graph/<case>/` mirrors a real
cross-artifact drift scenario. Tests run the orchestrator end-to-end via
the CLI (`run.py`) and assert findings counts + sub-graph routing. Direct
sub-graph imports cover finer-grained behavior (`--include-prose` toggle,
`.coherence-ignore` allowlist, normalizers, parser error paths).

`gh` calls are disabled via `COHERENCE_SKIP_GH=1` so fixtures behave
identically regardless of the runner's GitHub auth state.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COHERENCE_DIR = REPO_ROOT / "skills" / "code-ultrareview" / "scripts" / "coherence"
RUN_SCRIPT = COHERENCE_DIR / "run.py"
FIXTURES = REPO_ROOT / "tests" / "code-ultrareview" / "fixtures" / "coherence-graph"


# Add the scripts dir to sys.path so `from coherence._common import ...` works
# inside the sub-graph modules' relative imports.
_SCRIPTS_DIR = COHERENCE_DIR.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from coherence import (  # noqa: E402
    _common,
    capability_graph,
    cross_reference_graph,
    description_graph,
    example_graph,
    spec_conformance_graph,
    version_graph,
)


def _env() -> dict:
    env = os.environ.copy()
    env["COHERENCE_SKIP_GH"] = "1"
    return env


def _run_cli(fixture: str, *extra: str) -> dict:
    repo = FIXTURES / fixture
    r = subprocess.run(
        [sys.executable, str(RUN_SCRIPT), "--repo", str(repo), *extra],
        env=_env(), capture_output=True, text=True, timeout=15,
    )
    if r.returncode != 0:
        raise AssertionError(f"run.py exit {r.returncode}: {r.stderr}")
    return json.loads(r.stdout)


# ---------------------------------------------------------------------------
# Orchestrator — end-to-end fixture sweep
# ---------------------------------------------------------------------------


class TestOrchestratorFixtures(unittest.TestCase):
    def setUp(self):
        os.environ["COHERENCE_SKIP_GH"] = "1"

    def test_clean_repo_has_no_findings(self):
        out = _run_cli("clean-repo")
        self.assertEqual(out["lens"], "coherence-graph")
        self.assertEqual(out["findings"], [])

    def test_description_divergence_one_finding(self):
        out = _run_cli("description-divergence")
        descriptions = [f for f in out["findings"] if f["sub_graph"] == "description"]
        self.assertEqual(len(descriptions), 1)
        self.assertEqual(descriptions[0]["location"], "package.json ↔ marketplace.json")
        self.assertEqual(descriptions[0]["severity"], "Medium")
        self.assertGreaterEqual(descriptions[0]["confidence"], 80)

    def test_description_divergence_ignored_emits_zero(self):
        out = _run_cli("description-divergence-ignored")
        descriptions = [f for f in out["findings"] if f["sub_graph"] == "description"]
        self.assertEqual(descriptions, [])

    def test_version_mismatch_one_finding(self):
        out = _run_cli("version-mismatch")
        versions = [f for f in out["findings"] if f["sub_graph"] == "version"]
        self.assertEqual(len(versions), 1)
        self.assertIn("package.json", versions[0]["location"])
        self.assertIn("marketplace.json", versions[0]["location"])
        self.assertEqual(versions[0]["severity"], "High")

    def test_broken_cross_skill_reference_one_finding(self):
        out = _run_cli("broken-cross-skill-reference")
        refs = [f for f in out["findings"] if f["sub_graph"] == "cross-reference"]
        self.assertEqual(len(refs), 1)
        self.assertIn("/nonexistent", refs[0]["location"])

    def test_broken_example_one_finding(self):
        out = _run_cli("broken-example")
        examples = [f for f in out["findings"] if f["sub_graph"] == "example"]
        self.assertEqual(len(examples), 1)
        self.assertIn("--foo", examples[0]["location"])

    def test_clean_structured_divergent_prose_default_clean(self):
        out = _run_cli("clean-structured-divergent-prose")
        descriptions = [f for f in out["findings"] if f["sub_graph"] == "description"]
        self.assertEqual(descriptions, [])

    def test_clean_structured_divergent_prose_include_prose_flags(self):
        out = _run_cli("clean-structured-divergent-prose", "--include-prose")
        descriptions = [f for f in out["findings"] if f["sub_graph"] == "description"]
        self.assertEqual(len(descriptions), 2)
        self.assertTrue(any("README.prose" in f["location"] for f in descriptions))


class TestOrchestratorContract(unittest.TestCase):
    def setUp(self):
        os.environ["COHERENCE_SKIP_GH"] = "1"

    def test_lens_key_is_coherence_graph(self):
        out = _run_cli("clean-repo")
        self.assertEqual(out["lens"], "coherence-graph")

    def test_each_finding_carries_required_fields(self):
        out = _run_cli("description-divergence")
        required = {"lens", "sub_graph", "severity", "location", "finding",
                    "recommendation", "confidence"}
        for f in out["findings"]:
            self.assertTrue(required.issubset(f.keys()))
            self.assertEqual(f["lens"], "coherence-graph")

    def test_nonexistent_repo_path_exits_2(self):
        r = subprocess.run(
            [sys.executable, str(RUN_SCRIPT), "--repo", "/nonexistent/path/xyz"],
            env=_env(), capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(r.returncode, 2)


# ---------------------------------------------------------------------------
# Direct sub-graph tests
# ---------------------------------------------------------------------------


class TestIgnoreFileParser(unittest.TestCase):
    def test_parses_nested_lists(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / ".coherence-ignore").write_text(
                "description:\n"
                "  ignore_pairs:\n"
                "    - foo:bar\n"
                "    - 'a:b'\n"
                "version:\n"
                "  ignore_pairs:\n"
                "    - tag:pkg\n"
                "\n# comment\n",
                encoding="utf-8",
            )
            ig = _common.load_ignore(repo)
        self.assertEqual(ig.list_for("description", "ignore_pairs"), ["foo:bar", "a:b"])
        self.assertEqual(ig.list_for("version", "ignore_pairs"), ["tag:pkg"])
        self.assertTrue(ig.has("description", "ignore_pairs", "foo:bar"))
        self.assertFalse(ig.has("description", "ignore_pairs", "missing"))

    def test_missing_file_returns_empty(self):
        with tempfile.TemporaryDirectory() as t:
            ig = _common.load_ignore(Path(t))
        self.assertEqual(ig.data, {})

    def test_malformed_raises(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / ".coherence-ignore").write_text(
                "description:\n  ignore_pairs\n    - foo\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                _common.load_ignore(repo)

    def test_strips_inline_quotes(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / ".coherence-ignore").write_text(
                'description:\n  ignore_pairs:\n    - "a:b"\n    - \'c:d\'\n',
                encoding="utf-8",
            )
            ig = _common.load_ignore(repo)
        self.assertEqual(ig.list_for("description", "ignore_pairs"), ["a:b", "c:d"])


class TestNormalizers(unittest.TestCase):
    def test_description_case_insensitive(self):
        self.assertEqual(
            _common.normalize_description("Foo Bar"),
            _common.normalize_description("foo bar"),
        )

    def test_description_collapses_whitespace(self):
        self.assertEqual(
            _common.normalize_description("hello   world"),
            _common.normalize_description("hello world"),
        )

    def test_version_strips_leading_v(self):
        self.assertEqual(_common.normalize_version("v1.2.3"), "1.2.3")
        self.assertEqual(_common.normalize_version("V1.2.3"), "1.2.3")
        self.assertEqual(_common.normalize_version("1.2.3"), "1.2.3")


class TestDescriptionGraph(unittest.TestCase):
    def setUp(self):
        os.environ["COHERENCE_SKIP_GH"] = "1"

    def test_no_sources_no_findings(self):
        with tempfile.TemporaryDirectory() as t:
            findings = description_graph.run(Path(t), _common.IgnoreFile())
        self.assertEqual(findings, [])

    def test_single_source_no_findings(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "package.json").write_text(
                json.dumps({"description": "Only one source."}), encoding="utf-8"
            )
            findings = description_graph.run(repo, _common.IgnoreFile())
        self.assertEqual(findings, [])

    def test_pair_disagreement_emits_finding(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "package.json").write_text(
                json.dumps({"description": "Alpha"}), encoding="utf-8"
            )
            mp_dir = repo / ".claude-plugin"
            mp_dir.mkdir()
            (mp_dir / "marketplace.json").write_text(
                json.dumps({"metadata": {"description": "Beta"}}), encoding="utf-8"
            )
            findings = description_graph.run(repo, _common.IgnoreFile())
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].sub_graph, "description")


class TestVersionGraph(unittest.TestCase):
    def setUp(self):
        os.environ["COHERENCE_SKIP_GH"] = "1"

    def test_no_sources(self):
        with tempfile.TemporaryDirectory() as t:
            findings = version_graph.run(Path(t), _common.IgnoreFile())
        self.assertEqual(findings, [])

    def test_changelog_header_extracted(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "package.json").write_text(
                json.dumps({"version": "1.2.4"}), encoding="utf-8"
            )
            (repo / "CHANGELOG.md").write_text(
                "# Changelog\n\n## 1.2.3 — initial\n", encoding="utf-8"
            )
            findings = version_graph.run(repo, _common.IgnoreFile())
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].severity, "High")


class TestSpecConformanceStub(unittest.TestCase):
    def test_no_spec_no_finding(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "README.md").write_text("# nothing here\n", encoding="utf-8")
            findings = spec_conformance_graph.run(repo, _common.IgnoreFile())
        self.assertEqual(findings, [])

    def test_rfc_mention_surfaces_low_confidence(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "README.md").write_text(
                "# project\n\nFollows RFC 6874 for zone IDs.\n", encoding="utf-8"
            )
            findings = spec_conformance_graph.run(repo, _common.IgnoreFile())
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].severity, "Low")
        self.assertEqual(findings[0].confidence, 50)
        self.assertIn("deep", findings[0].recommendation.lower())

    def test_allowlisted_spec_suppressed(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "README.md").write_text(
                "# project\n\nFollows RFC 6874.\n", encoding="utf-8"
            )
            (repo / ".coherence-ignore").write_text(
                "spec-conformance:\n  ignore_specs:\n    - RFC 6874\n",
                encoding="utf-8",
            )
            ig = _common.load_ignore(repo)
            findings = spec_conformance_graph.run(repo, ig)
        self.assertEqual(findings, [])


class TestCrossReferenceGraph(unittest.TestCase):
    def setUp(self):
        os.environ["COHERENCE_SKIP_GH"] = "1"

    def test_external_links_ignored(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "README.md").write_text(
                "[click](https://example.com)\n", encoding="utf-8"
            )
            findings = cross_reference_graph.run(repo, _common.IgnoreFile())
        self.assertEqual(findings, [])

    def test_fenced_block_links_ignored(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "README.md").write_text(
                "```\n[example](./not-real.md)\n```\n", encoding="utf-8"
            )
            findings = cross_reference_graph.run(repo, _common.IgnoreFile())
        self.assertEqual(findings, [])

    def test_broken_relative_link_surfaces(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "README.md").write_text(
                "[gone](./missing.md)\n", encoding="utf-8"
            )
            findings = cross_reference_graph.run(repo, _common.IgnoreFile())
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].severity, "High")

    def test_known_external_slash_skill_skipped(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            mp_dir = repo / ".claude-plugin"
            mp_dir.mkdir()
            (mp_dir / "marketplace.json").write_text(
                json.dumps({"plugins": [{"name": "p", "skills": ["./skills/spec"]}]}),
                encoding="utf-8",
            )
            (repo / "README.md").write_text(
                "Use `/init` and `/memory`.\n", encoding="utf-8"
            )
            findings = cross_reference_graph.run(repo, _common.IgnoreFile())
        self.assertEqual(findings, [])


class TestExampleGraph(unittest.TestCase):
    def setUp(self):
        os.environ["COHERENCE_SKIP_GH"] = "1"

    def test_no_readme_no_findings(self):
        with tempfile.TemporaryDirectory() as t:
            findings = example_graph.run(Path(t), _common.IgnoreFile())
        self.assertEqual(findings, [])

    def test_unrecognized_flag_surfaces(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "README.md").write_text(
                "```bash\npython3 scripts/demo.py --missing\n```\n",
                encoding="utf-8",
            )
            scripts_dir = repo / "scripts"
            scripts_dir.mkdir()
            (scripts_dir / "demo.py").write_text(
                'parser.add_argument("--known")\n', encoding="utf-8"
            )
            findings = example_graph.run(repo, _common.IgnoreFile())
        self.assertEqual(len(findings), 1)
        self.assertIn("--missing", findings[0].location)

    def test_allowlisted_flag_skipped(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "README.md").write_text(
                "```bash\npython3 scripts/demo.py --missing\n```\n",
                encoding="utf-8",
            )
            scripts_dir = repo / "scripts"
            scripts_dir.mkdir()
            (scripts_dir / "demo.py").write_text(
                'parser.add_argument("--known")\n', encoding="utf-8"
            )
            ig = _common.IgnoreFile(data={"example": {"ignore_flags": ["--missing"]}})
            findings = example_graph.run(repo, ig)
        self.assertEqual(findings, [])


class TestCapabilityGraph(unittest.TestCase):
    def test_unmatched_item_surfaces(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "README.md").write_text(
                "# project\n\n## Features\n\n- Mythical capability\n",
                encoding="utf-8",
            )
            findings = capability_graph.run(repo, _common.IgnoreFile())
        self.assertEqual(len(findings), 1)
        self.assertIn("Mythical capability", findings[0].finding)

    def test_matched_path_capability_skipped(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scripts_dir = repo / "scripts"
            scripts_dir.mkdir()
            (scripts_dir / "real_thing.py").write_text("pass\n", encoding="utf-8")
            (repo / "README.md").write_text(
                "# project\n\n## Commands\n\n- `real_thing`\n",
                encoding="utf-8",
            )
            findings = capability_graph.run(repo, _common.IgnoreFile())
        self.assertEqual(findings, [])

    def test_allowlisted_capability_skipped(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "README.md").write_text(
                "# project\n\n## Features\n\n- legacy-cli\n",
                encoding="utf-8",
            )
            ig = _common.IgnoreFile(data={"capability": {"ignore_items": ["legacy-cli"]}})
            findings = capability_graph.run(repo, ig)
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
