# humanize-en — JSON Schemas

Contracts for the deterministic scripts under `scripts/`. Any script that emits or consumes JSON conforms to one of the shapes below.

## prescan hit list (universal)

Emitted by `scripts/prescan.py <file>` on stdout (no `--brand` flag). A JSON array; each entry is one universal pattern hit.

```json
[
  {
    "pattern": 7,
    "label": "ai-vocabulary",
    "line": 42,
    "snippet": "...we'll delve into the intricacies of the..."
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| `pattern` | integer | Pattern number per `references/patterns.md` (1–32). |
| `label` | string | Short slug naming the pattern family (`significance-inflation`, `promotional`, `ai-vocabulary`, `copula-avoidance`, `negative-parallelism`, `em-dash-density`, `filler`, `signposting`). |
| `line` | integer | 1-indexed line number in the source (post-mask). |
| `snippet` | string | Up to ~20 chars of context on either side of the match. |

Exit codes: `0` scan complete (hits or not), `1` argument or I/O error.

## prescan hit list (brand-aware)

Emitted when `scripts/prescan.py --brand <voice-doc> <file>` is invoked. Universal hits gain a `source: "universal"` discriminator so callers can split the merged array; brand hits use a string `pattern` slug, carry `source: "brand"`, and add `rule_id` so the coverage report can attribute each rewrite to the originating YAML rule.

```json
[
  {
    "pattern": 7,
    "label": "ai-vocabulary",
    "line": 12,
    "snippet": "Moreover, the data...",
    "source": "universal"
  },
  {
    "pattern": "brand:all_caps_emphasis",
    "label": "brand-all-caps-emphasis",
    "line": 3,
    "snippet": "## ALL CAPS HEADING",
    "source": "brand",
    "rule_id": "all_caps_emphasis"
  },
  {
    "pattern": "brand:forbidden_lexicon",
    "label": "brand-forbidden-lexicon",
    "line": 9,
    "snippet": "...game-changing stuff.",
    "source": "brand",
    "rule_id": "forbidden_lexicon:game-changing"
  },
  {
    "pattern": "brand:rewrite_rule",
    "label": "brand-rewrite-rule",
    "line": 11,
    "snippet": "Great question — let me explain.",
    "source": "brand",
    "rule_id": "rewrite_rule:no-salesperson-opener"
  }
]
```

| Field | Type | Source values | Description |
|-------|------|---------------|-------------|
| `pattern` | integer or string | universal / brand | `1–32` for universal; one of these 11 slugs for brand: `brand:all_caps_emphasis`, `brand:forbidden_lexicon`, `brand:rewrite_rule`, `brand:first_person_singular`, `brand:first_person_plural`, `brand:second_person`, `brand:signposting`, `brand:negative_parallelism`, `brand:rule_of_three_heading`, `brand:rhetorical_questions`, `brand:emoji`. |
| `label` | string | both | Short slug naming the family. Brand labels prefix `brand-`. |
| `line` | integer | both | 1-indexed line number. |
| `snippet` | string | both | Up to ~20 chars of context. |
| `source` | string | both | `"universal"` or `"brand"`. Always present on brand-aware runs. |
| `rule_id` | string | brand | Originating YAML rule identifier. Format depends on the detector — see the table below. Brand hits only. |

Brand `rule_id` formats — exact values emitted per detector:

| Pattern slug | `rule_id` format | Example |
|---|---|---|
| `brand:all_caps_emphasis` | `all_caps_emphasis` (literal) | `all_caps_emphasis` |
| `brand:forbidden_lexicon` | `forbidden_lexicon:<term>` (term verbatim) | `forbidden_lexicon:game-changing` |
| `brand:rewrite_rule` | `rewrite_rule:<rule_id>` (from YAML) | `rewrite_rule:no-hedging-imperative` |
| `brand:first_person_singular` | `pronouns:first-person singular` | identical |
| `brand:first_person_plural` | `pronouns:first-person plural in marketing` | identical |
| `brand:second_person` | `pronouns:second-person 'you' in marketing` | identical |
| `brand:signposting` | `signposting` (literal) | `signposting` |
| `brand:negative_parallelism` | `negative_parallelism` (literal) | `negative_parallelism` |
| `brand:rule_of_three_heading` | `rule_of_three` (literal) | `rule_of_three` |
| `brand:rhetorical_questions` | `rhetorical_questions` (literal) | `rhetorical_questions` |
| `brand:emoji` | `emoji` (literal) | `emoji` |

Each detector is enabled only when the voice doc declares it (via `forbidden_patterns`, `pronouns.forbid`, `forbidden_lexicon`, or `rewrite_rules`). The `pronouns:second-person 'you' in marketing` rule_id contains a literal apostrophe — JSON-safe but worth quoting carefully when pasted into shell tooling.

`forbidden_patterns` values that have **no** deterministic detector (`marketing_analogies`, `superficial_ing` per `../brand-voice/references/canonical-format.md`) are silently passed through — the LLM rewrite step is the only enforcement layer. The brand prescan emits zero hits for these even when present in the YAML; the *Coverage report* row still appears under `-f` so the audit gap is visible.

`pronouns.forbid` is matched case-insensitively — voice docs may write `"First-person singular"` or `"first-person singular"` interchangeably; both enable the detector.

Exit codes match the universal contract: `0` scan complete, `1` argument or I/O error (including missing or malformed voice doc).

## validate result

Emitted by `scripts/validate.py <file> [--brand <voice-doc>] [--baseline <hits.json>]` on stdout. Single object summarising the post-rewrite state.

```json
{
  "path": "drafts/release-notes.md",
  "status": "residuals",
  "residuals": [
    {"pattern": "brand:all_caps_emphasis", "label": "brand-all-caps-emphasis",
     "line": 14, "snippet": "...THE non-negotiable...", "source": "brand",
     "rule_id": "all_caps_emphasis"}
  ],
  "summary": {
    "total_residuals": 1,
    "universal_residuals": 0,
    "brand_residuals": 1,
    "new_hit_count": 0
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `path` | string | Absolute or relative path to the validated file. |
| `status` | string | `"clean"` (zero hits), `"residuals"` (hits remain but none are new vs. baseline), or `"regression"` (at least one hit appears that was not in the baseline). |
| `residuals` | array | All current hits. Same shape as the prescan hit list — universal hits have integer `pattern`, brand hits have string `pattern` + `source: "brand"` + `rule_id`. |
| `new_hits` | array | Present only when `status == "regression"`. Subset of `residuals` whose signature is not in the baseline. |
| `summary.total_residuals` | integer | `len(residuals)`. |
| `summary.universal_residuals` | integer | Count of residuals with `source != "brand"`. |
| `summary.brand_residuals` | integer | Count of residuals with `source == "brand"`. |
| `summary.new_hit_count` | integer | `len(new_hits)`; always 0 unless status is `"regression"`. |

Exit codes: `0` if `status` is `"clean"` or `"residuals"`, `1` on `"regression"`, `2` on argument or I/O errors (missing target, missing baseline, malformed JSON, invalid voice doc).

Hit identity for the regression check is `(pattern, snippet)` — the line number is deliberately omitted. The rewrite step can shorten or lengthen the file, shifting every subsequent line, so a signature that included the line would treat the same lexical violation at a new line number as a regression. The 20-char-each-side snippet from `prescan.py:scan` usually disambiguates same-pattern matches that genuinely live in different sentences; two identical sentences on different lines collapse into one signature, which is the right trade-off — regressions surface *new* lexical violations, not duplicate-count drift.

## eval sample

Shape of a file in `eval-corpus/samples/<name>.json`. Pairs an input prose sample with the expected pattern hits.

```json
{
  "id": "hero-landing-01",
  "description": "Homepage hero copy — classic SaaS AI-voice. Em-dash overuse, negative parallelism, filler.",
  "input": "Our platform — truly powerful — lets you delve into the data. It's not just analytics, it's insight. In order to get started, simply sign up.",
  "expected_hits": [
    {"pattern": 7, "label": "ai-vocabulary"},
    {"pattern": 9, "label": "negative-parallelism"},
    {"pattern": 14, "label": "em-dash-density"},
    {"pattern": 23, "label": "filler"}
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Kebab-case sample identifier. Unique within the corpus. |
| `description` | string | Short human-readable summary — what this sample tests. |
| `input` | string | The AI-voice prose to scan. |
| `expected_hits` | array | Expected pattern hits. Each entry has `pattern` (int) and `label` (string). Line numbers are not asserted — only the set of pattern families. |

Samples assert the set of patterns expected, not exact match counts. This keeps the corpus stable as `prescan.py` evolves per-pattern regexes.

## eval result

Emitted by `scripts/eval_patterns.py --sample <path>` or with the full corpus. Summarises pass/fail per pattern for each sample.

```json
{
  "samples": [
    {
      "id": "hero-landing-01",
      "expected_patterns": [7, 9, 14, 23],
      "detected_patterns": [7, 9, 14, 23],
      "missing": [],
      "extra": [],
      "pass": true
    }
  ],
  "summary": {
    "total_samples": 1,
    "passed": 1,
    "failed": 0,
    "pass_rate": 1.0
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `samples[].id` | string | Sample identifier from the corpus file. |
| `samples[].expected_patterns` | int[] | Sorted, de-duplicated list from the sample's `expected_hits`. |
| `samples[].detected_patterns` | int[] | Sorted, de-duplicated list of pattern numbers `prescan.py` returned. |
| `samples[].missing` | int[] | Expected but not detected — under-coverage. |
| `samples[].extra` | int[] | Detected but not expected — potential false positive. |
| `samples[].pass` | boolean | `missing.length == 0 AND extra.length == 0`. |
| `summary.pass_rate` | number | `passed / total_samples`, 0–1. |

Exit codes: `0` all samples pass, `1` at least one fails, `2` argument or I/O error.
