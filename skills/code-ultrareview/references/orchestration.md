# Orchestration

Main-thread orchestration details for Phase 3 (axis review) and Phase 4 (validation). Subagents cannot spawn other subagents; the main thread launches both axis reviewers and Haiku validators.

## Phase 3 — axis review

The orchestrator prepares per-axis bundles via `scripts/axis_dispatch.py prepare`, then launches every bundle as a parallel `Explore` subagent in one message. `$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing the skill's SKILL.md elsewhere.

```bash
python3 "$SKILL_DIR"/scripts/axis_dispatch.py prepare \
  --scope <scope.json> \
  --findings <tool-findings.jsonl> \
  --diff <diff.patch> \
  --output-dir <run-dir>
```

Output: a JSON map `{axis: {input_path, prompt_path, findings_count}}`. The orchestrator reads each axis's `prompt_path`, then fans out one `Task` call per axis in the same message.

Each subagent receives via its bundle (`axis-input/{axis}.json`):

- `scope` — repo kind, languages, CLAUDE.md chain, files touched.
- `findings` — tool findings filtered to its own axis only (`scripts/battery_ingest.py` axis routing). Other axes' findings are excluded so the subagent's context stays lean.
- `diff_text` — the diff itself.
- `brief_path` — its axis brief at `references/axes/{axis}.md`.
- `anthropic_verbatim_path` — `references/anthropic-verbatim.md` carrying the 0-100 rubric, HIGH SIGNAL criteria, false-positive taxonomy, and agent-assumption rule.

Each subagent emits findings as JSONL on stdout, one finding per line, against the canonical schema (`axis`, `severity`, `location`, `finding`, `recommendation`, `confidence`).

**Coverage, not filtering.** Axis reviewers maximize coverage at the finding stage — they report low-severity and uncertain findings with an honest confidence rather than self-filtering on importance. Phase 4 validators plus the 80-confidence threshold do the ranking; the A2 contract surfaces sub-80 findings in `### ⚠️ Unverified`. The split is deliberate: a finder told to be conservative suppresses real bugs, so confidence filtering lives downstream of finding, never inside it.

**Conditional Coherence.** `axis_dispatch prepare` adds Coherence to the bundle list when `scope.json["activates_coherence"]` is true (still within the 10-parallel concurrency cap). When inactive, the report header surfaces `Coherence axis: inactive`.

**No silent failure.** If any axis subagent returns no output (timeout, error, malformed JSON), the orchestrator emits a 🔴 High finding for that axis citing the failure mode — never a silent skip.

## Phase 4 — validation

The orchestrator prepares per-finding validator bundles via `scripts/run_validators.py prepare`, then launches one Haiku `Task` per finding in the same message — batched ≤10 parallel.

```bash
python3 "$SKILL_DIR"/scripts/run_validators.py prepare \
  --scope <scope.json> \
  --findings <axis-findings.jsonl> \
  --diff <diff.patch> \
  --output-dir <run-dir>
```

Output: `{count, batches: [[idx, ...], ...], bundles: {idx: {input_path, prompt_path}}}`. The orchestrator reads each batch's `prompt_path`, fans out one `Task` per index in one message, collects stdout as `{index, score, reason}` lines, then runs `scripts/run_validators.py ingest` to apply A2-preserving promote / demote logic on top of `scripts/synthesis_core.py` primitives.

Each validator:

1. Re-scores 0-100 against the verbatim rubric.
2. Re-checks that the cited CLAUDE.md rule actually exists in `claude_md_chain`. Demotes with explicit reason if not found (`CLAUDE.md rule not found at <path>`).
3. Stays read-only — no Write / Edit / Bash, no nested subagent spawn.

**Confidence threshold = 80** (`scripts/synthesis_core.py:CONFIDENCE_THRESHOLD`). Tool-battery findings (confidence 100) skip the validator phase — they are deterministic.

**Typical runtime.** 5-15 sub-80 findings → one batch → ~30-60s total. Latency is dominated by Haiku launch overhead, not validator inference; 25+ findings spread over 2-3 batches stay under ~2 min.

**A2 contract.** No sub-80 finding silently dropped. Each one is promoted to ≥80, demoted with reason, or surfaced in `### ⚠️ Unverified` with the validator's reason text.

## Phase 3.5 — `--verify-build` (opt-in)

Build verification runs BEFORE validators via `scripts/run_build_verify.py`, composing `scripts/build_detect.py` (canonical test command per repo type) with `scripts/synthesis_core.py:iterate_unverified` (+30 confidence, cap 95, floor 80). The test command runs once with a 120 s default timeout; for each sub-80 finding on `correctness` / `tests` / `design-api` / `performance`, a non-zero exit promotes the finding past the validator phase. Other axes pass through unchanged.
