"""Single source of truth for cross-skill pipeline contracts.

Skills compose via the `-f` flag (see `.agents/rules/repo-conventions.md`):
a producer saves to `~/.agents/output/<project>/<skill>/<skill>-<slug>.md`
and reports the fully-expanded absolute path; a consumer takes that explicit
path via `-f` verbatim — no reconstruction, no inference. Schema drift
between producer and consumer is where bugs hide —
pinning each contract here forces consumer tests to break alongside producer
drift in the same PR diff.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = REPO_ROOT / "skills"


CLUSTERS = {
    "workflow": {
        # forge → apex
        "producer": "forge",
        "producer_output": "~/.agents/output/{project}/forge/forge-{slug}.md",
        "consumer": "apex",  # apex consumes the forge plan via -f
        # Schema keys the producer commits to and the consumer reads — drift
        # in either side breaks the chain. Validated by test_workflow_cluster.
        "spec_workstream_required_columns": ("Priority", "Complexity", "Depends on"),
        "spec_workstream_priorities": ("P0", "P1", "P2"),
        "spec_workstream_complexities": ("S", "M", "L", "XL"),
    },
    "writing-v1": {
        # brand-voice → humanize-en
        "producer": "brand-voice",
        "producer_output": "BRAND-VOICE.md",
        "consumer": "humanize-en",
        "consumer_reader_script": "extract_rules.py",
        # Keys humanize-en reads from extract_rules --explain-json output.
        "explain_json_required_keys": ("chain", "merged"),
        "merged_required_sections": ("forbidden_lexicon", "lexical_exceptions"),
        "forbidden_entry_required_keys": ("source", "value"),
        # Inner shape of lexical_exceptions — the whitelists humanize-en reads.
        # Drift here breaks the silent-false-positive contract (BPM, MIDI,
        # in-your-face, etc. legitimately admitted by some voices).
        "lexical_exceptions_inner_keys": ("acronyms", "compound_idioms"),
    },
    "design": {
        # award-design → design-system
        "producer": "award-design",
        "producer_output": "DESIGN.md",
        "consumer": "design-system",
        # Google DESIGN.md open standard contract — eight ordered prose
        # sections + YAML frontmatter with design tokens. Producer must
        # commit to this; consumer's audit.sh enforces it.
        "design_md_canonical_sections": (
            "Overview",
            "Colors",
            "Typography",
            "Layout",
            "Elevation & Depth",
            "Shapes",
            "Components",
            "Do's and Don'ts",
        ),
        "design_md_token_groups": (
            "colors", "typography", "rounded", "spacing", "components",
        ),
        # Extension namespaces — top-level YAML keys preserved-but-unvalidated
        # by the Google CLI per design-md-spec.md. Components MUST NOT bind to
        # these (the closed property-token set rejects them — empirical lint
        # failure). Validated bidirectionally by /design-system audit-extensions.
        "design_md_extension_namespaces": (
            "motion", "shadows", "aspectRatios", "heights", "containers",
            "breakpoints", "zIndex", "borderWidths", "opacity", "scrollTriggers",
        ),
        # The eight canonical component property tokens — the closed set.
        # Anything outside this is rejected as an unknown property.
        "design_md_canonical_property_tokens": (
            "backgroundColor", "textColor", "typography", "rounded",
            "padding", "size", "height", "width",
        ),
    },
    "review": {
        # code-ultrareview → apex. Report-only producer (by default); apex
        # consumes the saved report via -f as generic foundational context
        # (no apex change). /oneshot is intentionally NOT a -f consumer (it
        # has no -f flag) — the skill points there manually with a
        # description, never a file.
        #
        # confidence_threshold (80) is the routing boundary, NOT a silent
        # drop — sub-80 findings surface as "[unverified]" with the
        # rationale "Sub-80 confidence ({score}) — verify locally before
        # action." (the A2 no-silent-drop contract). See
        # `scripts/synthesis_core.py::apply_a2` for the routing primitives
        # and `scripts/synthesize.py` for the Phase 5 composer. Consumers
        # reading reports MUST expect per-severity sub-sections
        # (### 🔴 High / ### 🟠 Medium / ### 🟢 Low / ### ⚠️ Unverified) under
        # ## 🔎 Findings — every ## section is emoji-prefixed and HR-separated.
        "producer": "code-ultrareview",
        "producer_output": "~/.agents/output/{project}/code-ultrareview/code-ultrareview-{slug}.md",
        "consumer": "apex",
        # Schema the producer commits to and a consumer reads — drift in
        # either side breaks the chain. Validated by test_review_cluster.
        # Sections every rendered report must carry, each with its canonical
        # emoji prefix. `📐 Derivation coverage` and `🪛 --apply-safe summary`
        # are opt-in (only emitted under their respective flags) — required
        # in the TEMPLATE but not in the contract; see
        # `tests/code-ultrareview/test_report_template.py::CANONICAL_SECTIONS`
        # for the broader template-level list. The emoji prefix is part of the
        # section identity — `## Findings` (without emoji) is non-conformant.
        "report_required_sections": (
            "📋 Axis summary",
            "🔎 Findings",
            "✅ What looks good",
            "⚖️ Verdict",
            "🧰 Tools skipped",
            "🛡️ What I did NOT check",
        ),
        # The four mandatory sub-sections inside `## 🔎 Findings`. Render in
        # this order, every time, even when count is 0 (body `_None._`).
        # Test-only SSOT: consumed by tests/code-ultrareview/test_report_template.py
        # (template parity), tests/_pipeline/test_review_cluster.py (fixture
        # parity), and tests/code-ultrareview/test_section_emoji_drift.py (regression
        # sweep). No skill code reads this; the tuple pins the contract so
        # template ↔ fixture drift breaks the suite.
        "report_findings_subsections": (
            "🔴 High",
            "🟠 Medium",
            "🟢 Low",
            "⚠️ Unverified",
        ),
        # The 8 canonical axes (always-on) plus the conditional 9th
        # (`coherence`, activated when metadata files appear in the diff).
        # Mirror `scripts/synthesis_core.py::CANONICAL_AXES` + `CONDITIONAL_AXES`.
        "report_axis_keys": (
            "correctness", "simplification", "tests", "documentation",
            "style", "intent", "design-api", "performance", "coherence",
        ),
        # High/Medium/Low retained for compatibility; Important/Nit/
        # Pre-existing added per Anthropic Managed Code Review and emitted
        # by `scripts/synthesis_core.py::assign_anthropic_tier`. Both
        # schemes coexist on the same finding row — readers can parse either.
        "report_severities": (
            "High", "Medium", "Low",
            "Important", "Nit", "Pre-existing",
        ),
        "confidence_threshold": 80,
        # Mandatory entries in `## 🛡️ What I did NOT check`. The skill
        # surfaces them in every report — `/security-review` is the
        # explicit command pointer for the security deferral; the other
        # entries describe out-of-scope categories rather than commands.
        "deferral_targets": (
            "/security-review",
            "Runtime performance",
            "Flaky test detection",
        ),
        # Conventional Comments labels emitted in the JSONL alongside the
        # markdown. Drift here breaks `tests/code-ultrareview/test_findings_jsonl.py`
        # and any downstream consumer piping through `gh pr comment`.
        "jsonl_labels": (
            "issue", "suggestion", "nitpick", "question",
        ),
    },
}


def read_skill_md(name: str) -> str:
    return (SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")
