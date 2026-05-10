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

Apply? (yes/no)
```

Apply only on explicit `yes` **from the user**. When another skill invokes `/humanize-en` on a file, the approval prompt still flows to the end user — a parent skill must not auto-answer on their behalf.
