# Orchestration

Main-thread orchestration details for Phase 3 (axis review) and Phase 4 (validation). Subagents cannot spawn other subagents; the main thread launches both axis reviewers and Haiku validators.

## Phase 3 — axis review

The orchestrator prepares per-axis bundles via `scripts/axis_dispatch.py prepare`, then launches every bundle as a parallel `Explore` subagent in one message. `$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing the skill's SKILL.md elsewhere.

### Produce the diff

`prepare --diff` takes a patch file no phase emits on its own — the orchestrator produces it, matching the Phase 1 scope resolution (`scope.json["base"]`, `["target"]`, `["dirty_tree"]`):

- **Clean tree** (`dirty_tree` false) — diff the base + target from `scope.json` (resolved by `scripts/resolve_base.sh`; the base is already a merge-base, so the two-dot form is correct — no three-dot):

  ```bash
  git diff <base> <target> > /tmp/cur-diff.patch
  ```

- **Dirty tree** (`dirty_tree` true) — tracked changes plus every untracked file appended as added lines, so uncommitted-new content reviews too:

  ```bash
  git diff HEAD > /tmp/cur-diff.patch   # outside the repo — a patch in the cwd is itself untracked and would self-include below
  git ls-files --others --exclude-standard -z \
    | while IFS= read -r -d '' f; do
        git diff --no-index /dev/null "$f" >> /tmp/cur-diff.patch || true
      done
  ```

  `git diff --no-index` exits 1 whenever the files differ — always here — so the `|| true` keeps `set -e` shells running.

Phase 1 also records target-side added/modified hunks in `scope.json["changed_line_ranges"]`. Phase 2 uses that map to exclude pre-existing line-level analyzer findings from confidence-100 coverage; manifest/API analyzers remain path-scoped because their reported line is not authoritative.

### Prepare the bundles

```bash
python3 "$SKILL_DIR"/scripts/axis_dispatch.py prepare \
  --scope <scope.json> \
  --findings <tool-findings.jsonl> \
  --diff <diff.patch> \
  --output-dir <run-dir>
```

Output: `{axes, coherence_active, bundles, run_id, input_hashes}` where each bundle contains its input path, prompt path, finding count, and the same `run_id`. The orchestrator reads each axis's `prompt_path`, then fans out one `Task` call per axis in the same message.

Each subagent receives via its bundle (`axis-input/{axis}.json`):

- `scope` — repo kind, languages, CLAUDE.md chain, files touched.
- `findings` — tool findings filtered to its own axis only (`scripts/battery_ingest.py` axis routing). Other axes' findings are excluded so the subagent's context stays lean.
- `diff_text` — the diff itself.
- `brief_path` — its axis brief at `references/axes/{axis}.md`.
- `anthropic_verbatim_path` — `references/anthropic-verbatim.md` carrying the 0-100 rubric, HIGH SIGNAL criteria, false-positive taxonomy, and agent-assumption rule.
- `reconcile` — present only for the Intent axis when `--reconcile` completed; the hash-verified derivation payload with `UNCLASSIFIED` claims for that reviewer to classify.

Each subagent emits findings as JSONL on stdout, one finding per line, against the canonical schema (`run_id`, `axis`, `severity`, `location`, `finding`, `recommendation`, `confidence`). An axis with no findings emits `{"run_id":"<prepared-run-id>","axis":"<axis>","no_findings":true}`. Ingest rejects missing or stale run IDs.

**Coverage, not filtering.** Axis reviewers maximize coverage at the finding stage — they report low-severity and uncertain findings with an honest confidence rather than self-filtering on importance. Phase 4 validators plus the 80-confidence threshold do the ranking; the A2 contract surfaces sub-80 findings in `### ⚠️ Unverified`. The split is deliberate: a finder told to be conservative suppresses real bugs, so confidence filtering lives downstream of finding, never inside it.

**Conditional Coherence.** `axis_dispatch prepare` adds Coherence to the bundle list when `scope.json["activates_coherence"]` is true (still within the 10-parallel concurrency cap). When inactive, the report header surfaces `Coherence axis: inactive`.

**Selected-axis integrity.** `axis_dispatch ingest` cross-checks the requested axes recorded during `prepare` against any explicit ingest selection. A mismatch exits 2 before merging output, so an omitted or substituted axis cannot produce a scoped verdict.

Collect the subagent outputs as `<axis-results-dir>/<axis>.jsonl`, then ingest exactly the prepared set:

```bash
python3 "$SKILL_DIR"/scripts/axis_dispatch.py ingest \
  --scope <scope.json> \
  --results-dir <axis-results-dir> \
  --output <axis-findings.jsonl> \
  [--axes <same-comma-separated-subset-used-by-prepare>]
```

**No silent failure.** Before creating bundles, `axis_dispatch prepare` independently verifies complete deterministic-tool and requested mutation/reconcile coverage. Prepare and ingest first invalidate any previous axis/validator success. Ingest removes the previous merged output, validates one complete result per requested axis, then publishes the new JSONL atomically. If any selected axis subagent returns no output, times out, errors, or emits malformed JSON, `axis_dispatch ingest` exits 4. Validation and synthesis must not run with incomplete coverage.

## Phase 4 — validation

The orchestrator prepares per-finding validator bundles via `scripts/run_validators.py prepare`, then launches one Haiku `Task` per finding in the same message — batched ≤10 parallel.

```bash
python3 "$SKILL_DIR"/scripts/run_validators.py prepare \
  --scope <scope.json> \
  --findings <axis-findings.jsonl> \
  --diff <diff.patch> \
  --output-dir <run-dir>
```

Output: `{count, batches: [[idx, ...], ...], bundles, run_id, input_hashes}`. The orchestrator reads each batch's `prompt_path`, fans out one `Task` per index in one message, collects stdout as `{run_id, index, score, reason}` lines, then runs `scripts/run_validators.py ingest` to apply A2-preserving promote / demote logic on top of `scripts/synthesis_core.py` primitives. Every result must repeat the exact prepared `run_id`.

```bash
python3 "$SKILL_DIR"/scripts/run_validators.py ingest \
  --scope <scope.json> \
  --findings <axis-findings.jsonl> \
  --results <validator-results.jsonl> \
  --output <validated-findings.jsonl>
```

Prepare refuses incomplete axis coverage. Both commands invalidate any prior validator success; ingest also removes the previous validated output, requires exactly one valid `{run_id, index, score, reason}` result for every prepared sub-80 finding, verifies that the diff and axis-findings SHA-256 identities still match preparation, and publishes only after the complete set validates.

Each validator:

1. Re-scores 0-100 against the verbatim rubric.
2. Re-checks that the cited CLAUDE.md rule actually exists in `claude_md_chain`. Demotes with explicit reason if not found (`CLAUDE.md rule not found at <path>`).
3. Stays read-only — no Write / Edit / Bash, no nested subagent spawn.

**Confidence threshold = 80** (`scripts/synthesis_core.py:CONFIDENCE_THRESHOLD`). Tool-battery findings (confidence 100) skip the validator phase — they are deterministic.

Confidence `0` is a valid uncertain finding, not an omission sentinel. It receives a validator bundle and either gets promoted or remains explicit under `### ⚠️ Unverified`.

**Typical runtime.** 5-15 sub-80 findings → one batch → ~30-60s total. Latency is dominated by Haiku launch overhead, not validator inference; 25+ findings spread over 2-3 batches stay under ~2 min.

**A2 contract.** No sub-80 finding silently dropped. Each one is promoted to ≥80, demoted with reason, or surfaced in `### ⚠️ Unverified` with the validator's reason text.

## Phase 3.5 — `--verify-build` (opt-in)

Build verification runs BEFORE validators via `scripts/run_build_verify.py` and `scripts/build_detect.py` whenever `--verify-build` is requested. It first records incomplete `build_coverage` and removes prior build output/metadata. The canonical command runs once with a 120 s default timeout even when every finding is already at or above 80. JavaScript detection requires an actual `scripts.test` entry. Python detection requires declared pytest configuration/dependencies or a collectable unittest suite; a manifest alone never invents a command. A pass with collected tests completes the gate; a missing command or runner exits 3 with project-aware installation guidance plus the exact review command to rerun. Missing/malformed input, zero collected tests, failure, timeout, or execution error exits 4 with the canonical test command to diagnose and the exact review command to rerun. The timeout terminates the command's process group. Findings pass through byte-for-byte because a generic test result cannot prove or refute a specific review finding.

## Phase 5 — synthesis

Synthesis accepts only the artifacts named and hashed by the current coverage manifests:

```bash
python3 "$SKILL_DIR"/scripts/synthesize.py \
  --scope <scope.json> \
  --findings <validated-findings.jsonl> \
  --tool-findings <tool-findings.jsonl> \
  [--mutation-findings <mutation-findings.jsonl>] \
  --repo-root <repo-root> \
  --output-dir <report-dir>
```

Pass `--mutation-findings` exactly when `mutation_coverage.applicable` is true. The tool, axis, validator, diff, and applicable mutation files must retain the absolute paths, SHA-256 digests, finding counts, and run identities recorded by their producing phases. A missing, replaced, modified, or cross-run artifact exits 4 before rendering any verdict.
