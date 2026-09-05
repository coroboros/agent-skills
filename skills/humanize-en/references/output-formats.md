# Output formats

Canonical templates the skill emits depending on input mode and whether `-f <voice-doc>` is set. Every invocation closes with one of these — never improvise the structure.

## For inline text (default mode)

```
## Rewrite

<humanized text>

## Patterns removed

- #N <pattern name> — <short note, e.g., "4 instances, em-dashes converted to commas">
- ...
```

## For inline text under `-f`

```
## Rewrite

<humanized text>

## Coverage report

| Rule | Source | Detection | Hits | Action | Residual |
|---|---|---|---|---|---|
| #14 em-dash density | universal | prescan | 8 | preserved (citation format) | 0 |
| brand:all_caps_emphasis | brand | prescan-brand | 14 | rewrite | 0 |
| brand:negative_parallelism | brand | prescan-brand | 4 | rewrite | 0 |
| brand:forbidden_lexicon (26 entries) | brand | prescan-brand | 0 | n/a | 0 |
```

Every YAML rule appears in the table — even with 0 hits — so a future pass can verify the prior pass actually checked the rule. Missing rows are a hard failure, not a stylistic choice.

## For file paths

```
## Diff preview

<unified-diff-style or before/after blocks for changed passages>

## Coverage report
<as above; count-only summary in default mode>

## Validation report (under `-f` only)

status: clean | residuals | regression
<residual hits or regression diff if any>

<Applied diff for an authorized rewrite; proposed diff for audit-only.>
```

Carry the user's authorized target and mode through a parent skill invocation. Apply an explicitly requested rewrite without another approval prompt. Audit/propose stays read-only; a parent call or filepath alone cannot authorize a new edit. Label mechanical validation separately from semantic rule coverage.
