"""Execute the archive operation documented by the revision workflow."""

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
            for name in ("v1.md", "v3.md", "v99-notes.md"):
                (versions / name).write_bytes(name.encode())
            before = {p.name: p.read_bytes() for p in versions.iterdir()}
            result = subprocess.run([sys.executable, "-", str(root)], input=archive_code(),
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(Path(result.stdout.strip()), versions / "v4.md")
            self.assertEqual((versions / "v4.md").read_bytes(), current.read_bytes())
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


if __name__ == "__main__":
    unittest.main()
