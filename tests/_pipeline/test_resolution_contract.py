"""Pins the deterministic `-f` resolution contract across its THREE homes.

The resolution rule (the brainstorm/spec/apex synergy keystone) is prose in
three files that can silently drift apart (code-review finding #3):

- `.claude/rules/repo-conventions.md`  — the SSOT rule
- `skills/spec/steps/step-01-discover.md` — spec's consumer-side application
- `skills/apex/steps/step-01-analyze.md`  — apex's consumer-side application

`_contracts.py`'s `test_ssot_documents_deterministic_resolution` only checks
the rule doc. This pins all three to the same invariants so a future edit to
one cannot diverge the keystone unnoticed. Phrasing differs per file by
design — only the invariants must hold everywhere.
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
SOURCES = {
    "rule": REPO / ".claude" / "rules" / "repo-conventions.md",
    "spec-step": REPO / "skills" / "spec" / "steps" / "step-01-discover.md",
    "apex-step": REPO / "skills" / "apex" / "steps" / "step-01-analyze.md",
}

# (label, compiled test) — every invariant must hold in every source.
INVARIANTS = [
    ("bare→global path",
     lambda s: "~/.claude/output/" in s),
    ("producer+project mapping",
     lambda s: "{producer}" in s and "{project}" in s),
    ("explicit-path passthrough",
     lambda s: re.search(r"explicit path", s, re.I) is not None),
    ("fail loud on absent",
     lambda s: "fail loud" in s),
    ("never glob / no inference",
     lambda s: re.search(r"never .*glob|never fall back to a glob", s, re.I)
     is not None),
    # code-review F4: the failure path must offer the explicit absolute path.
    ("absolute-path fallback on failure",
     lambda s: re.search(r"explicit absolute path", s, re.I) is not None),
]


class TestResolutionContractConsistency(unittest.TestCase):
    def test_every_source_states_every_invariant(self):
        texts = {k: p.read_text(encoding="utf-8") for k, p in SOURCES.items()}
        for src, text in texts.items():
            for label, holds in INVARIANTS:
                with self.subTest(source=src, invariant=label):
                    self.assertTrue(
                        holds(text),
                        f"{SOURCES[src].relative_to(REPO)} no longer states "
                        f"the '{label}' invariant — the -f resolution keystone "
                        f"has drifted across its three homes.",
                    )

    def test_sources_exist(self):
        for k, p in SOURCES.items():
            self.assertTrue(p.is_file(), f"{k} source missing: {p}")


if __name__ == "__main__":
    unittest.main()
