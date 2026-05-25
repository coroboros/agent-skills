"""Unit tests for scripts/check_prose_hygiene.py — the prose-hygiene detector."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "code-ultrareview"
SCRIPT = SKILL_DIR / "scripts" / "check_prose_hygiene.py"
FIX = Path(__file__).resolve().parent / "fixtures" / "prose-hygiene"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


detector = _load("check_prose_hygiene", SCRIPT)


def _run(*args: str) -> list[dict]:
    """Invoke the script as a subprocess and parse the JSON findings."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def _commits_payload(records: list[tuple[str, str, str]]) -> str:
    """Build a NUL-delimited commits payload matching fetch_commits.sh.

    Each record is `(sha, subject, body)`. Format: `<sha>\\0<subject>\\0<body>\\0---\\n`.
    Markdown fixture files cannot carry NUL bytes, so this helper builds them
    in-memory and writes to a tmp file when the test needs `--commits-file`.
    """
    out = [f"RESULT: base=test commit_count={len(records)}"]
    for sha, subject, body in records:
        out.append(f"{sha}\x00{subject}\x00{body}\x00---")
    return "\n".join(out) + "\n"


def _commits_with_ai_footer() -> str:
    return _commits_payload([
        (
            "deadbeefcafebabedeadbeefcafebabedeadbeef",
            "feat(prose-hygiene): add lens",
            "This commit adds the lens.\n\nCo-Authored-By: Claude <noreply@anthropic.com>\n\n🤖 Generated with Claude Code",
        ),
        (
            "1234567890abcdef1234567890abcdef12345678",
            "nope something",
            "",
        ),
    ])


def _commits_cc_clean() -> str:
    return _commits_payload([
        ("1111111111111111111111111111111111111111", "feat(prose-hygiene): add lens", ""),
        ("2222222222222222222222222222222222222222", "fix(scripts): handle missing gh", ""),
        ("3333333333333333333333333333333333333333", "docs(readme): document --no-prose-hygiene", ""),
    ])


def _write_tmp(text: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
        fh.write(text)
        return fh.name


def _categories(findings: list[dict]) -> set[str]:
    return {f["category"] for f in findings}


class TestInternalLeaks(unittest.TestCase):
    def test_macos_home_path_flagged_high(self):
        findings = _run("--pr-body-file", str(FIX / "pr-body-leak.md"))
        leaks = [f for f in findings if f["category"] == "internal-leak"]
        # macOS path, personal email, and machine hostname all live in the fixture.
        self.assertGreaterEqual(len(leaks), 3)
        self.assertTrue(all(f["severity"] == "High" for f in leaks))
        self.assertTrue(all(f["confidence"] >= 80 for f in leaks))

    def test_macos_home_path_pattern_tag(self):
        findings = _run("--pr-body-file", str(FIX / "pr-body-leak.md"))
        patterns = {
            f["meta"]["pattern"]
            for f in findings
            if f["category"] == "internal-leak"
        }
        self.assertIn("macos-home-path", patterns)
        self.assertIn("personal-email", patterns)
        self.assertIn("machine-hostname", patterns)

    def test_clean_body_emits_no_leak_findings(self):
        findings = _run("--pr-body-file", str(FIX / "pr-body-clean.md"))
        self.assertNotIn("internal-leak", _categories(findings))


class TestSignatureFooters(unittest.TestCase):
    def test_claude_coauthor_in_commit_body_flagged(self):
        findings = _run("--commits-file", _write_tmp(_commits_with_ai_footer()))
        footers = [f for f in findings if f["category"] == "ai-signature-footer"]
        self.assertTrue(footers)
        self.assertTrue(all(f["severity"] == "High" for f in footers))
        patterns = {f["meta"]["pattern"] for f in footers}
        self.assertTrue({"claude-coauthor", "robot-generated-with"} & patterns)

    def test_clean_commits_emit_no_footer_findings(self):
        findings = _run("--commits-file", _write_tmp(_commits_cc_clean()))
        self.assertNotIn("ai-signature-footer", _categories(findings))


class TestRuleRestatement(unittest.TestCase):
    def test_no_ai_footer_restatement_flagged(self):
        findings = _run(
            "--pr-body-file", str(FIX / "pr-body-rule-restatement.md")
        )
        restate = [f for f in findings if f["category"] == "rule-restatement"]
        self.assertTrue(restate, "expected at least one rule-restatement finding")
        patterns = {f["meta"]["pattern"] for f in restate}
        self.assertIn("no-ai-footer-restatement", patterns)
        self.assertIn("followed-rule", patterns)
        self.assertIn("filler-test-plan", patterns)

    def test_section_header_alone_is_not_flagged(self):
        # Clean fixture has `## Summary` and `## Test plan` headers but no
        # restatement bullets — the headers must not trigger.
        findings = _run("--pr-body-file", str(FIX / "pr-body-clean.md"))
        self.assertNotIn("rule-restatement", _categories(findings))


class TestAIVocabulary(unittest.TestCase):
    def test_known_terms_flagged_low(self):
        findings = _run("--pr-body-file", str(FIX / "pr-body-ai-tells.md"))
        tells = [f for f in findings if f["category"] == "ai-vocabulary"]
        self.assertTrue(tells)
        self.assertTrue(all(f["severity"] == "Low" for f in tells))
        terms = {f["meta"]["term"] for f in tells}
        for expected in ("delve", "tapestry", "pivotal", "additionally", "moreover"):
            self.assertIn(expected, terms)

    def test_em_dash_density_flagged_when_high(self):
        findings = _run("--pr-body-file", str(FIX / "pr-body-ai-tells.md"))
        density = [f for f in findings if f["category"] == "em-dash-density"]
        self.assertTrue(density, "expected em-dash density finding on AI-tells fixture")

    def test_per_term_cap_bounds_noise(self):
        body = "delve " * 10
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
            fh.write(body)
            path = fh.name
        findings = _run("--pr-body-file", path)
        delve = [
            f for f in findings
            if f["category"] == "ai-vocabulary" and f["meta"]["term"] == "delve"
        ]
        # 10 occurrences in the fixture, but the per-term cap is 3.
        self.assertEqual(len(delve), 3)


class TestLengthOverflow(unittest.TestCase):
    def test_pr_body_above_hard_cap_flagged_medium(self):
        # 200 bullets → > 150 non-blank lines → Medium length-overflow.
        body = "## Summary\n" + "\n".join(
            f"- Bullet {i} describing some part of the change in adequate detail."
            for i in range(1, 201)
        ) + "\n"
        findings = _run("--pr-body-file", _write_tmp(body))
        overflow = [f for f in findings if f["category"] == "length-overflow"]
        med = [f for f in overflow if f["severity"] == "Medium"]
        self.assertTrue(med, "expected a Medium length-overflow finding")

    def test_pr_body_above_soft_cap_flagged_low(self):
        # Fixture sits between soft (80) and hard (150) caps → Low.
        findings = _run("--pr-body-file", str(FIX / "pr-body-overlong.md"))
        overflow = [f for f in findings if f["category"] == "length-overflow"]
        self.assertTrue(overflow, "expected at least one length-overflow finding")
        low = [f for f in overflow if f["severity"] == "Low"]
        self.assertTrue(low, "expected a Low length-overflow finding for soft-cap range")

    def test_clean_body_emits_no_length_findings(self):
        findings = _run("--pr-body-file", str(FIX / "pr-body-clean.md"))
        self.assertNotIn("length-overflow", _categories(findings))


class TestCommitShape(unittest.TestCase):
    def test_non_cc_commit_flagged_when_repo_adopts_cc(self):
        # Force CC adoption via a sentinel `.commitlintrc.json` in a tmp repo.
        commits_path = _write_tmp(_commits_with_ai_footer())
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            (tmp / ".commitlintrc.json").write_text("{}", encoding="utf-8")
            findings = _run(
                "--commits-file", commits_path,
                "--repo-root", str(tmp),
            )
        non_cc = [f for f in findings if f["category"] == "commit-shape-non-cc"]
        self.assertTrue(non_cc)
        adopted = [f for f in non_cc if f["meta"]["adopted"] is True]
        self.assertTrue(adopted, "adoption signal should mark these as Medium")
        self.assertTrue(all(f["severity"] == "Medium" for f in adopted))

    def test_non_cc_commit_informational_when_repo_does_not_adopt(self):
        commits_path = _write_tmp(_commits_with_ai_footer())
        with tempfile.TemporaryDirectory() as tmpdir:
            findings = _run(
                "--commits-file", commits_path,
                "--repo-root", tmpdir,
            )
        non_cc = [f for f in findings if f["category"] == "commit-shape-non-cc"]
        if non_cc:
            self.assertTrue(all(f["severity"] == "Low" for f in non_cc))

    def test_cc_subject_not_flagged(self):
        commits_path = _write_tmp(_commits_cc_clean())
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            (tmp / ".commitlintrc.json").write_text("{}", encoding="utf-8")
            findings = _run(
                "--commits-file", commits_path,
                "--repo-root", str(tmp),
            )
        self.assertNotIn("commit-shape-non-cc", _categories(findings))


class TestScopeFilter(unittest.TestCase):
    def test_skill_md_excluded_from_prose_files(self):
        kept = detector.filter_scope([
            "README.md",
            "skills/code-ultrareview/SKILL.md",
            "CLAUDE.md",
            ".claude/rules/writing.md",
            "evals.json",
            "skills/forge/templates/forge-artifact.md",
            "docs/intro.md",
        ])
        self.assertEqual(set(kept), {"README.md", "docs/intro.md"})

    def test_scope_filter_handles_windows_paths(self):
        kept = detector.filter_scope([r"skills\code-ultrareview\SKILL.md"])
        self.assertEqual(kept, [])


class TestEmptyInputs(unittest.TestCase):
    def test_no_inputs_returns_empty_list(self):
        findings = _run()
        self.assertEqual(findings, [])

    def test_missing_pr_body_file_path_does_not_crash(self):
        findings = _run("--pr-body-file", "/nonexistent/path/body.md")
        self.assertEqual(findings, [])


class TestDiscoveryHelpers(unittest.TestCase):
    def test_discover_rules_returns_existing_files_only(self):
        # The agent-skills repo has CLAUDE.md and .claude/rules/* — at
        # minimum CLAUDE.md should be discovered.
        paths = detector.discover_rules(REPO_ROOT)
        self.assertTrue(paths)
        for p in paths:
            self.assertTrue(Path(p).is_file(), f"discovered path missing: {p}")

    def test_cc_is_adopted_true_with_commitlintrc(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            (tmp / ".commitlintrc.json").write_text("{}", encoding="utf-8")
            self.assertTrue(detector.cc_is_adopted(tmp))

    def test_cc_is_adopted_false_on_empty_repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertFalse(detector.cc_is_adopted(Path(tmpdir)))

    def test_cc_is_adopted_true_via_package_json_dependency(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            (tmp / "package.json").write_text(
                json.dumps({"devDependencies": {"@commitlint/cli": "*"}}),
                encoding="utf-8",
            )
            self.assertTrue(detector.cc_is_adopted(tmp))


class TestCommitsParser(unittest.TestCase):
    def test_parses_inline_two_commits(self):
        text = _commits_with_ai_footer()
        commits = detector.parse_commits(text)
        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0]["sha"][:7], "deadbee")
        self.assertEqual(commits[1]["sha"][:7], "1234567")

    def test_strips_result_header_lines(self):
        text = "RESULT: base=abc commit_count=1\nsha\x00subj\x00body\x00---\n"
        commits = detector.parse_commits(text)
        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0]["sha"], "sha")
        self.assertEqual(commits[0]["subject"], "subj")


if __name__ == "__main__":
    unittest.main()
