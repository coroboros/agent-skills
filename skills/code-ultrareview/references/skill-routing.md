# Skill routing — lens-cluster → installed-skill chain

The action plan emitted in every report routes each finding cluster (per-lens, per-marker) to a delegation skill. This document defines the canonical routing table and the fallback contract.

## Contract

- Routing is keyed by **(lens, severity marker)**. Six canonical lenses × three markers (🔴 / 🟠 / 🟢) = 18 cells.
- Each cell is an **ordered list of candidates** `(skill_name, command)`. The first candidate whose skill is installed wins.
- `/apex` is the **mandatory final candidate** in every cell. An import-time assertion in `scripts/detect_skills.py::_validate_routing_table()` enforces this.
- When no candidate is installed (anomalous — `/apex` should always be available alongside `code-ultrareview`), the routing still emits `/apex` with `fallback_used: True`. The report stays actionable; the user repairs their install separately.
- `fallback_used` is `True` whenever at least one earlier candidate was not installed.

## Table

| Lens | 🔴 (High) | 🟠 (Medium) | 🟢 (Low) |
|------|-----------|-------------|----------|
| rules | `/apex` | `/apex` | `/oneshot` → `/apex` |
| bugs-drift | `/apex` | `/apex` | `/oneshot` → `/apex` |
| docs-version | `/apex` | `/humanize-en` → `/apex` | `/fix-grammar` → `/oneshot` → `/apex` |
| tests-blindspots | `/apex` | `/apex` | `/oneshot` → `/apex` |
| coherence-graph | `/apex` | `/apex` | `/oneshot` → `/apex` |
| derivation | `/apex` | `/apex` | `/oneshot` → `/apex` |

Authoritative source: `scripts/detect_skills.py::ROUTING_TABLE`. Tests in `tests/code-ultrareview/test_detect_skills.py::TestRoutingTableShape` pin shape parity.

## Why these choices

- **🔴 High everywhere → `/apex`** — high-severity findings need analysis + multi-file changes. `/apex`'s plan-execute-examine fits.
- **`docs-version` 🟠 → `/humanize-en`** — prose tone drift is the specialized lane; falls to `/apex` otherwise.
- **`docs-version` 🟢 → `/fix-grammar` → `/oneshot`** — grammar nits are the most specialized lane; `/oneshot` is a generic quick-fix below `/apex`.
- **🟢 across other lenses → `/oneshot`** — low-severity findings are quick polish work, well-suited to a single-pass fix skill.

## Detection

`detect_skills.detect_installed_skills(home, project_root)` scans:

1. `<home>/.claude/skills/*/SKILL.md` (global)
2. `<project_root>/.claude/skills/*/SKILL.md` (project) — when `project_root` is set

Project skills shadow global on name collision. Hidden directories (`.foo`) and dirs without `SKILL.md` are skipped.

## CLI

```bash
python3 skills/code-ultrareview/scripts/detect_skills.py --json
```

Prints `{skill_name: skill_md_path}` JSON. Useful for debugging an unexpected `fallback_used` in a report.

## Adding a candidate

To insert a new specialized skill ahead of `/apex` in some cell:

1. Edit `ROUTING_TABLE` in `scripts/detect_skills.py`.
2. Keep `("apex", "/apex")` last in the cell — the validator will fail import otherwise.
3. Update this table.
4. Add a test in `tests/code-ultrareview/test_detect_skills.py` confirming the new candidate is honoured when installed and skipped when absent.

A new lens follows the same workflow plus a parity update in `aggregation.CANONICAL_LENSES`.
