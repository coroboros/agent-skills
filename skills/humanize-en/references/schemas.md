# humanize-en — JSON Schemas

Contracts for the deterministic scripts under `scripts/`. Any script that emits or consumes JSON conforms to one of the shapes below.

## prescan hit list

Emitted by `scripts/prescan.py <file>` on stdout. A JSON array; each entry is one pattern hit.

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
