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


def _read_main_readme() -> str | None:
    """Return the content of README.md as it lives on the main branch.

    Tries `main` then `origin/main`. Returns None when neither ref is
    reachable — CI checkouts with `fetch-depth: 1` only see the PR head;
    skip the main-corpus sanity checks in that case rather than failing.
    """
    for ref in ("main", "origin/main"):
        result = subprocess.run(
            ["git", "show", f"{ref}:README.md"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout
    return None


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


class TestAuthoringProcessTrace(unittest.TestCase):
    def test_path_anchored_brand_voice_flagged_high(self):
        findings = _run("--pr-body-file", str(FIX / "pr-body-authoring-trace.md"))
        traces = [f for f in findings if f["category"] == "authoring-process-trace"]
        self.assertGreaterEqual(len(traces), 4)
        self.assertTrue(all(f["severity"] == "High" for f in traces))
        self.assertTrue(all(f["confidence"] >= 80 for f in traces))

    def test_pattern_tags_cover_all_families(self):
        findings = _run("--pr-body-file", str(FIX / "pr-body-authoring-trace.md"))
        patterns = {
            f["meta"]["pattern"]
            for f in findings
            if f["category"] == "authoring-process-trace"
        }
        self.assertIn("brand-voice-path", patterns)
        self.assertIn("brand-voice-path-filename", patterns)
        self.assertIn("internal-tooling", patterns)
        self.assertTrue(
            {"maintainer-specific", "maintainer-possessive"} & patterns,
            f"expected at least one maintainer-* hit, got {patterns}",
        )

    def test_bare_brand_voice_mentions_not_flagged(self):
        # Plain mentions of the public `brand-voice` skill and bare
        # `BRAND-VOICE.md` (no path prefix) must not fire — patterns are
        # anchored on path-context, not on the bare slug or filename.
        findings = _run("--pr-body-file", str(FIX / "pr-body-clean.md"))
        self.assertNotIn("authoring-process-trace", _categories(findings))

    def test_skill_md_classifies_as_leak_only(self):
        # SKILL.md is Tier 2 (leak-only): it passes through filter_scope
        # but only the leak / signature / authoring-process checks run on
        # it. The style/length/vocab checks are prose contracts that do
        # not apply to model-instruction files.
        self.assertEqual(
            detector.classify_scope("skills/code-ultrareview/SKILL.md"),
            "leak-only",
        )
        self.assertIn(
            "skills/code-ultrareview/SKILL.md",
            detector.filter_scope([
                "skills/code-ultrareview/SKILL.md",
                "README.md",
            ]),
        )

    def test_authoring_trace_fires_on_skill_md_leak(self):
        # A model-instruction file that accidentally cites an authoring
        # path (`~/.claude/brand-voices/...`) is still a leak — Tier 2
        # runs the authoring-process-trace check.
        body = "Internal: see ~/.claude/brand-voices/example/BRAND-VOICE.md."
        with tempfile.NamedTemporaryFile(
            "w", prefix="SKILL_", suffix=".md", delete=False
        ) as fh:
            fh.write(body)
            path = fh.name
        findings = _run("--prose-file", path)
        traces = [
            f for f in findings
            if f["category"] == "authoring-process-trace"
        ]
        self.assertTrue(
            traces,
            "Tier 2 should still emit authoring-process-trace findings",
        )

    def test_main_corpus_emits_no_authoring_trace(self):
        # Sanity check — running the new detector against the current main
        # README must produce zero authoring-process-trace findings. The
        # path-context anchor is what makes this hold; loosening the regex
        # will fire on legitimate `brand-voice` skill references.
        main_readme = _read_main_readme()
        if main_readme is None:
            self.skipTest("main README not reachable (shallow CI clone)")
        tmp_path = _write_tmp(main_readme)
        findings = _run("--prose-file", tmp_path)
        traces = [f for f in findings if f["category"] == "authoring-process-trace"]
        self.assertEqual(
            traces, [],
            f"unexpected authoring-process-trace findings on main README: {traces}",
        )


class TestDefensiveNegation(unittest.TestCase):
    def test_skill_subject_negation_flagged_medium(self):
        findings = _run("--pr-body-file", str(FIX / "pr-body-defensive-negation.md"))
        negs = [f for f in findings if f["category"] == "defensive-negation"]
        self.assertTrue(negs, "expected defensive-negation findings on the fixture")
        self.assertTrue(all(f["severity"] == "Medium" for f in negs))
        self.assertTrue(all(f["confidence"] >= 70 for f in negs))

    def test_pattern_tags_cover_all_families(self):
        findings = _run("--pr-body-file", str(FIX / "pr-body-defensive-negation.md"))
        patterns = {
            f["meta"]["pattern"]
            for f in findings
            if f["category"] == "defensive-negation"
        }
        self.assertIn("skill-subject-negation", patterns)
        self.assertIn("defensive-scoping", patterns)
        self.assertIn("anchored-negation", patterns)

    def test_clean_fixture_emits_no_findings(self):
        # Mandate / behavioral-contract forms (NEVER commit secrets, never
        # aborts, never silent-drops) live in the clean fixture and must
        # not fire on their own — bare defensive patterns are absent.
        findings = _run("--pr-body-file", str(FIX / "pr-body-clean.md"))
        self.assertNotIn("defensive-negation", _categories(findings))

    def test_uppercase_NEVER_allowlist_suppresses_on_same_line(self):
        # A defensive-pattern match on the same line as the uppercase NEVER
        # mandate marker is suppressed — the line is policy, not scaffold.
        body = "The lens never names a thing — NEVER commit secrets is the rule."
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
            fh.write(body)
            path = fh.name
        findings = _run("--pr-body-file", path)
        negs = [f for f in findings if f["category"] == "defensive-negation"]
        self.assertEqual(negs, [], f"allowlist should suppress; got: {negs}")

    def test_never_aborts_allowlist_suppresses_on_same_line(self):
        body = "The lens never names any input — never aborts the review."
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
            fh.write(body)
            path = fh.name
        findings = _run("--pr-body-file", path)
        negs = [f for f in findings if f["category"] == "defensive-negation"]
        self.assertEqual(negs, [], f"allowlist should suppress; got: {negs}")

    def test_code_block_and_table_rows_skipped(self):
        body = (
            "Body text first.\n\n"
            "```\n"
            "The lens never names a thing.\n"
            "```\n\n"
            "| Header | Value |\n"
            "|---|---|\n"
            "| This skill never names any item | x |\n"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
            fh.write(body)
            path = fh.name
        findings = _run("--pr-body-file", path)
        negs = [f for f in findings if f["category"] == "defensive-negation"]
        self.assertEqual(negs, [], f"skip-regions should suppress; got: {negs}")

    def test_defensive_negation_skipped_on_leak_only_tier(self):
        # SKILL.md is Tier 2 (leak-only). Defensive-negation is a prose
        # contract that does not apply to model-instruction files, so
        # the dispatcher skips it for the leak-only tier — even when the
        # pattern matches the file content.
        body = "The lens never names a specific config file."
        with tempfile.NamedTemporaryFile(
            "w", prefix="CLAUDE_", suffix=".md", delete=False
        ) as fh:
            fh.write(body)
            path = fh.name
        # Confirm the test path classifies as leak-only (tempfile names
        # include `CLAUDE_` prefix but live in /tmp, so they don't match
        # Tier 1's repo-relative patterns).
        self.assertEqual(detector.classify_scope(path), "leak-only")
        findings = _run("--prose-file", path)
        negs = [f for f in findings if f["category"] == "defensive-negation"]
        self.assertEqual(
            negs, [],
            "Tier 2 should skip defensive-negation; got: " + str(negs),
        )

    def test_main_corpus_fp_rate_under_threshold(self):
        # WS-C ship-or-defer sanity check. Running the detector against the
        # current main README should produce ≤2 defensive-negation findings.
        # >2 means the heuristic over-fires on legitimate prose; tighten the
        # patterns or defer the category to a follow-up version.
        main_readme = _read_main_readme()
        if main_readme is None:
            self.skipTest("main README not reachable (shallow CI clone)")
        tmp_path = _write_tmp(main_readme)
        findings = _run("--prose-file", tmp_path)
        negs = [f for f in findings if f["category"] == "defensive-negation"]
        self.assertLessEqual(
            len(negs), 2,
            f"FP rate too high on main README: {len(negs)} hits — tighten patterns. "
            f"Hits: {negs}",
        )


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
    def test_classify_scope_assigns_correct_tiers(self):
        cases = {
            # Tier 1 — full prose
            "README.md": "full",
            "README.en.md": "full",
            "CHANGELOG.md": "full",
            "RELEASE-NOTES.md": "full",
            "RELEASE_NOTES.md": "full",
            "CONTRIBUTING.md": "full",
            "docs/intro.md": "full",
            "docs/guide/api.mdx": "full",
            # Tier 2 — leak-only (model-instruction files + source code)
            "skills/code-ultrareview/SKILL.md": "leak-only",
            "CLAUDE.md": "leak-only",
            "AGENTS.md": "leak-only",
            ".cursorrules": "leak-only",
            ".claude/rules/writing.md": "leak-only",
            ".cursor/rules.md": "leak-only",
            "skills/forge/evals/evals.json": "leak-only",
            "src/foo.py": "leak-only",
            "lib/util.ts": "leak-only",
            "internal/server.go": "leak-only",
            "scripts/build.sh": "leak-only",
            # Skip — build artifacts
            "dist/bundle.js": "skip",
            "build/output.js": "skip",
            "node_modules/foo/package.json": "skip",
            "pnpm-lock.yaml": "skip",
            "yarn.lock": "skip",
            "bundle.min.js": "skip",
            "app.min.css": "skip",
            "foo.pyc": "skip",
            "lib.so": "skip",
            "coverage/lcov.info": "skip",
            "__pycache__/cached.pyc": "skip",
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                self.assertEqual(detector.classify_scope(path), expected)

    def test_classify_scope_handles_windows_paths(self):
        # Backslashes normalize to forward slashes before classification.
        self.assertEqual(
            detector.classify_scope(r"skills\code-ultrareview\SKILL.md"),
            "leak-only",
        )
        self.assertEqual(
            detector.classify_scope(r"dist\bundle.js"),
            "skip",
        )
        self.assertEqual(
            detector.classify_scope(r"docs\intro.md"),
            "full",
        )

    def test_filter_scope_drops_skip_tier_only(self):
        kept = detector.filter_scope([
            "README.md",                          # full → kept
            "skills/code-ultrareview/SKILL.md",   # leak-only → kept
            "CLAUDE.md",                          # leak-only → kept
            ".claude/rules/writing.md",           # leak-only → kept
            "src/foo.py",                         # leak-only → kept
            "dist/bundle.js",                     # skip → dropped
            "node_modules/lib/index.js",          # skip → dropped
            "pnpm-lock.yaml",                     # skip → dropped
        ])
        self.assertEqual(
            set(kept),
            {
                "README.md",
                "skills/code-ultrareview/SKILL.md",
                "CLAUDE.md",
                ".claude/rules/writing.md",
                "src/foo.py",
            },
        )


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
