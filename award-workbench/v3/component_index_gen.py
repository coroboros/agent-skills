#!/usr/bin/env python3
"""Per-archetype component indexes — the discovery layer for the tier-2 load.

Blueprint §2: `assets/components/` is never read whole. A build that needs a
behaviour greps the manifest today, which means it has to already know the id it
wants. The index inverts that: every component and form tagged for the archetype
appears as `id — first sentence of whenToUse` inside the archetype's tier-2 file,
so selection happens in context the build has already paid for. The manifest
stays authoritative — slots, tokens, deps, variants and init signatures live only
there, and 11 of 103 components carry manifest facts absent from their file
headers, so this index is generated FROM the manifest and never replaces it.

Emits one `## Component index` block per archetype. Paste each block under that
heading in `references/<stem>.md`; re-run and re-paste when the manifest changes.

Usage:
    python3 component_index_gen.py [--archetype NAME] [--out DIR]

Exit codes: 0 = emitted, 1 = unknown archetype or unreadable manifest.
"""

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent.parent / "skills" / "award-design"
MANIFEST = SKILL_DIR / "assets" / "components" / "manifest.json"

# The manifest tags entries with the playbook-era slugs; the references are named
# for the archetype. This mapping is the only place the two vocabularies meet.
SLUG_TO_STEM = {
    "minimalist": "minimalist",
    "brutalist": "brutalist",
    "editorial-dark": "editorial",
    "bold-maximal": "bold-maximal",
    "immersive": "immersive-cinematic",
    "experimental": "experimental",
    "corporate-luxury": "corporate-luxury",
    "bento": "bento-card",
    "spatial-organic": "spatial-organic",
}

HEADING = "## Component index"

PREAMBLE = (
    "Generated from `assets/components/manifest.json` — the authority for slots, "
    "variants, tokens, deps and `init` signatures, and the only place 11 of the 103 "
    "components record facts their file headers omit. Each row is the id plus the "
    "opening of its `whenToUse`, clipped: enough to pick, never enough to build. "
    "Grep the manifest for the chosen id to get its contract. Forms are the page "
    "skeletons (CSS, slots, variants); components are the behaviours that mount into "
    "their slots."
)

CLIP = 160

# A sentence ends on a period preceded by a word character or a closing bracket and
# followed by an opening capital — which is what keeps `lerp 0.1`, `(.19,1,.22,1)`
# and `Terminal's` from splitting the row.
SENTENCE_END = re.compile(r"(?<=[a-zA-Z\)\]>”\"'])\.\s+(?=[A-Z“\"(\[])")


def first_sentence(text):
    head = SENTENCE_END.split(text.strip(), maxsplit=1)[0].rstrip()
    if len(head) > CLIP:
        # Several entries carry a 500+ char opening clause; the row is a pointer, so
        # it clips on the last word boundary rather than paying for the whole spec.
        return head[:CLIP].rsplit(" ", 1)[0].rstrip(" ,;:—-") + "…"
    return head if head.endswith(".") else head + "."


def rows_for(manifest, slug):
    def collect(entries):
        return sorted(
            (e["id"], first_sentence(e["whenToUse"]))
            for e in entries if slug in e.get("archetypes", ()))

    return collect(manifest["forms"]), collect(manifest["components"])


def render(manifest, slug):
    forms, components = rows_for(manifest, slug)
    lines = [HEADING, "", PREAMBLE, "",
             f"**Forms** ({len(forms)}) — page skeletons"]
    lines += [f"- `{cid}` — {blurb}" for cid, blurb in forms]
    lines += ["", f"**Components** ({len(components)}) — behaviours"]
    lines += [f"- `{cid}` — {blurb}" for cid, blurb in components]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="award-design per-archetype component indexes from the manifest")
    parser.add_argument("--archetype", default=None,
                        help="manifest slug or reference stem; omitted, all nine are emitted")
    parser.add_argument("--out", default=None, type=Path,
                        help="write <stem>.md blocks into this directory instead of stdout")
    args = parser.parse_args(argv)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    slugs = list(SLUG_TO_STEM)
    if args.archetype:
        stem_to_slug = {stem: slug for slug, stem in SLUG_TO_STEM.items()}
        slug = args.archetype if args.archetype in SLUG_TO_STEM else stem_to_slug.get(args.archetype)
        if slug is None:
            print(f"unknown archetype {args.archetype!r}; slugs: {', '.join(SLUG_TO_STEM)}",
                  file=sys.stderr)
            return 1
        slugs = [slug]

    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
    for slug in slugs:
        block = render(manifest, slug)
        if args.out:
            (args.out / f"{SLUG_TO_STEM[slug]}.md").write_text(block, encoding="utf-8")
        else:
            print(f"<!-- {SLUG_TO_STEM[slug]}.md -->")
            print(block)
    return 0


if __name__ == "__main__":
    sys.exit(main())
