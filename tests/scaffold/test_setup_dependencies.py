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
        self.assertEqual(
            [item["id"] for item in data["evals"]],
            [1, 2, 3, 4, 5, 6, 7],
        )
        prompts = "\n".join(item["prompt"] for item in data["evals"])
        self.assertIn("next-cloudflare", prompts)
        self.assertIn("astro-cloudflare", prompts)
        self.assertIn("both generated scaffold templates", prompts)
        self.assertIn("existing project that already has package.json", prompts)
        self.assertIn("customer portals/customer-portal", prompts)
        self.assertIn("Node 22.11.0", prompts)
        self.assertIn("jq is unavailable", prompts)
        self.assertIn("Tailwind, shadcn/ui, and package-name contracts", prompts)
        self.assertIn(
            "declared project-local designmd dependency",
            data["evals"][1]["expected_output"],
        )
        expected_counts = {1: 4, 2: 4, 3: 4, 4: 2, 5: 4, 6: 4, 7: 4}
        for item in data["evals"]:
            with self.subTest(eval_id=item["id"]):
                self.assertEqual(
                    len(item["expectations"]), expected_counts[item["id"]]
                )
                self.assertTrue(item["expected_output"])

    def test_supported_web_scaffolds_install_designmd(self):
        for name in ("setup-astro-cloudflare.md", "setup-next-cloudflare.md"):
            with self.subTest(reference=name):
                text = (REFERENCES / name).read_text(encoding="utf-8")
                self.assertIn('pnpm --dir "{project_dir}" add -D', text)
                self.assertIn("@google/design.md", text)
                self.assertNotRegex(text, r"(?m)^pnpm add(?:\s|$)")
                self.assertIn("never rely on a previous shell call preserving", text)

    def test_framework_generators_pin_supported_majors(self):
        next_setup = (REFERENCES / "setup-next-cloudflare.md").read_text(
            encoding="utf-8"
        )
        astro_setup = (REFERENCES / "setup-astro-cloudflare.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("pnpm create next-app@16", next_setup)
        self.assertIn('next-app@16 "{project_dir}"', next_setup)
        self.assertIn("--no-linter", next_setup)
        self.assertIn("--no-react-compiler", next_setup)
        self.assertIn("--use-pnpm", next_setup)
        self.assertIn("--disable-git", next_setup)
        self.assertIn("--no-agents-md", next_setup)
        self.assertIn("--yes", next_setup)
        self.assertNotIn("--eslint=false", next_setup)
        self.assertIn("pnpm create astro@5", astro_setup)
        self.assertIn('astro@5 "{project_dir}"', astro_setup)
        self.assertNotIn("--typescript", astro_setup)
        self.assertIn("astro@6", astro_setup)
        self.assertIn("@astrojs/cloudflare@13", astro_setup)
        self.assertIn("@astrojs/sitemap@3", astro_setup)
        self.assertIn("tailwindcss@4", astro_setup)
        self.assertIn("@tailwindcss/vite@4", astro_setup)
        self.assertNotIn("astro add", astro_setup)
        self.assertIn("shadcn@4", next_setup)
        self.assertIn(
            'pnpm --dir "{project_dir}" exec shadcn init --defaults --base base --no-rtl',
            next_setup,
        )
        self.assertNotIn("pnpm dlx", next_setup)
        self.assertNotIn("@latest", next_setup)
        self.assertNotIn("@latest", astro_setup)

    def test_generator_owned_files_have_explicit_overlay_contracts(self):
        skill = SKILL_MD.read_text(encoding="utf-8")
        astro_setup = (REFERENCES / "setup-astro-cloudflare.md").read_text(
            encoding="utf-8"
        )
        astro_instructions = (
            TEMPLATES / "astro-cloudflare" / "AGENTS.md"
        ).read_text(encoding="utf-8")
        next_instructions = (
            TEMPLATES / "next-cloudflare" / "AGENTS.md"
        ).read_text(encoding="utf-8")

        self.assertIn("`astro.config.mjs`", astro_setup)
        self.assertLess(
            astro_setup.index("`astro.config.mjs`"),
            astro_setup.index("## 5. Shared overlay"),
        )
        self.assertIn("preserve framework-generated `readme.md`", skill.lower())
        self.assertNotIn("@README.md", astro_instructions)
        self.assertNotIn("@README.md", next_instructions)

    def test_generated_runtime_contract_files_are_centralized(self):
        self.assertEqual(
            (TEMPLATES / "shared" / "node-version").read_text(encoding="utf-8"),
            "22.12.0\n",
        )
        self.assertIn(
            "Copy to .dev.vars",
            (TEMPLATES / "shared" / "dev.vars.example").read_text(
                encoding="utf-8"
            ),
        )
        self.assertEqual(
            json.loads(
                (
                    TEMPLATES
                    / "astro-cloudflare"
                    / "tsconfig.json.template"
                ).read_text(encoding="utf-8")
            ),
            {"extends": "astro/tsconfigs/strict"},
        )
        self.assertEqual(
            (TEMPLATES / "shared" / "tailwind.css").read_text(encoding="utf-8"),
            '@import "tailwindcss";\n',
        )
        self.assertIn(
            'import "../styles/global.css";',
            (
                TEMPLATES / "astro-cloudflare" / "index.astro.template"
            ).read_text(encoding="utf-8"),
        )

    def test_generated_tailwind_instructions_use_css_first_v4(self):
        astro_instructions = (
            TEMPLATES / "astro-cloudflare" / "AGENTS.md"
        ).read_text(encoding="utf-8")
        next_setup = (REFERENCES / "setup-next-cloudflare.md").read_text(
            encoding="utf-8"
        )
        astro_setup = (REFERENCES / "setup-astro-cloudflare.md").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("tailwind.config", astro_instructions)
        self.assertIn("src/styles/global.css", astro_instructions)
        self.assertIn('@import "tailwindcss";', next_setup)
        self.assertIn('@import "tailwindcss";', astro_setup)

    def test_skill_commands_quote_every_user_derived_argument(self):
        body = SKILL_MD.read_text(encoding="utf-8")
        self.assertIn('preflight.sh "{project_dir}" "{project_name}"', body)
        self.assertIn(
            'overlay_templates.sh "{scaffold}" "{project_name}" "{project_dir}"',
            body,
        )
        self.assertIn('verify_scaffold.sh "{project_dir}"', body)

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
                    "`npx skills add coroboros/agent-skills --skill design-system`",
                    instructions,
                )
                self.assertNotIn("`designmd lint DESIGN.md`", instructions)
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
