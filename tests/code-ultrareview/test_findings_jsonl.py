"""WS-5 tests for `scripts/findings_to_jsonl.py`.

Pins:

    1. Label mapping — `(severity, axis)` → Conventional Comments label
       (`issue` / `suggestion` / `nitpick` / `question`).
    2. Permalink format — verbatim Anthropic shape
       `https://github.com/<owner>/<repo>/blob/<full-sha>/<path>#L<n>-L<m>`.
       Single-line locations render as `#L<n>-L<n>`.
    3. Owner/repo detection — handles HTTPS + SSH GitHub origins; rejects
       non-GitHub remotes (no permalink, no guess).
    4. SHA detection — only accepts full 40-char hex SHAs.
    5. JSONL emission is line-delimited JSON — every line parses cleanly,
       record fields are deterministic, validator-produced fields surface
       when present.
    6. CLI surface — `--findings <in> --output <out>` round-trip.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT_DIR = REPO_ROOT / "skills" / "code-ultrareview" / "scripts"
SCRIPT = SCRIPT_DIR / "findings_to_jsonl.py"

sys.path.insert(0, str(REPO_ROOT / "tests" / "_pipeline"))
from _contracts import CLUSTERS  # noqa: E402

REVIEW = CLUSTERS["review"]


def _load():
    spec = importlib.util.spec_from_file_location("findings_to_jsonl", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ftj = _load()


def _finding(**overrides) -> dict:
    base = {
        "axis": "correctness",
        "severity": "Medium",
        "location": "src/a.ts:10",
        "finding": "Potential null deref",
        "recommendation": "Add a guard",
        "confidence": 85,
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# 1. Label mapping
# ---------------------------------------------------------------------------


class TestLabelMapping(unittest.TestCase):
    def test_high_correctness_is_issue(self):
        label = ftj.label_for(_finding(severity="High", axis="correctness"))
        self.assertEqual(label, "issue")

    def test_high_design_api_is_issue(self):
        label = ftj.label_for(_finding(severity="High", axis="design-api"))
        self.assertEqual(label, "issue")

    def test_medium_any_axis_is_suggestion(self):
        for axis in ("correctness", "tests", "documentation", "style",
                     "intent", "performance", "design-api", "simplification"):
            label = ftj.label_for(_finding(severity="Medium", axis=axis))
            self.assertEqual(
                label, "suggestion", f"axis={axis} expected suggestion"
            )

    def test_low_documentation_is_nitpick(self):
        label = ftj.label_for(_finding(severity="Low", axis="documentation"))
        self.assertEqual(label, "nitpick")

    def test_low_style_is_nitpick(self):
        label = ftj.label_for(_finding(severity="Low", axis="style"))
        self.assertEqual(label, "nitpick")

    def test_low_other_axes_is_suggestion(self):
        label = ftj.label_for(_finding(severity="Low", axis="correctness"))
        self.assertEqual(label, "suggestion")

    def test_sub_80_is_question_regardless_of_axis(self):
        for axis in ("correctness", "design-api", "tests", "documentation"):
            label = ftj.label_for(
                _finding(severity="Low", axis=axis, confidence=70)
            )
            self.assertEqual(
                label, "question", f"sub-80 axis={axis} expected question"
            )

    def test_labels_in_contract_match_implementation(self):
        """The pipeline contract pins the label vocabulary — drift breaks
        any consumer piping JSONL through `gh pr comment`."""
        self.assertEqual(
            sorted(REVIEW["jsonl_labels"]),
            sorted(ftj.LABELS),
        )


# ---------------------------------------------------------------------------
# 2. Permalink format
# ---------------------------------------------------------------------------


class TestPermalink(unittest.TestCase):
    SHA = "a" * 40
    OWNER_REPO = "coroboros/agent-skills"

    def test_single_line_location(self):
        link = ftj.make_permalink(self.OWNER_REPO, self.SHA, "src/a.ts:42")
        self.assertEqual(
            link,
            f"https://github.com/{self.OWNER_REPO}/blob/{self.SHA}/src/a.ts#L42-L42",
        )

    def test_range_location(self):
        link = ftj.make_permalink(self.OWNER_REPO, self.SHA, "src/a.ts:10-25")
        self.assertEqual(
            link,
            f"https://github.com/{self.OWNER_REPO}/blob/{self.SHA}/src/a.ts#L10-L25",
        )

    def test_path_only_no_fragment(self):
        link = ftj.make_permalink(self.OWNER_REPO, self.SHA, "src/a.ts")
        self.assertEqual(
            link,
            f"https://github.com/{self.OWNER_REPO}/blob/{self.SHA}/src/a.ts",
        )

    def test_missing_owner_repo_returns_none(self):
        link = ftj.make_permalink(None, self.SHA, "src/a.ts:1")
        self.assertIsNone(link)

    def test_missing_sha_returns_none(self):
        link = ftj.make_permalink(self.OWNER_REPO, None, "src/a.ts:1")
        self.assertIsNone(link)

    def test_empty_location_returns_none(self):
        link = ftj.make_permalink(self.OWNER_REPO, self.SHA, "")
        self.assertIsNone(link)


# ---------------------------------------------------------------------------
# 3. Location parser — handles all three shapes
# ---------------------------------------------------------------------------


class TestParseLocation(unittest.TestCase):
    def test_single_line(self):
        self.assertEqual(
            ftj.parse_location("src/a.ts:42"),
            ("src/a.ts", 42, 42),
        )

    def test_range(self):
        self.assertEqual(
            ftj.parse_location("src/a.ts:10-25"),
            ("src/a.ts", 10, 25),
        )

    def test_path_only(self):
        self.assertEqual(
            ftj.parse_location("src/a.ts"),
            ("src/a.ts", None, None),
        )

    def test_empty(self):
        self.assertEqual(ftj.parse_location(""), ("", None, None))

    def test_whitespace_stripped(self):
        self.assertEqual(
            ftj.parse_location("  src/a.ts:42  "),
            ("src/a.ts", 42, 42),
        )


# ---------------------------------------------------------------------------
# 4. Owner/repo + SHA detection
# ---------------------------------------------------------------------------


class TestRemoteDetection(unittest.TestCase):
    def _make_repo(self, tmp: Path, remote_url: str | None) -> Path:
        repo = tmp / "repo"
        repo.mkdir()
        subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
        if remote_url:
            subprocess.run(
                ["git", "-C", str(repo), "remote", "add", "origin", remote_url],
                check=True,
            )
        (repo / "README.md").write_text("hi\n", encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t",
             "add", "README.md"], check=True,
        )
        subprocess.run(
            ["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t",
             "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
             "commit", "-q", "-m", "init"], check=True,
        )
        return repo

    def test_https_github_origin(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._make_repo(
                Path(tmp),
                "https://github.com/coroboros/agent-skills.git",
            )
            self.assertEqual(
                ftj.detect_owner_repo(repo),
                "coroboros/agent-skills",
            )

    def test_ssh_github_origin(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._make_repo(
                Path(tmp),
                "git@github.com:coroboros/agent-skills.git",
            )
            self.assertEqual(
                ftj.detect_owner_repo(repo),
                "coroboros/agent-skills",
            )

    def test_non_github_remote_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._make_repo(
                Path(tmp),
                "https://gitlab.com/coroboros/agent-skills.git",
            )
            self.assertIsNone(ftj.detect_owner_repo(repo))

    def test_no_remote_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._make_repo(Path(tmp), remote_url=None)
            self.assertIsNone(ftj.detect_owner_repo(repo))

    def test_sha_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._make_repo(Path(tmp), remote_url=None)
            sha = ftj.detect_sha(repo)
            self.assertIsNotNone(sha)
            self.assertRegex(sha, r"^[0-9a-f]{40}$")


# ---------------------------------------------------------------------------
# 5. JSONL emission — record shape + validity
# ---------------------------------------------------------------------------


class TestRecordShape(unittest.TestCase):
    def test_required_fields_present(self):
        record = ftj.to_record(_finding())
        for key in ("label", "axis", "severity", "confidence", "location",
                    "finding", "recommendation"):
            self.assertIn(key, record, f"missing field {key!r}")

    def test_permalink_omitted_without_owner_repo(self):
        record = ftj.to_record(_finding())
        self.assertNotIn("permalink", record)

    def test_permalink_included_with_owner_repo_and_sha(self):
        record = ftj.to_record(
            _finding(),
            owner_repo="coroboros/agent-skills",
            sha="a" * 40,
        )
        self.assertIn("permalink", record)
        self.assertIn("github.com/coroboros/agent-skills", record["permalink"])

    def test_validator_score_surfaced(self):
        record = ftj.to_record(_finding(validator_score=85))
        self.assertEqual(record["validator_score"], 85)

    def test_validator_reason_surfaced(self):
        record = ftj.to_record(
            _finding(meta={"validator_reason": "CLAUDE.md rule confirmed"})
        )
        self.assertEqual(record["validator_reason"], "CLAUDE.md rule confirmed")


class TestJsonlValidity(unittest.TestCase):
    def test_every_emitted_line_parses(self):
        findings = [
            _finding(severity="High", axis="correctness"),
            _finding(severity="Medium", axis="tests"),
            _finding(severity="Low", axis="documentation"),
            _finding(severity="Medium", axis="design-api", confidence=70),
        ]
        for line in ftj.emit(findings, owner_repo=None, sha=None):
            record = json.loads(line)
            self.assertIn("label", record)

    def test_label_mapping_in_emitted_records(self):
        findings = [
            _finding(severity="High", axis="correctness"),
            _finding(severity="High", axis="design-api"),
            _finding(severity="Medium", axis="tests"),
            _finding(severity="Low", axis="documentation"),
            _finding(severity="Low", axis="style"),
            _finding(severity="Low", axis="correctness"),
            _finding(severity="Medium", axis="tests", confidence=70),
        ]
        labels = [json.loads(line)["label"]
                  for line in ftj.emit(findings, owner_repo=None, sha=None)]
        self.assertEqual(
            labels,
            ["issue", "issue", "suggestion", "nitpick", "nitpick",
             "suggestion", "question"],
        )


# ---------------------------------------------------------------------------
# 6. CLI surface
# ---------------------------------------------------------------------------


class TestCli(unittest.TestCase):
    def test_findings_to_output_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            findings_path = tmp_path / "findings.jsonl"
            findings_path.write_text(
                json.dumps(_finding(severity="High", axis="correctness")) + "\n",
                encoding="utf-8",
            )
            output_path = tmp_path / "out.jsonl"
            result = subprocess.run(
                [sys.executable, str(SCRIPT),
                 "--findings", str(findings_path),
                 "--output", str(output_path)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            content = output_path.read_text(encoding="utf-8")
            self.assertTrue(content.strip(), "output empty")
            for line in content.splitlines():
                record = json.loads(line)
                self.assertEqual(record["label"], "issue")

    def test_cli_omits_permalink_when_owner_repo_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            findings_path = tmp_path / "findings.jsonl"
            findings_path.write_text(
                json.dumps(_finding(severity="High", axis="correctness")) + "\n",
                encoding="utf-8",
            )
            # repo-root pointing at a non-git directory → owner_repo lookup
            # returns None; permalink should be omitted.
            output_path = tmp_path / "out.jsonl"
            non_git = tmp_path / "not-a-repo"
            non_git.mkdir()
            result = subprocess.run(
                [sys.executable, str(SCRIPT),
                 "--findings", str(findings_path),
                 "--output", str(output_path),
                 "--repo-root", str(non_git)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            line = output_path.read_text(encoding="utf-8").strip().splitlines()[0]
            record = json.loads(line)
            self.assertNotIn("permalink", record)


# ---------------------------------------------------------------------------
# Malformed input — fail loud
# ---------------------------------------------------------------------------


class TestMalformedInput(unittest.TestCase):
    def test_invalid_json_line_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bad = tmp_path / "bad.jsonl"
            bad.write_text("not valid json\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                ftj.load_findings(bad)


# ---------------------------------------------------------------------------
# Threshold + dot-in-repo regression — single source of truth + permalink fixes
# ---------------------------------------------------------------------------


class TestThresholdSingleSource(unittest.TestCase):
    """Pins that `findings_to_jsonl.CONFIDENCE_THRESHOLD` is the same object
    as `synthesis_core.CONFIDENCE_THRESHOLD`. A future bump in synthesis_core
    propagates to the JSONL label routing automatically.
    """

    def test_threshold_imported_from_synthesis_core(self):
        synth_spec = importlib.util.spec_from_file_location(
            "synthesis_core", SCRIPT_DIR / "synthesis_core.py"
        )
        assert synth_spec is not None and synth_spec.loader is not None
        synth = importlib.util.module_from_spec(synth_spec)
        synth_spec.loader.exec_module(synth)
        self.assertEqual(ftj.CONFIDENCE_THRESHOLD, synth.CONFIDENCE_THRESHOLD)


class TestRepoNameWithDot(unittest.TestCase):
    """Owner/repo regex must accept `.` in the repo name (e.g. `react.dev`,
    `next.js`, `lodash.fp`). Permalink was silently omitted before the fix.
    """

    def test_repo_name_with_dot_resolves_https(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            subprocess.run(
                ["git", "init", "-q", str(repo)],
                check=True, capture_output=True,
            )
            subprocess.run(
                ["git", "-C", str(repo), "remote", "add",
                 "origin", "https://github.com/owner/react.dev"],
                check=True, capture_output=True,
            )
            self.assertEqual(ftj.detect_owner_repo(repo), "owner/react.dev")

    def test_repo_name_with_dot_resolves_ssh(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            subprocess.run(
                ["git", "init", "-q", str(repo)],
                check=True, capture_output=True,
            )
            subprocess.run(
                ["git", "-C", str(repo), "remote", "add",
                 "origin", "git@github.com:owner/react.dev.git"],
                check=True, capture_output=True,
            )
            self.assertEqual(ftj.detect_owner_repo(repo), "owner/react.dev")


if __name__ == "__main__":
    unittest.main()
