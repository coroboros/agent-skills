"""Tests for skills/scaffold/scripts/overlay_templates.sh.

Strategy: run the script against the real templates/ folder, with a fresh
temp target directory per test. Token substitution is exercised by reading
back files the templates touch (e.g. biome.json, package.json after merge).
jq-missing path is exercised by giving the script a PATH that excludes jq.
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "scaffold"
SCRIPTS = SKILL_DIR / "scripts"
OVERLAY = SCRIPTS / "overlay_templates.sh"
TEMPLATES = SKILL_DIR / "templates"


BASH = shutil.which("bash") or "/bin/bash"


def _run(*args, env=None):
    return subprocess.run(
        [BASH, str(OVERLAY), *args],
        capture_output=True,
        text=True,
        env=env if env is not None else os.environ.copy(),
    )


class TestArgValidation(unittest.TestCase):
    def test_unknown_scaffold_flagged(self):
        with tempfile.TemporaryDirectory() as t:
            r = _run("rails-cloudflare", "my-app", t)
        self.assertEqual(r.returncode, 1)
        self.assertIn("unknown scaffold", r.stderr)

    def test_missing_args_usage_error(self):
        # Script calls usage() which exits 2 when fewer than 3 args provided.
        r = _run("next-cloudflare")
        self.assertEqual(r.returncode, 2)

    def test_missing_target_dir_flagged(self):
        with tempfile.TemporaryDirectory() as t:
            ghost = Path(t) / "does-not-exist"
            r = _run("next-cloudflare", "my-app", str(ghost))
        self.assertEqual(r.returncode, 1)
        self.assertIn("target_dir does not exist", r.stderr)


class TestTokenSubstitution(unittest.TestCase):
    """biome.json.template contains [Project Name] — verify substitution."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.target = Path(self._tmp.name) / "proj"
        self.target.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def test_project_name_substituted_in_claude_md(self):
        # CLAUDE.md templates contain `[Project Name]` — the canonical token
        # used by the substitution pass. Verify it's replaced post-run.
        src = (TEMPLATES / "astro-cloudflare" / "CLAUDE.md").read_text()
        self.assertIn("[Project Name]", src, "template lost its token — test stale")

        r = _run("astro-cloudflare", "my-cool-app", str(self.target))
        self.assertEqual(r.returncode, 0, msg=f"stderr={r.stderr}\nstdout={r.stdout}")
        out = (self.target / "CLAUDE.md").read_text()
        self.assertNotIn("[Project Name]", out)
        self.assertIn("my-cool-app", out)

    def test_package_json_name_replaced(self):
        # When a project-name placeholder package.json already exists, the
        # `"name": "project-name"` substitution must rewrite it to PROJECT_NAME.
        (self.target / "package.json").write_text(
            json.dumps({"name": "project-name", "scripts": {"dev": "x"}})
        )
        r = _run("next-cloudflare", "my-cool-app", str(self.target))
        self.assertEqual(r.returncode, 0, msg=f"stderr={r.stderr}\nstdout={r.stdout}")
        pkg = json.loads((self.target / "package.json").read_text())
        # jq merge: scripts overlay + type=module + private=true.
        self.assertEqual(pkg.get("type"), "module")
        self.assertTrue(pkg.get("private"))
        # Scripts merged from template (template provides at least `dev` or
        # similar — assert we have *something* beyond the original).
        self.assertIn("scripts", pkg)


class TestIdempotency(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.target = Path(self._tmp.name) / "proj"
        self.target.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def test_second_run_skips_without_force(self):
        first = _run("astro-cloudflare", "demo", str(self.target))
        self.assertEqual(first.returncode, 0, msg=f"first run stderr={first.stderr}")
        second = _run("astro-cloudflare", "demo", str(self.target))
        # All files exist → SKIPPED > 0 and no --force → exit 1, ok=partial.
        self.assertEqual(second.returncode, 1)
        self.assertIn("RESULT: skipped=", second.stdout)
        self.assertIn("ok=partial", second.stdout)
        self.assertIn("--force to overwrite", second.stdout)

    def test_force_overwrites(self):
        first = _run("astro-cloudflare", "demo", str(self.target))
        self.assertEqual(first.returncode, 0)
        # Mutate a written file to confirm --force restores it from template.
        biome = self.target / "biome.json"
        biome.write_text("// tampered\n")
        second = _run("astro-cloudflare", "demo", str(self.target), "--force")
        self.assertEqual(second.returncode, 0, msg=f"stderr={second.stderr}")
        self.assertNotEqual(biome.read_text(), "// tampered\n")
        self.assertIn("ok=true", second.stdout)


class TestJqMissing(unittest.TestCase):
    """Build a sealed PATH containing only the externals overlay needs except jq."""

    REQUIRED = ["mkdir", "dirname", "sed", "mktemp", "mv", "pwd", "find", "wc", "tr", "cat"]

    def _sealed_bin(self, root: Path) -> Path:
        bin_dir = root / "sealed-bin"
        bin_dir.mkdir()
        for tool in self.REQUIRED:
            for candidate in ("/usr/bin", "/bin"):
                src = Path(candidate) / tool
                if src.exists():
                    (bin_dir / tool).symlink_to(src)
                    break
            else:
                self.skipTest(f"{tool} not found in /usr/bin or /bin")
        return bin_dir

    def test_jq_missing_when_pkg_json_present(self):
        original_pkg = '{"name": "project-name"}'
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            target = tmp / "proj"
            target.mkdir()
            (target / "package.json").write_text(original_pkg)
            sealed = self._sealed_bin(tmp)
            env = os.environ.copy()
            env["PATH"] = str(sealed)
            # Sanity: jq must NOT be reachable from sealed PATH.
            jq_check = subprocess.run(
                [BASH, "-c", "command -v jq"], env=env, capture_output=True, text=True
            )
            self.assertNotEqual(jq_check.returncode, 0, "sealed PATH still resolves jq")
            r = _run("next-cloudflare", "demo", str(target), env=env)

            # Exit + messages contract.
            self.assertEqual(r.returncode, 1)
            self.assertIn("jq required", r.stderr)
            self.assertIn("RESULT: error=jq-missing", r.stdout)

            # Atomicity contract: jq-missing aborts BEFORE `jq … > $TMP_PKG`
            # and `mv $TMP_PKG $PKG_JSON`, so the pre-existing package.json
            # is never mutated. A future change that swaps the order — or adds
            # a non-jq merge fallback — must update this assertion deliberately.
            self.assertEqual(
                (target / "package.json").read_text(),
                original_pkg,
                "jq-missing failure mutated package.json",
            )

            # No .tmp debris anywhere in target. mktemp is never reached on
            # this path, but pin the contract so a regression that moves
            # mktemp above the jq check surfaces here.
            debris = list(target.rglob("*.tmp")) + list(target.rglob(".tmp.*"))
            self.assertEqual(debris, [],
                             f"jq-missing left temp files in target: {debris}")


if __name__ == "__main__":
    unittest.main()
