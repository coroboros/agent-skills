"""Guard: every test package under tests/ is reachable by `unittest discover`.

`unittest discover tests/` — the command CI runs — only recurses into directories
that are importable packages, i.e. that contain an `__init__.py`. A skill test
directory holding `test_*.py` files but no `__init__.py` is silently skipped: its
tests never run in CI even though they pass when the module is run directly. This
guard fails loudly so the gap surfaces in review, not in a missed regression.
"""
import unittest
from pathlib import Path

TESTS_ROOT = Path(__file__).resolve().parent.parent


class TestDiscoveryIntegrity(unittest.TestCase):
    def test_every_test_package_has_init(self):
        offenders = []
        for d in sorted(TESTS_ROOT.iterdir()):
            if not d.is_dir() or d.name == "__pycache__":
                continue
            # Only dirs that actually hold test modules matter — an empty or
            # cruft-only dir contributes nothing to discover and needs no marker.
            if any(d.glob("test_*.py")) and not (d / "__init__.py").exists():
                offenders.append(d.name)
        self.assertEqual(
            offenders, [],
            f"test dirs with test_*.py but no __init__.py (discover/CI skips them): {offenders}",
        )


if __name__ == "__main__":
    unittest.main()
