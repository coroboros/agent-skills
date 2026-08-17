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


def _run(*args, env=None, overlay=OVERLAY):
    return subprocess.run(
        [BASH, str(overlay), *args],
        capture_output=True,
        text=True,
        env=env if env is not None else os.environ.copy(),
        timeout=30,
    )


def _write_package_json(target: Path, content: str = '{"name": "project-name"}'):
    (target / "package.json").write_text(content, encoding="utf-8")


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

    def test_extra_or_unknown_argument_is_rejected(self):
        with tempfile.TemporaryDirectory() as target:
            for args in (("unexpected",), ("--force", "extra")):
                with self.subTest(args=args):
                    result = _run("next-cloudflare", "my-app", target, *args)
                    self.assertEqual(result.returncode, 2)

    def test_missing_target_dir_flagged(self):
        with tempfile.TemporaryDirectory() as t:
            ghost = Path(t) / "does-not-exist"
            r = _run("next-cloudflare", "my-app", str(ghost))
        self.assertEqual(r.returncode, 1)
        self.assertIn("target_dir does not exist", r.stderr)

    def test_invalid_project_name_fails_before_writing(self):
        for project_name in ("has spaces", "unsafe&name"):
            with self.subTest(project_name=project_name):
                with tempfile.TemporaryDirectory() as t:
                    target = Path(t)
                    r = _run("next-cloudflare", project_name, str(target))
                    self.assertEqual(r.returncode, 1)
                    self.assertIn("RESULT: error=invalid-project-name", r.stdout)
                    self.assertEqual(list(target.iterdir()), [])

    def test_invalid_cloudflare_service_name_fails_before_writing(self):
        for project_name in ("a" * 64, "name-"):
            with self.subTest(project_name=project_name):
                with tempfile.TemporaryDirectory() as t:
                    target = Path(t)
                    r = _run("next-cloudflare", project_name, str(target))
                    self.assertEqual(r.returncode, 1)
                    self.assertIn(
                        "RESULT: error=invalid-cloudflare-service-name",
                        r.stdout,
                    )
                    self.assertEqual(list(target.iterdir()), [])


class TestRequiredJsonInputs(unittest.TestCase):
    def test_missing_package_json_fails_before_any_write(self):
        with tempfile.TemporaryDirectory() as t:
            target = Path(t) / "proj"
            target.mkdir()

            result = _run("next-cloudflare", "demo", str(target))

            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("RESULT: error=package-json-missing", result.stderr)
            self.assertEqual(list(target.iterdir()), [])

    def test_missing_scripts_json_fails_before_any_write(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            isolated_skill = root / "scaffold"
            shutil.copytree(SKILL_DIR, isolated_skill)
            (isolated_skill / "templates/next-cloudflare/scripts.json").unlink()
            target = root / "proj"
            target.mkdir()
            original_package = '{"name": "project-name"}\n'
            _write_package_json(target, original_package)

            result = _run(
                "next-cloudflare",
                "demo",
                str(target),
                overlay=isolated_skill / "scripts/overlay_templates.sh",
            )

            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("RESULT: error=source-missing", result.stderr)
            self.assertEqual((target / "package.json").read_text(), original_package)
            self.assertEqual(
                sorted(path.name for path in target.iterdir()),
                ["package.json"],
            )


class TestTokenSubstitution(unittest.TestCase):
    """biome.json.template contains [Project Name] — verify substitution."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.target = Path(self._tmp.name) / "proj"
        self.target.mkdir()
        _write_package_json(self.target)

    def tearDown(self):
        self._tmp.cleanup()

    def test_project_name_substituted_in_agents_md(self):
        # AGENTS.md templates contain `[Project Name]` — the canonical token
        # used by the substitution pass. Verify it's replaced post-run.
        src = (TEMPLATES / "astro-cloudflare" / "AGENTS.md").read_text()
        self.assertIn("[Project Name]", src, "template lost its token — test stale")

        r = _run("astro-cloudflare", "my-cool-app", str(self.target))
        self.assertEqual(r.returncode, 0, msg=f"stderr={r.stderr}\nstdout={r.stdout}")
        out = (self.target / "AGENTS.md").read_text()
        self.assertNotIn("[Project Name]", out)
        self.assertIn("my-cool-app", out)
        self.assertEqual((self.target / "CLAUDE.md").read_text(), "@AGENTS.md\n")

    def test_runtime_prerequisite_templates_are_generated(self):
        result = _run("astro-cloudflare", "my-cool-app", str(self.target))

        self.assertEqual(
            result.returncode,
            0,
            msg=f"stderr={result.stderr}\nstdout={result.stdout}",
        )
        self.assertEqual(
            (self.target / ".node-version").read_text(encoding="utf-8"),
            "22.12.0\n",
        )
        self.assertIn(
            "Copy to .dev.vars",
            (self.target / ".dev.vars.example").read_text(encoding="utf-8"),
        )
        self.assertEqual(
            json.loads(
                (self.target / "tsconfig.json").read_text(encoding="utf-8")
            ),
            {"extends": "astro/tsconfigs/strict"},
        )

    def test_generator_gitignore_is_merged_without_duplicates(self):
        generated = "# create-next-app\n.next/\n/public-build\n"
        (self.target / ".gitignore").write_text(generated, encoding="utf-8")

        result = _run("next-cloudflare", "my-cool-app", str(self.target))

        self.assertEqual(
            result.returncode,
            0,
            msg=f"stderr={result.stderr}\nstdout={result.stdout}",
        )
        lines = (self.target / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[:3], generated.splitlines())
        self.assertEqual(lines.count(".next/"), 1)
        self.assertEqual(lines.count(".open-next/"), 1)
        self.assertIn("node_modules/", lines)
        self.assertIn("RESULT: merged-gitignore=", result.stdout)

    def test_generated_rules_use_cross_agent_paths(self):
        for scaffold in ("astro-cloudflare", "next-cloudflare"):
            with self.subTest(scaffold=scaffold):
                target = self.target / scaffold
                target.mkdir()
                _write_package_json(target)
                r = _run(scaffold, "demo", str(target))
                self.assertEqual(
                    r.returncode,
                    0,
                    msg=f"stderr={r.stderr}\nstdout={r.stdout}",
                )
                self.assertTrue((target / "AGENTS.md").is_file())
                self.assertEqual((target / "CLAUDE.md").read_text(), "@AGENTS.md\n")
                self.assertTrue(
                    (target / ".agents/rules/cloudflare-tooling.md").is_file()
                )
                self.assertEqual((target / ".claude").exists(), False)

        self.assertTrue(
            (self.target / "astro-cloudflare/.agents/rules/seo.md").is_file()
        )
        self.assertFalse(
            (self.target / "next-cloudflare/.agents/rules/seo.md").exists()
        )

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
        self.assertEqual(pkg["name"], "my-cool-app")
        self.assertEqual(pkg.get("type"), "module")
        self.assertTrue(pkg.get("private"))
        # Scripts merged from template (template provides at least `dev` or
        # similar — assert we have *something* beyond the original).
        self.assertIn("scripts", pkg)

    def test_scoped_project_name_uses_safe_machine_slug(self):
        r = _run("next-cloudflare", "@scope/my_app", str(self.target))

        self.assertEqual(r.returncode, 0, msg=f"stderr={r.stderr}\nstdout={r.stdout}")
        self.assertIn("@scope/my_app", (self.target / "AGENTS.md").read_text())
        package = json.loads((self.target / "package.json").read_text())
        self.assertEqual(package["name"], "@scope/my_app")
        wrangler = json.loads(
            "\n".join(
                line for line in (self.target / "wrangler.jsonc").read_text().splitlines()
                if not line.lstrip().startswith("//")
            )
        )
        self.assertEqual(wrangler["name"], "scope-my-app")

    def test_tailwind_import_and_astro_entrypoint_are_generated(self):
        next_target = self.target / "next"
        next_target.mkdir()
        _write_package_json(next_target)
        next_css = next_target / "src/app/globals.css"
        next_css.parent.mkdir(parents=True)
        next_css.write_text("@theme { --color-brand: red; }\n", encoding="utf-8")

        next_result = _run("next-cloudflare", "next-app", str(next_target))

        self.assertEqual(
            next_result.returncode,
            0,
            msg=f"stderr={next_result.stderr}\nstdout={next_result.stdout}",
        )
        next_output = next_css.read_text(encoding="utf-8")
        self.assertTrue(next_output.startswith('@import "tailwindcss";\n'))
        self.assertIn("--color-brand: red", next_output)

        astro_target = self.target / "astro"
        astro_target.mkdir()
        _write_package_json(astro_target)

        astro_result = _run("astro-cloudflare", "astro-app", str(astro_target))

        self.assertEqual(
            astro_result.returncode,
            0,
            msg=f"stderr={astro_result.stderr}\nstdout={astro_result.stdout}",
        )
        self.assertEqual(
            (astro_target / "src/styles/global.css").read_text(encoding="utf-8"),
            '@import "tailwindcss";\n',
        )
        astro_page = (astro_target / "src/pages/index.astro").read_text(
            encoding="utf-8"
        )
        self.assertIn('import "../styles/global.css";', astro_page)
        self.assertIn("<title>astro-app</title>", astro_page)

    def test_astro_minimal_generator_fixture_reaches_controlled_overlay(self):
        target = self.target / "astro-minimal"
        target.mkdir()
        _write_package_json(target)
        generated_readme = "# Astro Starter Kit: Minimal\n"
        (target / "README.md").write_text(generated_readme, encoding="utf-8")
        (target / "astro.config.mjs").write_text(
            "import { defineConfig } from 'astro/config';\n\n"
            "// https://astro.build/config\n"
            "export default defineConfig({});\n",
            encoding="utf-8",
        )
        (target / "tsconfig.json").write_text(
            '{"extends":"astro/tsconfigs/strict"}\n', encoding="utf-8"
        )
        generated_page = target / "src/pages/index.astro"
        generated_page.parent.mkdir(parents=True)
        generated_page.write_text("<h1>Astro</h1>\n", encoding="utf-8")

        setup = (
            SKILL_DIR / "references/setup-astro-cloudflare.md"
        ).read_text(encoding="utf-8")
        for relative in (
            "astro.config.mjs",
            "tsconfig.json",
            "src/pages/index.astro",
        ):
            self.assertIn(f"`{relative}`", setup)
            (target / relative).unlink()

        result = _run("astro-cloudflare", "astro-minimal", str(target))

        self.assertEqual(
            result.returncode,
            0,
            msg=f"stderr={result.stderr}\nstdout={result.stdout}",
        )
        self.assertIn("@astrojs/cloudflare", (target / "astro.config.mjs").read_text())
        self.assertEqual((target / "README.md").read_text(), generated_readme)

    def test_force_does_not_duplicate_tailwind_import(self):
        first = _run("astro-cloudflare", "demo", str(self.target))
        second = _run("astro-cloudflare", "demo", str(self.target), "--force")

        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        css = (self.target / "src/styles/global.css").read_text(encoding="utf-8")
        self.assertEqual(css.count('@import "tailwindcss";'), 1)


class TestIdempotency(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.target = Path(self._tmp.name) / "proj"
        self.target.mkdir()
        _write_package_json(self.target)

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


class TestSafeDestinations(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.target = self.root / "proj"
        self.target.mkdir()
        _write_package_json(self.target)
        self.outside = self.root / "outside"
        self.outside.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def _assert_preflight_rejected_without_writes(self, result):
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("RESULT: error=unsafe-destination", result.stdout)
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.assertEqual(
            list(self.target.glob(".overlay.*"))
            + list(self.target.rglob(".overlay.*")),
            [],
        )

    def test_existing_destination_symlink_is_rejected(self):
        outside_file = self.outside / "biome.json"
        outside_file.write_text("outside\n", encoding="utf-8")
        (self.target / "biome.json").symlink_to(outside_file)

        result = _run("next-cloudflare", "demo", str(self.target), "--force")

        self._assert_preflight_rejected_without_writes(result)
        self.assertIn("reason=symlink-destination", result.stdout)
        self.assertEqual(outside_file.read_text(encoding="utf-8"), "outside\n")

    def test_dangling_destination_symlink_is_rejected(self):
        outside_file = self.outside / "missing-biome.json"
        (self.target / "biome.json").symlink_to(outside_file)

        result = _run("next-cloudflare", "demo", str(self.target), "--force")

        self._assert_preflight_rejected_without_writes(result)
        self.assertIn("reason=symlink-destination", result.stdout)
        self.assertFalse(outside_file.exists())

    def test_parent_symlink_is_rejected_before_any_write(self):
        (self.target / ".agents").symlink_to(self.outside, target_is_directory=True)

        result = _run("next-cloudflare", "demo", str(self.target), "--force")

        self._assert_preflight_rejected_without_writes(result)
        self.assertIn("reason=symlink-parent", result.stdout)
        self.assertEqual(list(self.outside.iterdir()), [])


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
                [BASH, "-c", "command -v jq"], env=env, capture_output=True, text=True,
                timeout=30,
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
            self.assertEqual(
                sorted(path.name for path in target.iterdir()),
                ["package.json"],
                "jq-missing failure wrote templates before prerequisite checks",
            )

            # No .tmp debris anywhere in target. mktemp is never reached on
            # this path, but pin the contract so a regression that moves
            # mktemp above the jq check surfaces here.
            debris = list(target.rglob("*.tmp")) + list(target.rglob(".tmp.*"))
            self.assertEqual(debris, [],
                             f"jq-missing left temp files in target: {debris}")


if __name__ == "__main__":
    unittest.main()
