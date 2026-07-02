"""Pins the `{project}` derivation — the keystone of the global-output scheme.

Two contracts, both load-bearing and previously unverified (code-review
finding #1 + #2):

1. The bash kebab (`basename | tr lower | tr -cs a-z0-9 - | sed strip`) must
   match the documented behavior on adversarial repo basenames, including the
   empty case → `unnamed` (a basename with zero [a-z0-9] used to yield an
   empty segment and a malformed/colliding path).
2. The four apex scripts MUST derive an IDENTICAL `{project}` for the same
   root — `setup-templates.sh:35-37` states this as a contract ("divergence
   strands output where the sibling scripts can't find it"). Each script was
   tested in isolation; nothing pinned that they agree.

Strategy: run the real scripts with cwd=<adversarially-named dir>, an
isolated HOME, and GIT_CEILING capping the git walk so PROJECT_ROOT == pwd
deterministically. Extract the `<project>` path segment each script emits.
"""

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
APEX_SCRIPTS = REPO_ROOT / "skills" / "apex" / "scripts"
BASH = shutil.which("bash") or "/bin/bash"

# Basename → expected {project}. Mirrors the bash pipeline + the empty fallback.
CASES = {
    "agent-skills": "agent-skills",
    "My Repo": "my-repo",
    "REPO!!!": "repo",
    "a.b.c": "a-b-c",
    "--x--": "x",
    "Café": "caf",          # `tr -cs a-z0-9` drops non-ASCII (documented)
    "123ABC": "123abc",
    "+++": "unnamed",       # all-non-alphanumeric → empty kebab → fallback
    "___": "unnamed",
}

_SEG = re.compile(r"/\.agents/output/([^/\s]+)/apex")


def _expected(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "unnamed"


def _run(script: str, *args, cwd: Path, home: Path):
    env = os.environ.copy()
    env["HOME"] = str(home)
    env["GIT_CEILING_DIRECTORIES"] = str(cwd.parent)  # PROJECT_ROOT → pwd == cwd
    return subprocess.run(
        [BASH, str(APEX_SCRIPTS / script), *args],
        cwd=str(cwd), env=env, capture_output=True, text=True, timeout=30,
    )


def _project_from(text: str):
    m = _SEG.search(text)
    return m.group(1) if m else None


class TestKebabDerivation(unittest.TestCase):
    """The Python mirror (`CASES`) and the real bash must agree, via the
    canonical producer setup-templates.sh, for every adversarial basename."""

    def test_cases_match_python_mirror(self):
        for name, expected in CASES.items():
            self.assertEqual(_expected(name), expected,
                             f"mirror disagrees for {name!r}")

    def test_setup_templates_derives_documented_project(self):
        for name, expected in CASES.items():
            with self.subTest(basename=name), tempfile.TemporaryDirectory() as t:
                root = Path(t) / name
                home = Path(t) / "home"
                root.mkdir()
                home.mkdir()
                r = _run("setup-templates.sh", "feat", "desc",
                         "false", "true", "false", "false", "false", "", "in",
                         cwd=root, home=home)
                self.assertEqual(r.returncode, 0,
                                 f"{name!r}: stderr={r.stderr}")
                proj = _project_from(r.stdout)
                self.assertEqual(
                    proj, expected,
                    f"basename {name!r}: script→{proj!r}, expected {expected!r}",
                )
                # Never an empty {project} segment on disk.
                self.assertNotIn("/output//", r.stdout)


class TestSiblingConsistency(unittest.TestCase):
    """All four apex scripts derive the SAME {project} for one root — the
    contract setup-templates.sh's own comment declares load-bearing. Each
    runs with a fresh HOME so it surfaces its computed path via its
    target-missing branch (or OUTPUT_DIR for the producer)."""

    NAME = "My Weird Repo!!!"   # exercises spaces + symbols together

    def _proj(self, t, script, *args):
        root = Path(t) / self.NAME
        home = Path(t) / f"home-{script}"
        root.mkdir(exist_ok=True)
        home.mkdir()
        r = _run(script, *args, cwd=root, home=home)
        return _project_from(r.stdout + r.stderr)

    def test_four_scripts_agree(self):
        expected = _expected(self.NAME)  # → my-weird-repo
        with tempfile.TemporaryDirectory() as t:
            derived = {
                "setup-templates.sh": self._proj(
                    t, "setup-templates.sh", "feat", "d",
                    "false", "true", "false", "false", "false", "", "in"),
                "resume_lookup.sh": self._proj(
                    t, "resume_lookup.sh", "01"),            # apex-dir-missing
                "update-progress.sh": self._proj(
                    t, "update-progress.sh", "01-x", "01", "analyze",
                    "complete"),                              # context-missing
                "validate_state.sh": self._proj(
                    t, "validate_state.sh", "01-x", "2"),    # task-missing
            }
        for script, proj in derived.items():
            self.assertEqual(
                proj, expected,
                f"{script} derived {proj!r}, expected {expected!r} — "
                f"sibling-consistency contract broken",
            )
        self.assertEqual(len(set(derived.values())), 1,
                         f"scripts disagree: {derived}")


if __name__ == "__main__":
    unittest.main()
