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
    },
    "writing-v1": {
        # brand-voice → humanize-en
        "producer": "brand-voice",
        "producer_output": "BRAND-VOICE.md",
        "consumer": "humanize-en",
        "consumer_reader_script": "extract_rules.py",
    },
    "writing-v2": {
        # humanize-en + fix-grammar (sequential, no shared file)
        "producer": "humanize-en",
        "consumer": "fix-grammar",
    },
    "design": {
        # award-design → design-system
        "producer": "award-design",
        "producer_output": "DESIGN.md",
        "consumer": "design-system",
    },
}


def read_skill_md(name: str) -> str:
    return (SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")
