"""Scaffold dependency contracts shared with downstream skills."""

import unittest
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_MD = REPO_ROOT / "skills" / "scaffold" / "SKILL.md"
REFERENCES = REPO_ROOT / "skills" / "scaffold" / "references"
TEMPLATES = REPO_ROOT / "skills" / "scaffold" / "templates"
EVALS = REPO_ROOT / "skills" / "scaffold" / "evals" / "evals.json"


class TestDesignSystemRuntime(unittest.TestCase):
    def test_skill_body_uses_portable_invocation_arguments(self):
        body = SKILL_MD.read_text(encoding="utf-8")
        self.assertNotIn("$ARGUMENTS", body)
        self.assertIn("invocation arguments", body)

    def test_skill_creator_evals_cover_both_scaffolds_and_handoff(self):
        data = json.loads(EVALS.read_text(encoding="utf-8"))
        self.assertEqual(data["skill_name"], "scaffold")
        self.assertEqual([item["id"] for item in data["evals"]], [1, 2, 3])
        prompts = "\n".join(item["prompt"] for item in data["evals"])
        self.assertIn("next-cloudflare", prompts)
        self.assertIn("astro-cloudflare", prompts)
        self.assertIn("both generated scaffold templates", prompts)
        self.assertIn(
            "declared project-local designmd dependency",
            data["evals"][1]["expected_output"],
        )
        for item in data["evals"]:
            with self.subTest(eval_id=item["id"]):
                self.assertEqual(len(item["expectations"]), 4)
                self.assertTrue(item["expected_output"])

    def test_supported_web_scaffolds_install_designmd(self):
        for name in ("setup-astro-cloudflare.md", "setup-next-cloudflare.md"):
            with self.subTest(reference=name):
                text = (REFERENCES / name).read_text(encoding="utf-8")
                self.assertIn('pnpm --dir "{project_dir}" add -D', text)
                self.assertIn("@google/design.md", text)
                self.assertNotRegex(text, r"(?m)^pnpm add(?:\s|$)")
                self.assertIn("never rely on a previous shell call preserving", text)

    def test_generated_projects_expose_project_local_design_audit(self):
        for scaffold in ("astro-cloudflare", "next-cloudflare"):
            with self.subTest(scaffold=scaffold):
                scripts = json.loads(
                    (TEMPLATES / scaffold / "scripts.json").read_text(
                        encoding="utf-8"
                    )
                )
                self.assertEqual(
                    scripts["design:audit"],
                    "designmd lint DESIGN.md",
                )
                instructions = (
                    TEMPLATES / scaffold / "AGENTS.md"
                ).read_text(encoding="utf-8")
                self.assertIn("`pnpm design:audit`", instructions)
                self.assertIn(
                    "`skills add coroboros/agent-skills --skill design-system`",
                    instructions,
                )
                self.assertNotIn("`designmd lint DESIGN.md`", instructions)
                self.assertNotRegex(
                    instructions,
                    r"\b(?:npx|pnpm\s+dlx|bunx|uvx)\b",
                )
                self.assertEqual(
                    (TEMPLATES / "shared" / "CLAUDE.md").read_text(
                        encoding="utf-8"
                    ),
                    "@AGENTS.md\n",
                )

    def test_generated_project_references_use_canonical_agents_entrypoint(self):
        wrangler = (
            TEMPLATES / "next-cloudflare" / "wrangler.jsonc.template"
        ).read_text(encoding="utf-8")
        self.assertIn("See AGENTS.md", wrangler)
        self.assertNotIn("See CLAUDE.md", wrangler)


if __name__ == "__main__":
    unittest.main()
