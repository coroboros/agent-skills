"""Execute the documented archive and isolated draft operations."""

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


STEP = Path(__file__).resolve().parents[2] / "skills/suno-produce/steps/revise.md"


def archive_code():
    match = re.search(r"python3 - .*? <<'PY'\n(.*?)\nPY", STEP.read_text(), re.DOTALL)
    if match is None:
        raise AssertionError("revision archive operation missing")
    return match.group(1)


class TestRevisionArchive(unittest.TestCase):
    def test_gaps_and_unrelated_names_preserve_every_prior_take(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            current = root / "TRACK.md"
            current.write_bytes(b"CURRENT\r\n")
            versions = root / "versions"
            versions.mkdir()
            for name in ("v1.md", "v4.md", "v99-notes.md"):
                (versions / name).write_bytes(name.encode())
            before = {p.name: p.read_bytes() for p in versions.iterdir()}
            result = subprocess.run([sys.executable, "-", str(root)], input=archive_code(),
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(Path(result.stdout.strip()), versions / "v5.md")
            self.assertEqual((versions / "v5.md").read_bytes(), current.read_bytes())
            for name, content in before.items():
                self.assertEqual((versions / name).read_bytes(), content)
            self.assertEqual(current.read_bytes(), b"CURRENT\r\n")

    def test_first_revision_is_v1(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "TRACK.md").write_text("INITIAL")
            result = subprocess.run([sys.executable, "-", str(root)], input=archive_code(),
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((root / "versions/v1.md").read_text(), "INITIAL")

    def test_destination_created_after_selection_is_never_overwritten(self):
        # Model a competing writer between the listing and exclusive open.
        collision = """from pathlib import Path
original_open = Path.open
def competing_open(path, mode='r', *args, **kwargs):
    if mode == 'xb':
        path.write_bytes(b'OTHER TAKE')
    return original_open(path, mode, *args, **kwargs)
Path.open = competing_open
"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "TRACK.md").write_text("CURRENT")
            result = subprocess.run([sys.executable, "-", str(root)],
                                    input=collision + archive_code(), text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FileExistsError", result.stderr)
            self.assertEqual((root / "versions/v1.md").read_text(), "OTHER TAKE")
            self.assertEqual((root / "TRACK.md").read_text(), "CURRENT")


class TestDraftIsolation(unittest.TestCase):
    def test_parallel_projects_do_not_share_candidate_bytes(self):
        for mode in ("create", "revise"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                step = STEP.with_name(f"{mode}.md").read_text()
                allocation = re.search(r"```bash\n(python3 -c [^\n]+)\n```", step)
                self.assertIsNotNone(allocation, "unique draft allocation missing")
                candidates = []
                for _ in range(2):
                    result = subprocess.run(["bash", "-c", allocation.group(1)],
                                            env={**os.environ, "TMPDIR": directory},
                                            text=True, capture_output=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    candidates.append(Path(result.stdout.strip()) / "TRACK.md")
                self.assertNotEqual(candidates[0], candidates[1])
                candidates[0].write_bytes(b"VALIDATED A")
                candidates[1].write_bytes(b"UNVALIDATED B")
                installed = Path(directory) / "TRACK.md"
                candidates[0].replace(installed)
                self.assertEqual(installed.read_bytes(), b"VALIDATED A")
                self.assertEqual(candidates[1].read_bytes(), b"UNVALIDATED B")


if __name__ == "__main__":
    unittest.main()
