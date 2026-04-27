"""Shared helpers for cross-skill structural tests."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

sys.path.insert(0, str(REPO_ROOT / "skills" / "brand-voice" / "scripts"))
from utils import parse_yaml_minimal, split_frontmatter  # noqa: E402


def get_skill_dirs():
    return sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith("."))


def load_frontmatter(skill_dir):
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    fm_text, body = split_frontmatter(text)
    fm = parse_yaml_minimal(fm_text) if fm_text else {}
    return fm, body
