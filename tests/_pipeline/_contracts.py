"""Single source of truth for cross-skill pipeline contracts.

Skills compose via the `-f` flag (see `.claude/rules/repo-conventions.md`):
a producer saves output to `.claude/output/<skill>/<slug>/`, a consumer
reads it via `-f <path>`. Schema drift between producer and consumer is
where bugs hide — pinning each contract here forces consumer tests to
break alongside producer drift in the same PR diff.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = REPO_ROOT / "skills"


CLUSTERS = {
    "workflow": {
        # brainstorm → spec → apex
        "producer": "brainstorm",
        "producer_output": ".claude/output/brainstorm/{slug}/brainstorm.md",
        "consumer": "spec",
        "consumer_output": ".claude/output/spec/{slug}/spec.md",
        "tertiary": "apex",  # apex consumes spec.md
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
        "merged_required_sections": ("forbidden_lexicon",),
        "forbidden_entry_required_keys": ("source", "value"),
    },
    "writing-v2": {
        # humanize-en + fix-grammar (sequential, no shared file)
        "producer": "humanize-en",
        "consumer": "fix-grammar",
        # The two skills stake out distinct surfaces — overlapping coverage
        # would create double-edit risks when chained. Validated by
        # test_writing_v2.TestSeparationOfConcerns.
        "humanize_territory": ("ai-tells", "patterns", "rule of three", "em-dash"),
        "fix_grammar_territory": ("grammar", "spelling", "typo"),
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
    },
}


def read_skill_md(name: str) -> str:
    return (SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")
