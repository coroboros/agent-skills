"""Pins the v2 `-f` contract across its THREE homes.

The keystone is no longer bare-name reconstruction — it is the opposite:
**explicit path, used verbatim, no magic**. It is stated as prose in three
files that can silently drift apart:

- `.claude/rules/repo-conventions.md`  — the SSOT rule (§ Pipeline chaining)
- `skills/spec/steps/step-01-discover.md` — spec's consumer-side application
- `skills/apex/steps/step-01-analyze.md`  — apex's consumer-side application

This pins all three to the same invariants so a future edit to one cannot
re-introduce reconstruction/inference/glob unnoticed. Phrasing differs per
file by design — only the invariants must hold everywhere.
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

# (label, predicate) — every invariant must hold in every source.
INVARIANTS = [
    ("explicit path",
     lambda s: "explicit path" in s),
    ("used/read verbatim",
     lambda s: "verbatim" in s),
    ("no reconstruction / inference / glob",
     lambda s: re.search(r"(no|nothing to|never)[^.\n]*reconstruct", s, re.I)
     is not None),
    ("fail loud when absent",
     lambda s: "fail loud" in s),
]


class TestExplicitPathContractConsistency(unittest.TestCase):
    def test_every_source_states_every_invariant(self):
        texts = {k: p.read_text(encoding="utf-8") for k, p in SOURCES.items()}
        for src, text in texts.items():
            for label, holds in INVARIANTS:
                with self.subTest(source=src, invariant=label):
                    self.assertTrue(
                        holds(text),
                        f"{SOURCES[src].relative_to(REPO)} no longer states "
                        f"the '{label}' invariant — the explicit-path `-f` "
                        f"contract has drifted (magic creeping back in?).",
                    )

    def test_no_source_reintroduces_bare_name_resolution(self):
        # The deleted mechanism must not return: a producer/skill mapping a
        # *bare* filename to a path is exactly the magic v2 removes.
        for k, p in SOURCES.items():
            with self.subTest(source=k):
                t = p.read_text(encoding="utf-8")
                self.assertNotRegex(
                    t, r"bare filename.*→.*~/\.claude/output",
                    f"{p.relative_to(REPO)} reintroduces bare-name resolution",
                )

    def test_sources_exist(self):
        for k, p in SOURCES.items():
            self.assertTrue(p.is_file(), f"{k} source missing: {p}")


if __name__ == "__main__":
    unittest.main()
