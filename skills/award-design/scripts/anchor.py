#!/usr/bin/env python3
"""The material anchor — a seeded draw from a curated ground/accent pool.

Same rut as the direction roll, one layer down: asked for a palette, a model
returns its argmax — warm cream, serif, terracotta — and generic negation only
moves it to a *different* fixed palette. So the palette is drawn rather than
asked for. Each seed is a physical-world material (a thing with a surface, a
temperature, a way of taking light) rather than a software archetype, because
a material implies a light that can drive a whole page, which an abstraction
like "dark mode" cannot.

Pool curation, three invariants the seeds are chosen against:
  * the anti-cream band (CREAM_BAND below) is never a GROUND — that warm-neutral
    pale is the model default the judges read as a tell;
  * ground hues spread evenly over the 30° buckets, so the draw cannot pile onto
    the frequent hues the way an unseeded pick does;
  * `quiet_safe` marks the seeds a regulated or accessibility-first brief can
    take: no neon micro-glow, no multi-hue gradient ground, accent chroma ≤ 0.17.

The five families are the article's dominant strategies (foundations.md):
dark base + saturated accent · monochromatic OKLCH depth · earthy pastels ·
neon micro-glow on dark · OKLCH multi-hue. Determinism is the point — the key
is printed with the reproduction command, and `os.urandom` seeds the default
key and nothing else.

Usage (paths relative to this skill's root):
    python3 scripts/anchor.py [--from KEY] [--brief-class default|regulated|quiet]
"""

import argparse
import hashlib
import math
import os
import sys

SCRIPT_REL = "scripts/anchor.py"
SCOPE = "anchor"
SALT = "material-seed"
QUIET_CLASSES = ("regulated", "quiet")
BRIEF_CLASSES = ("default",) + QUIET_CLASSES

# Never a ground: warm-neutral OKLCH L 0.84-0.97, C < 0.06, hue 40-100.
CREAM_BAND = {"lightness": (0.84, 0.97), "chroma_max": 0.06, "hue": (40.0, 100.0)}

# id · material · palette_family · oklch_ground · oklch_accent · temperature · quiet_safe
SEEDS = [
    {"id": "forge-scale", "material": "forge scale", "palette_family": "dark-base-accent",
     "oklch_ground": "oklch(0.19 0.030 25)", "oklch_accent": "oklch(0.74 0.19 48)",
     "temperature": "warm", "quiet_safe": False},
    {"id": "madder-root", "material": "dried madder root", "palette_family": "earthy-pastel",
     "oklch_ground": "oklch(0.80 0.050 20)", "oklch_accent": "oklch(0.42 0.14 22)",
     "temperature": "warm", "quiet_safe": True},
    {"id": "kiln-brick", "material": "kiln brick", "palette_family": "mono-oklch-depth",
     "oklch_ground": "oklch(0.36 0.085 42)", "oklch_accent": "oklch(0.86 0.10 52)",
     "temperature": "warm", "quiet_safe": True},
    {"id": "smoked-oak", "material": "smoked oak", "palette_family": "earthy-pastel",
     "oklch_ground": "oklch(0.70 0.065 58)", "oklch_accent": "oklch(0.38 0.10 250)",
     "temperature": "warm", "quiet_safe": True},
    {"id": "brass-shim", "material": "brass shim", "palette_family": "mono-oklch-depth",
     "oklch_ground": "oklch(0.30 0.050 75)", "oklch_accent": "oklch(0.84 0.13 85)",
     "temperature": "warm", "quiet_safe": True},
    {"id": "sulfur-crust", "material": "sulfur crust", "palette_family": "neon-microglow",
     "oklch_ground": "oklch(0.15 0.020 80)", "oklch_accent": "oklch(0.90 0.19 95)",
     "temperature": "warm", "quiet_safe": False},
    {"id": "wheat-chaff", "material": "wheat chaff", "palette_family": "earthy-pastel",
     "oklch_ground": "oklch(0.76 0.055 100)", "oklch_accent": "oklch(0.35 0.09 145)",
     "temperature": "warm", "quiet_safe": True},
    {"id": "lichen-stone", "material": "lichen on stone", "palette_family": "mono-oklch-depth",
     "oklch_ground": "oklch(0.32 0.045 110)", "oklch_accent": "oklch(0.82 0.11 118)",
     "temperature": "neutral", "quiet_safe": True},
    {"id": "leaf-pulp", "material": "crushed leaf pulp", "palette_family": "dark-base-accent",
     "oklch_ground": "oklch(0.21 0.040 140)", "oklch_accent": "oklch(0.78 0.18 135)",
     "temperature": "cool", "quiet_safe": False},
    {"id": "celadon-glaze", "material": "celadon glaze", "palette_family": "earthy-pastel",
     "oklch_ground": "oklch(0.78 0.050 145)", "oklch_accent": "oklch(0.40 0.12 20)",
     "temperature": "cool", "quiet_safe": True},
    {"id": "verdigris-copper", "material": "verdigris copper", "palette_family": "mono-oklch-depth",
     "oklch_ground": "oklch(0.34 0.055 170)", "oklch_accent": "oklch(0.84 0.10 165)",
     "temperature": "cool", "quiet_safe": True},
    {"id": "phosphor-glass", "material": "phosphor tube glass", "palette_family": "neon-microglow",
     "oklch_ground": "oklch(0.14 0.015 165)", "oklch_accent": "oklch(0.88 0.20 158)",
     "temperature": "cool", "quiet_safe": False},
    {"id": "glacier-ice", "material": "glacier ice", "palette_family": "multi-hue-oklch",
     "oklch_ground": "oklch(0.26 0.050 195)", "oklch_accent": "oklch(0.86 0.14 200)",
     "temperature": "cool", "quiet_safe": False},
    {"id": "wet-slate", "material": "wet slate", "palette_family": "dark-base-accent",
     "oklch_ground": "oklch(0.18 0.020 200)", "oklch_accent": "oklch(0.76 0.15 190)",
     "temperature": "cool", "quiet_safe": True},
    {"id": "anodized-aluminum", "material": "anodized aluminum",
     "palette_family": "mono-oklch-depth",
     "oklch_ground": "oklch(0.24 0.025 235)", "oklch_accent": "oklch(0.80 0.12 230)",
     "temperature": "cool", "quiet_safe": True},
    {"id": "deep-water", "material": "deep water", "palette_family": "dark-base-accent",
     "oklch_ground": "oklch(0.17 0.055 230)", "oklch_accent": "oklch(0.74 0.17 215)",
     "temperature": "cool", "quiet_safe": True},
    {"id": "wet-asphalt", "material": "wet asphalt", "palette_family": "dark-base-accent",
     "oklch_ground": "oklch(0.16 0.012 255)", "oklch_accent": "oklch(0.80 0.16 70)",
     "temperature": "neutral", "quiet_safe": True},
    {"id": "printed-newsprint", "material": "printed newsprint",
     "palette_family": "mono-oklch-depth",
     "oklch_ground": "oklch(0.90 0.008 250)", "oklch_accent": "oklch(0.44 0.16 25)",
     "temperature": "cool", "quiet_safe": True},
    {"id": "iodine-crystal", "material": "iodine crystal", "palette_family": "neon-microglow",
     "oklch_ground": "oklch(0.15 0.030 285)", "oklch_accent": "oklch(0.72 0.22 290)",
     "temperature": "cool", "quiet_safe": False},
    {"id": "amethyst-quartz", "material": "amethyst quartz", "palette_family": "multi-hue-oklch",
     "oklch_ground": "oklch(0.28 0.060 290)", "oklch_accent": "oklch(0.85 0.13 320)",
     "temperature": "cool", "quiet_safe": False},
    {"id": "dyed-silk", "material": "aniline-dyed silk", "palette_family": "multi-hue-oklch",
     "oklch_ground": "oklch(0.23 0.055 315)", "oklch_accent": "oklch(0.82 0.15 340)",
     "temperature": "cool", "quiet_safe": False},
    {"id": "plum-skin", "material": "plum skin", "palette_family": "earthy-pastel",
     "oklch_ground": "oklch(0.74 0.045 320)", "oklch_accent": "oklch(0.36 0.11 300)",
     "temperature": "cool", "quiet_safe": True},
    {"id": "oxblood-leather", "material": "oxblood leather", "palette_family": "mono-oklch-depth",
     "oklch_ground": "oklch(0.26 0.075 350)", "oklch_accent": "oklch(0.84 0.11 355)",
     "temperature": "warm", "quiet_safe": True},
    {"id": "carmine-shellac", "material": "carmine shellac", "palette_family": "neon-microglow",
     "oklch_ground": "oklch(0.13 0.025 345)", "oklch_accent": "oklch(0.70 0.23 5)",
     "temperature": "warm", "quiet_safe": False},
]

COMPOSITION_NOTE = (
    "Compose every remaining role — type color, hairlines, states, imagery grade — around "
    "this\nanchor's light; the anchor never overrides an explicit brand commitment, which "
    "wins on\nsight and sends the draw back for a ground that serves it.")


def unit(scope, salt, key):
    """The shared 32-bit draw: sha256(scope:salt:key) → [0, 1]."""
    digest = hashlib.sha256(f"{scope}:{salt}:{key}".encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") / 0xFFFFFFFF


def pool_for(brief_class):
    if brief_class in QUIET_CLASSES:
        return [seed for seed in SEEDS if seed["quiet_safe"]]
    return list(SEEDS)


def draw(key, brief_class):
    pool = pool_for(brief_class)
    # The all-ones digest is the single input that would index past the end.
    return pool[min(len(pool) - 1, math.floor(unit(SCOPE, SALT, key) * len(pool)))]


def report(key, brief_class):
    seed = draw(key, brief_class)
    pool_size = len(pool_for(brief_class))
    return "\n".join([
        f"── ANCHOR ── key={key} brief-class={brief_class} pool={pool_size} → {seed['id']}",
        f"reproduce: python3 {SCRIPT_REL} --from {key} --brief-class {brief_class}",
        "",
        f"material      {seed['material']}",
        f"family        {seed['palette_family']}",
        f"ground        {seed['oklch_ground']}",
        f"accent        {seed['oklch_accent']}",
        f"temperature   {seed['temperature']}",
        f"quiet-safe    {'yes' if seed['quiet_safe'] else 'no'}",
        "",
        COMPOSITION_NOTE,
    ])


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="award-design material anchor — seeded ground/accent draw")
    parser.add_argument("--from", dest="key", default=None,
                        help="hex draw key; omitted, a fresh one is drawn and printed")
    parser.add_argument("--brief-class", dest="brief_class", default=BRIEF_CLASSES[0],
                        choices=BRIEF_CLASSES,
                        help="regulated / quiet filter the pool to its quiet-safe seeds")
    args = parser.parse_args(argv)

    key = args.key or os.urandom(4).hex()
    print(report(key, args.brief_class))
    return 0


if __name__ == "__main__":
    sys.exit(main())
