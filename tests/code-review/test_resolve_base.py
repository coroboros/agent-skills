"""Tests for skills/code-review/scripts/resolve_base.sh.

Strategy: build a fresh tempdir git repo per ladder rung, run the script
with cwd=repo, and assert the parsed `RESULT:` line + exit code. Git config
is isolated (GIT_CONFIG_GLOBAL/SYSTEM=/dev/null) and identity is forced via
env so the suite is deterministic on any contributor's machine.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "code-review" / "scripts" / "resolve_base.sh"

BASH = shutil.which("bash") or "/bin/bash"
_GIT = shutil.which("git")
GIT = _GIT or "git"


def _env(cwd: Path) -> dict:
    env = os.environ.copy()
    env["GIT_CEILING_DIRECTORIES"] = str(Path(cwd).parent)
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_AUTHOR_NAME"] = "t"
    env["GIT_AUTHOR_EMAIL"] = "t@t"
    env["GIT_COMMITTER_NAME"] = "t"
    env["GIT_COMMITTER_EMAIL"] = "t@t"
    return env


def _git(cwd: Path, *args: str) -> str:
    r = subprocess.run(
        [GIT, *args], cwd=cwd, env=_env(cwd),
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0:
        raise AssertionError(f"git {args} failed: {r.stderr}")
    return r.stdout.strip()


def _run(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [BASH, str(SCRIPT), *args], cwd=cwd, env=_env(cwd),
        capture_output=True, text=True, timeout=30,
    )


def _result(stdout: str) -> dict:
    line = next(
        (ln for ln in stdout.splitlines() if ln.startswith("RESULT:")), ""
    )
    out: dict[str, str] = {}
    for tok in line[len("RESULT:"):].strip().split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k] = v
    return out


def _new_repo(tmp: Path, default: str = "main") -> Path:
    """init + point the unborn HEAD at `default` (works on any git version)."""
    repo = tmp / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "symbolic-ref", "HEAD", f"refs/heads/{default}")
    return repo


def _commit(repo: Path, msg: str) -> str:
    _git(repo, "commit", "--allow-empty", "-q", "-m", msg)
    return _git(repo, "rev-parse", "HEAD")


@unittest.skipUnless(_GIT, "git required")
class TestExplicitOverride(unittest.TestCase):
    def test_b_flag_wins(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _commit(repo, "c1")
            r = _run(repo, "-b", "origin/release")
        self.assertEqual(r.returncode, 0, r.stderr)
        res = _result(r.stdout)
        self.assertEqual(res["rule"], "explicit")
        self.assertEqual(res["base"], "origin/release")
        self.assertEqual(res["target"], "HEAD")


@unittest.skipUnless(_GIT, "git required")
class TestFeatureMergeBase(unittest.TestCase):
    def test_feature_branch_uses_merge_base(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            root = _commit(repo, "root")
            _git(repo, "checkout", "-q", "-b", "feature")
            _commit(repo, "feature work")
            r = _run(repo)
        self.assertEqual(r.returncode, 0, r.stderr)
        res = _result(r.stdout)
        self.assertEqual(res["rule"], "feature-merge-base")
        self.assertEqual(res["base"], root)

    def test_merge_base_via_origin_fallback(self):
        """Local default branch absent (only origin/<default> exists):
        rung 2's `origin/<default>` fallback must still resolve."""
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            bare = tmp / "origin.git"
            bare.mkdir()
            _git(bare, "init", "-q", "--bare")
            repo = _new_repo(tmp)
            root = _commit(repo, "root")
            _git(repo, "remote", "add", "origin", str(bare))
            _git(repo, "push", "-q", "-u", "origin", "main")
            _git(repo, "remote", "set-head", "origin", "main")
            _git(repo, "checkout", "-q", "-b", "feature")
            _commit(repo, "feature work")
            _git(repo, "branch", "-D", "main")  # only origin/main remains
            r = _run(repo)
        self.assertEqual(r.returncode, 0, r.stderr)
        res = _result(r.stdout)
        self.assertEqual(res["rule"], "feature-merge-base")
        self.assertEqual(res["base"], root)


@unittest.skipUnless(_GIT, "git required")
class TestDefaultUpstream(unittest.TestCase):
    def test_on_default_with_upstream(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            bare = tmp / "origin.git"
            bare.mkdir()
            _git(bare, "init", "-q", "--bare")
            repo = _new_repo(tmp)
            _commit(repo, "c1")
            _git(repo, "remote", "add", "origin", str(bare))
            _git(repo, "push", "-q", "-u", "origin", "main")
            head = _git(repo, "rev-parse", "HEAD")
            r = _run(repo)
        self.assertEqual(r.returncode, 0, r.stderr)
        res = _result(r.stdout)
        self.assertEqual(res["rule"], "default-upstream")
        # base is now the merge-base sha (diffable ancestor), not the ref name
        self.assertEqual(res["base"], head)


@unittest.skipUnless(_GIT, "git required")
class TestDefaultNoUpstream(unittest.TestCase):
    def test_tag_preferred(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _commit(repo, "c1")
            c2 = _commit(repo, "c2")
            _git(repo, "tag", "1.0.0")
            _commit(repo, "c3")
            r = _run(repo)
        res = _result(r.stdout)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(res["rule"], "default-tag")
        # merge-base(1.0.0, HEAD) == the tagged commit (c2), a diffable ancestor
        self.assertEqual(res["base"], c2)

    def test_prev_when_no_tag(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _commit(repo, "c1")
            _commit(repo, "c2")
            r = _run(repo)
        res = _result(r.stdout)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(res["rule"], "default-prev")
        self.assertEqual(res["base"], "HEAD~1")

    def test_initial_single_commit(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _commit(repo, "only")
            empty_tree = _git(repo, "hash-object", "-t", "tree", os.devnull)
            r = _run(repo)
        res = _result(r.stdout)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(res["rule"], "default-initial")
        self.assertEqual(res["base"], empty_tree)


@unittest.skipUnless(_GIT, "git required")
class TestUnresolvable(unittest.TestCase):
    def test_no_commits(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            r = _run(repo)
        self.assertEqual(r.returncode, 2)
        self.assertEqual(_result(r.stdout).get("rule"), "unresolvable")
        self.assertIn("no commits", r.stdout)

    def test_detached_head(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _commit(repo, "c1")
            _commit(repo, "c2")
            _git(repo, "checkout", "-q", "--detach", "HEAD")
            r = _run(repo)
        self.assertEqual(r.returncode, 2)
        self.assertIn("detached HEAD", r.stdout)

    def test_no_merge_base_unrelated_histories(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _commit(repo, "main root")
            _git(repo, "checkout", "-q", "--orphan", "feature")
            _commit(repo, "orphan root")
            r = _run(repo)
        self.assertEqual(r.returncode, 2)
        res = _result(r.stdout)
        self.assertEqual(res.get("rule"), "unresolvable")
        self.assertIn("no merge-base", r.stdout)

    def test_bad_flag(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _commit(repo, "c1")
            r = _run(repo, "-z")
        self.assertEqual(r.returncode, 2)
        self.assertEqual(_result(r.stdout).get("rule"), "unresolvable")


if __name__ == "__main__":
    unittest.main()
