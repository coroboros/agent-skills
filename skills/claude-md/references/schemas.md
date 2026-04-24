# claude-md — JSON Schemas

Contracts for the deterministic scripts under `scripts/`. Both scripts emit a JSON report on stdout and exit 0 on clean / 1 on findings / 2 on argument or I/O error.

## audit_claude_md report

Emitted by `scripts/audit_claude_md.py <path>`.

```json
{
  "lines": 317,
  "target_lines": 200,
  "over_target": true,
  "bloat": [
    {"line": 42, "category": "linter-enforced", "match": "run pnpm lint before commit"}
  ],
  "broken_imports": [
    {"line": 12, "path": "docs/missing.md"}
  ],
  "summary": {"ok": false, "findings": 3}
}
```

| Field | Type | Description |
|-------|------|-------------|
| `lines` | integer | Total lines in the file. |
| `target_lines` | integer | Canonical target (currently 200). |
| `over_target` | boolean | `lines > target_lines`. |
| `bloat[].line` | integer | 1-indexed line number of the hit. |
| `bloat[].category` | string | One of `linter-enforced`, `marketing-or-vision`, `obvious-info`, `verbose-explanation`, `redundant-spec`, `generic-best-practice`. |
| `bloat[].match` | string | The matching substring (trimmed). |
| `broken_imports[].line` | integer | Line of the `@path` import. |
| `broken_imports[].path` | string | The unresolved path (relative or `~`-expanded). |
| `summary.ok` | boolean | `len(bloat) + len(broken_imports) == 0 && !over_target`. |
| `summary.findings` | integer | Total count across all categories. |

## validate_rule_file report

Emitted by `scripts/validate_rule_file.py <path>`.

```json
{
  "has_frontmatter": true,
  "has_paths": true,
  "paths": ["src/api/**/*.ts", "src/server/**/*.ts"],
  "errors": [],
  "summary": {"ok": true}
}
```

| Field | Type | Description |
|-------|------|-------------|
| `has_frontmatter` | boolean | File starts with a `---` frontmatter block. |
| `has_paths` | boolean | Frontmatter contains a `paths:` key. |
| `paths` | string[] | Extracted glob strings (empty when `has_paths` is false). |
| `errors` | string[] | One message per validation failure (unclosed frontmatter, malformed list, suspicious glob characters). |
| `summary.ok` | boolean | `errors` is empty. |

## init_structure result

Emitted by `scripts/init_structure.sh <mode>` where `<mode>` is `single`, `hybrid`, or `rules-only`. Non-JSON — uses `RESULT: key=value` lines on stdout for compatibility with the skill's report parser.

```
RESULT: mode=hybrid
RESULT: created=CLAUDE.md,.claude/rules/tech.md,.claude/rules/writing.md
RESULT: skipped=
RESULT: ok=true
```

| Key | Type | Description |
|-----|------|-------------|
| `mode` | string | Storage strategy that was initialised. |
| `created` | comma-list | Paths created. Empty when the scaffold was a no-op. |
| `skipped` | comma-list | Paths that already existed (the script never overwrites). |
| `ok` | `true` / `false` | Overall status. `false` on unknown mode or permission error. |
