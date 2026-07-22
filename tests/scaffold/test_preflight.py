"""Tests for skills/scaffold/scripts/preflight.sh.

Strategy: build a per-test fake-bin directory containing stub `node`/`pnpm`
scripts, prepend it to PATH, and run preflight.sh against a temp target dir.
That gives full deterministic control over the version reported and over
presence/absence of each binary.
"""

import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "skills" / "scaffold" / "scripts"
PREFLIGHT = SCRIPTS / "preflight.sh"
BASH = shutil.which("bash") or "/bin/bash"


def _make_stub(bin_dir: Path, name: str, body: str) -> None:
    p = bin_dir / name
    p.write_text(body)
    p.chmod(p.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def _run(
    target_dir: Path,
    fake_bin: Path | None = None,
    project_name: str = "my-project",
    base_path: str = "/usr/bin:/bin:/usr/sbin:/sbin",
):
    env = os.environ.copy()
    # Keep only system essentials; prepend fake_bin so the stubs win.
    if fake_bin:
        env["PATH"] = (
            f"{fake_bin}:{base_path}" if base_path else str(fake_bin)
        )
    else:
        env["PATH"] = base_path
    return subprocess.run(
        [BASH, str(PREFLIGHT), str(target_dir), project_name],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )


class TestPreflightEnvironment(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.fake_bin = self.tmp / "bin"
        self.fake_bin.mkdir()
        self.target = self.tmp / "project"
        self.target.mkdir()
        _make_stub(self.fake_bin, "jq", "#!/bin/sh\nexit 0\n")

    def tearDown(self):
        self._tmp.cleanup()

    def test_node_too_old_flagged(self):
        _make_stub(self.fake_bin, "node", '#!/bin/sh\necho v18.20.0\n')
        _make_stub(self.fake_bin, "pnpm", '#!/bin/sh\necho 9.0.0\n')
        r = _run(self.target, fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 1)
        self.assertIn("RESULT: node=too-old", r.stdout)
        self.assertIn("required=22", r.stdout)
        self.assertIn("RESULT: ok=false", r.stdout)

    def test_node_22_11_is_below_the_supported_floor(self):
        _make_stub(self.fake_bin, "node", '#!/bin/sh\necho v22.11.0\n')
        _make_stub(self.fake_bin, "pnpm", '#!/bin/sh\necho 9.0.0\n')
        r = _run(self.target, fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 1)
        self.assertIn("RESULT: node=too-old version=22.11.0 required=22.12.0", r.stdout)
        self.assertIn("RESULT: ok=false", r.stdout)

    def test_node_22_12_passes(self):
        _make_stub(self.fake_bin, "node", '#!/bin/sh\necho v22.12.0\n')
        _make_stub(self.fake_bin, "pnpm", '#!/bin/sh\necho 9.0.0\n')
        r = _run(self.target, fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 0)
        self.assertIn("RESULT: node=yes version=22.12.0", r.stdout)
        self.assertIn("RESULT: pnpm=yes", r.stdout)
        self.assertIn("RESULT: jq=yes", r.stdout)
        self.assertIn("RESULT: ok=true", r.stdout)

    def test_supported_even_node_major_passes(self):
        _make_stub(self.fake_bin, "node", '#!/bin/sh\necho v24.0.0\n')
        _make_stub(self.fake_bin, "pnpm", '#!/bin/sh\necho 9.0.0\n')

        result = _run(self.target, fake_bin=self.fake_bin)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("RESULT: node=yes version=24.0.0", result.stdout)

    def test_odd_node_majors_are_unsupported(self):
        for version in ("23.11.1", "25.0.0"):
            with self.subTest(version=version):
                _make_stub(
                    self.fake_bin,
                    "node",
                    f'#!/bin/sh\necho v{version}\n',
                )
                _make_stub(self.fake_bin, "pnpm", '#!/bin/sh\necho 9.0.0\n')

                result = _run(self.target, fake_bin=self.fake_bin)

                self.assertEqual(result.returncode, 1)
                self.assertIn(
                    f"RESULT: node=unsupported version={version} reason=odd-major",
                    result.stdout,
                )
                self.assertIn("RESULT: ok=false", result.stdout)

    def test_pnpm_missing_flagged(self):
        # node present, pnpm absent → exit 1, ok=false, RESULT: pnpm=no.
        _make_stub(self.fake_bin, "node", '#!/bin/sh\necho v22.12.0\n')
        r = _run(self.target, fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 1)
        self.assertIn("RESULT: pnpm=no", r.stdout)
        self.assertIn("RESULT: ok=false", r.stdout)

    def test_node_missing_flagged(self):
        _make_stub(self.fake_bin, "pnpm", '#!/bin/sh\necho 9.0.0\n')
        r = _run(self.target, fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 1)
        self.assertIn("RESULT: node=no", r.stdout)
        self.assertIn("RESULT: ok=false", r.stdout)

    def test_node_pre_release_version_is_rejected(self):
        """A prerelease does not satisfy the stable >=22.12.0 contract."""
        _make_stub(self.fake_bin, "node", '#!/bin/sh\necho v22.12.0-rc.1\n')
        _make_stub(self.fake_bin, "pnpm", '#!/bin/sh\necho 9.0.0\n')
        r = _run(self.target, fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 1)
        self.assertIn("RESULT: node=unsupported", r.stdout)
        self.assertIn("reason=invalid-version", r.stdout)
        self.assertIn("RESULT: ok=false", r.stdout)

    def test_node_version_without_v_prefix_handled(self):
        """`22.12.0` — some installations emit version without leading `v`.
        The script should normalize and pass."""
        _make_stub(self.fake_bin, "node", '#!/bin/sh\necho 22.12.0\n')
        _make_stub(self.fake_bin, "pnpm", '#!/bin/sh\necho 9.0.0\n')
        r = _run(self.target, fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("RESULT: node=yes version=22.12.0", r.stdout)

    def test_node_empty_version_string_handled(self):
        """A `node --version` that prints nothing must not silently pass.
        Catches regressions where empty version was treated as ≥22."""
        _make_stub(self.fake_bin, "node", '#!/bin/sh\necho ""\n')
        _make_stub(self.fake_bin, "pnpm", '#!/bin/sh\necho 9.0.0\n')
        r = _run(self.target, fake_bin=self.fake_bin)
        # Must NOT be ok=true with an empty version string.
        self.assertNotIn("RESULT: ok=true", r.stdout,
                         "empty node version was accepted as ok=true")

    def test_jq_missing_is_reported_before_scaffolding(self):
        sealed = self.tmp / "sealed-bin"
        sealed.mkdir()
        _make_stub(sealed, "node", '#!/bin/sh\necho v22.12.0\n')
        _make_stub(sealed, "pnpm", '#!/bin/sh\necho 9.0.0\n')
        for tool in ("dirname", "sed", "find"):
            source = shutil.which(tool)
            if source is None:
                self.skipTest(f"{tool} is unavailable")
            (sealed / tool).symlink_to(source)

        result = _run(self.target, fake_bin=sealed, base_path="")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("RESULT: jq=no", result.stdout)
        self.assertIn("RESULT: ok=false", result.stdout)

    def test_invalid_project_name_fails_before_tool_checks(self):
        r = _run(self.target, fake_bin=self.fake_bin, project_name="has spaces")

        self.assertEqual(r.returncode, 1)
        self.assertIn("RESULT: error=invalid-project-name", r.stdout)
        self.assertNotIn("RESULT: pnpm=", r.stdout)
        self.assertNotIn("RESULT: node=", r.stdout)

    def test_invalid_cloudflare_slug_fails_before_tool_checks(self):
        r = _run(self.target, fake_bin=self.fake_bin, project_name="a" * 64)

        self.assertEqual(r.returncode, 1)
        self.assertIn("RESULT: error=invalid-cloudflare-service-name", r.stdout)
        self.assertNotIn("RESULT: pnpm=", r.stdout)
        self.assertNotIn("RESULT: node=", r.stdout)

    def test_reserved_npm_names_fail_before_tool_checks(self):
        for project_name in ("node_modules", "favicon.ico", "@scope/node_modules"):
            with self.subTest(project_name=project_name):
                r = _run(
                    self.target,
                    fake_bin=self.fake_bin,
                    project_name=project_name,
                )
                self.assertEqual(r.returncode, 1)
                self.assertIn("RESULT: error=invalid-project-name", r.stdout)
                self.assertNotIn("RESULT: pnpm=", r.stdout)
                self.assertNotIn("RESULT: node=", r.stdout)


class TestPreflightTargetDirState(unittest.TestCase):
    """Missing and clean targets are allowed; existing projects fail closed."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.fake_bin = self.tmp / "bin"
        self.fake_bin.mkdir()
        # Always stub a passing env so we isolate target-state behaviour.
        _make_stub(self.fake_bin, "node", '#!/bin/sh\necho v22.12.0\n')
        _make_stub(self.fake_bin, "pnpm", '#!/bin/sh\necho 9.0.0\n')
        _make_stub(self.fake_bin, "jq", "#!/bin/sh\nexit 0\n")

    def tearDown(self):
        self._tmp.cleanup()

    def test_target_missing_reported(self):
        missing = self.tmp / "does-not-exist"
        r = _run(missing, fake_bin=self.fake_bin)
        self.assertIn("RESULT: target=missing", r.stdout)
        # The framework CLI may create this target after preflight.
        self.assertEqual(r.returncode, 0)

    def test_target_clean_reported(self):
        clean = self.tmp / "clean"
        clean.mkdir()
        r = _run(clean, fake_bin=self.fake_bin)
        self.assertIn("RESULT: target=clean", r.stdout)
        self.assertIn("files=0", r.stdout)
        self.assertEqual(r.returncode, 0)

    def test_target_under_parent_path_with_spaces_is_one_clean_argument(self):
        clean = self.tmp / "customer portals" / "customer-portal"
        clean.parent.mkdir()
        clean.mkdir()

        r = _run(clean, fake_bin=self.fake_bin)

        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"RESULT: target=clean path={clean}", r.stdout)
        self.assertIn("RESULT: ok=true", r.stdout)

    def test_invalid_target_basename_fails_before_tool_checks(self):
        invalid = self.tmp / "customer portal"
        invalid.mkdir()

        r = _run(invalid, fake_bin=self.tmp / "missing-bin")

        self.assertEqual(r.returncode, 1)
        self.assertIn("RESULT: error=invalid-target-name", r.stdout)
        self.assertNotIn("RESULT: pnpm=", r.stdout)
        self.assertNotIn("RESULT: node=", r.stdout)
        self.assertNotIn("RESULT: target=", r.stdout)

    def test_target_occupied_via_package_json(self):
        occupied = self.tmp / "occupied"
        occupied.mkdir()
        (occupied / "package.json").write_text("{}")
        r = _run(occupied, fake_bin=self.fake_bin)
        self.assertIn("RESULT: target=occupied", r.stdout)
        self.assertEqual(r.returncode, 1)
        self.assertIn("RESULT: ok=false", r.stdout)

    def test_target_occupied_via_next_config(self):
        occupied = self.tmp / "next-occupied"
        occupied.mkdir()
        (occupied / "next.config.ts").write_text("export default {};")
        r = _run(occupied, fake_bin=self.fake_bin)
        self.assertIn("RESULT: target=occupied", r.stdout)
        self.assertEqual(r.returncode, 1)

    def test_target_occupied_via_subdirectory(self):
        occupied = self.tmp / "directory-occupied"
        (occupied / "src").mkdir(parents=True)
        r = _run(occupied, fake_bin=self.fake_bin)

        self.assertIn("RESULT: target=occupied", r.stdout)
        self.assertEqual(r.returncode, 1)

    def test_target_occupied_via_hidden_file(self):
        occupied = self.tmp / "hidden-occupied"
        occupied.mkdir()
        (occupied / ".envrc").write_text("use node\n")
        r = _run(occupied, fake_bin=self.fake_bin)

        self.assertIn("RESULT: target=occupied", r.stdout)
        self.assertEqual(r.returncode, 1)

    def test_regular_file_target_is_occupied(self):
        occupied = self.tmp / "file-target"
        occupied.write_text("not a directory\n")
        r = _run(occupied, fake_bin=self.fake_bin)

        self.assertIn("RESULT: target=occupied", r.stdout)
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
