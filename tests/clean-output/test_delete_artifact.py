"""Tests for skills/clean-output/scripts/delete_artifact.py.

Exercise the path-resolution guard, file/dir deletion, symlink handling, and
the exit-code contract (0 deleted / 1 missing-or-unwritable / 2 guard-violation).
Fixtures use `tempfile.TemporaryDirectory` so the suite never touches the
real ~/.claude/output/.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "clean-output" / "scripts" / "delete_artifact.py"


def _run(path: Path, root: Path) -> tuple[int, str, str]:
    r = subprocess.run(
        [sys.executable, str(SCRIPT), str(path), "--root", str(root)],
        capture_output=True,
        text=True,
    )
    return r.returncode, r.stdout, r.stderr


class TestSuccessfulDeletion(unittest.TestCase):
    def test_deletes_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "my-app" / "forge" / "forge-x.md"
            target.parent.mkdir(parents=True)
            target.write_text("content")
            code, _, err = _run(target, root)
            self.assertEqual(code, 0, err)
            self.assertFalse(target.exists())

    def test_deletes_directory_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "my-app" / "apex" / "01-feature"
            target.mkdir(parents=True)
            (target / "00-context.md").write_text("ctx")
            (target / "01-analyze.md").write_text("analyze")
            code, _, err = _run(target, root)
            self.assertEqual(code, 0, err)
            self.assertFalse(target.exists())


class TestPathGuard(unittest.TestCase):
    """The script refuses any path that resolves outside --root."""

    def test_refuses_absolute_outside_root(self):
        """The canonical AC test — passing /etc/hosts must exit 2 and not touch it."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = Path("/etc/hosts")
            self.assertTrue(target.exists(), "test premise: /etc/hosts must exist")
            code, _, err = _run(target, root)
            self.assertEqual(code, 2, err)
            self.assertIn("outside", err)
            self.assertTrue(target.exists(), "/etc/hosts must remain untouched")

    def test_refuses_dotdot_traversal(self):
        """A path constructed to traverse out via `..` must still resolve outside."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "claude" / "output"
            root.mkdir(parents=True)
            attacker = root / ".." / ".." / "outside.md"
            attacker.resolve().write_text("oops")
            code, _, err = _run(attacker, root)
            self.assertEqual(code, 2, err)
            self.assertTrue(attacker.resolve().exists(),
                            "the file outside root must remain untouched")

    def test_refuses_nonexistent_outside(self):
        """A nonexistent path outside root still fails the guard before existence check.

        Guard-first ordering means the script never reports `missing` for paths
        that would have been refused anyway. Strictest contract first.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = Path("/etc/definitely-does-not-exist-xyz")
            code, _, err = _run(target, root)
            self.assertEqual(code, 2, err)
            self.assertIn("outside", err)


class TestMissingPath(unittest.TestCase):
    def test_missing_inside_root_returns_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "my-app" / "forge" / "ghost.md"
            code, _, err = _run(target, root)
            self.assertEqual(code, 1, err)
            self.assertIn("missing", err)


class TestSymlinkHandling(unittest.TestCase):
    """Symlinks unlink the link, never follow into the target — even when the target
    is inside the root. The path-guard short-circuits any symlink whose resolved
    target escapes the sandbox."""

    def test_symlink_pointing_outside_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "my-app" / "forge").mkdir(parents=True)
            link = root / "my-app" / "forge" / "evil-link"
            try:
                link.symlink_to("/etc/hosts")
            except OSError:
                self.skipTest("filesystem does not support symlinks")
            code, _, err = _run(link, root)
            self.assertEqual(code, 2, err)
            self.assertTrue(link.is_symlink(), "symlink must remain")
            self.assertTrue(Path("/etc/hosts").exists())

    def test_symlink_pointing_inside_unlinks_only_the_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "my-app" / "forge").mkdir(parents=True)
            real = root / "my-app" / "forge" / "real.md"
            real.write_text("real content")
            link = root / "my-app" / "forge" / "alias.md"
            try:
                link.symlink_to(real)
            except OSError:
                self.skipTest("filesystem does not support symlinks")
            code, _, err = _run(link, root)
            self.assertEqual(code, 0, err)
            self.assertFalse(link.is_symlink(), "link must be gone")
            self.assertTrue(real.exists(), "the real file must survive")


class TestRootResolution(unittest.TestCase):
    def test_root_can_have_trailing_slash_and_dotdot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root_canonical = Path(tmp) / "output"
            root_canonical.mkdir()
            target = root_canonical / "forge.md"
            target.write_text("x")
            messy_root = Path(tmp) / "junk" / ".." / "output"
            code, _, err = _run(target, messy_root)
            self.assertEqual(code, 0, err)


if __name__ == "__main__":
    unittest.main()
