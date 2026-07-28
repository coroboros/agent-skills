#!/usr/bin/env python3
"""The anti-argmax roll — SHA-256 assignment over the model's own written spines.

A model asked for a direction returns its argmax: the same safe concept every
run, whatever the brief. Prompting around it does not move it — the rut is the
sampler's, not the prompt's. The mechanism that does move it is external and
mechanical: the model WRITES 5-7 candidate spines first, then a hash it does not
control assigns one. The floor is 3 — indexes 1 and 2 are unreachable, because
the top of a self-ranked list IS the argmax and a roll that can return it is a
roll the rut survives. The assignment lands in the padded tail on purpose; the
one-line viability note each spine carries is what keeps the tail buildable.

Determinism is the whole point: the key is printed, the reproduction command is
printed, and anyone can replay the hash offline. Nothing here reads the clock or
draws unseeded randomness — `os.urandom` supplies the default key and nothing
else.

Usage (paths relative to this skill's root):
    python3 scripts/direction_roll.py <spine-count> [--from KEY] [--archetype NAME]
                                      [--reroll N] [--scope direction|surface]

Exit codes: 0 = rolled, 1 = invalid spine count or unknown archetype.
"""

import argparse
import hashlib
import math
import os
import sys
from pathlib import Path

MIN_SPINES = 5
MAX_SPINES = 7
FLOOR = 3

SCRIPT_REL = "scripts/direction_roll.py"
ARCHETYPE_DIR = Path(__file__).resolve().parent.parent / "references" / "archetype"
ARCHETYPES = ("minimalist", "brutalist", "editorial", "bold-maximal",
              "immersive-cinematic", "experimental", "corporate-luxury",
              "bento-card", "spatial-organic")
SCOPES = ("direction", "surface")

SPINE_CONTRACT = (
    "the 5-7 candidate spines must already be WRITTEN under `SPINES:` in the "
    "design_plan\nbefore this ran, one line each with its replayable-moment "
    "viability note; paste this\nstdout verbatim under `SEED:`. Spine {index} is "
    "the assignment, not a suggestion —\ntaste is never grounds for a re-roll, and "
    "a direction the user pinned always wins.")

REROLL_NOTICE = (
    "every direction any earlier roll showed is eliminated. It does not come\n"
    "back reworded, re-scoped, or renamed under a new spine number.")

CHALLENGER_INSTRUCTION = (
    "Fuse each challenger's Spectacle material with the brief's own truth, then "
    "weigh each\nfusion against spine {index} on audience identification and "
    "product clarity. A challenger\nthat wins BOTH becomes the build; one that "
    "wins a single axis loses.")


def unit(scope, salt, key):
    """The shared 32-bit draw: sha256(scope:salt:key) → [0, 1]."""
    digest = hashlib.sha256(f"{scope}:{salt}:{key}".encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") / 0xFFFFFFFF


def roll_index(scope, key, count, reroll):
    salt = f"index:reroll-{reroll}" if reroll else "index"
    # 3 + floor(u * (count - 2)) lands in 3..count for every u < 1; the all-ones
    # digest is the single input that would overshoot, so the top is clamped.
    index = min(count, FLOOR + math.floor(unit(scope, salt, key) * (count - FLOOR + 1)))
    return index, salt


def draw_challengers(scope, key, archetype):
    """Two archetype names off the same hash, excluding the brief's own."""
    pool = [name for name in ARCHETYPES if name != archetype]
    picks = []
    for slot in (1, 2):
        drawn = unit(scope, f"challenger-{slot}", key)
        picks.append(pool.pop(min(len(pool) - 1, math.floor(drawn * len(pool)))))
    return picks


def repro_command(count, key, scope, archetype, reroll):
    parts = [f"python3 {SCRIPT_REL} {count} --from {key} --scope {scope}"]
    if archetype:
        parts.append(f"--archetype {archetype}")
    if reroll:
        parts.append(f"--reroll {reroll}")
    return " ".join(parts)


def archetype_block(archetype):
    if not archetype:
        return ["ARCHETYPE — none named; run again with --archetype to pull its tier-1 DNA."]
    path = ARCHETYPE_DIR / f"{archetype}.md"
    if path.is_file():
        return [f"ARCHETYPE — {archetype} (tier 1)", "", path.read_text(encoding="utf-8").rstrip()]
    return [f"ARCHETYPE — {archetype}: tier-1 file not on disk yet "
            f"(references/archetype/{archetype}.md); read references/{archetype}.md instead."]


def report(count, key, scope, archetype, reroll):
    index, salt = roll_index(scope, key, count, reroll)
    lines = [
        f"── SEED ── key={key} scope={scope} salt={salt} spines={count} "
        f"→ ASSIGNED SPINE {index}",
        f"reproduce: {repro_command(count, key, scope, archetype, reroll)}",
        "",
        "CONTRACT — " + SPINE_CONTRACT.format(index=index),
        "",
    ]
    if reroll:
        lines += [f"REROLL {reroll} — " + REROLL_NOTICE, ""]
    lines += archetype_block(archetype)
    challengers = draw_challengers(scope, key, archetype)
    lines += [
        "",
        "CHALLENGERS — " + " · ".join(challengers),
        CHALLENGER_INSTRUCTION.format(index=index),
        "",
        f"ASSIGNED SPINE {index} of {count} (restated for truncated readers)",
    ]
    return "\n".join(lines)


def parse_count(raw):
    """Spine count or None — the SPINES contract admits 5, 6, or 7 and nothing else."""
    try:
        count = int(raw)
    except ValueError:
        return None
    return count if MIN_SPINES <= count <= MAX_SPINES else None


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="award-design direction roll — SHA-256 assignment over written spines")
    parser.add_argument("spine_count", help=f"how many spines are written ({MIN_SPINES}-{MAX_SPINES})")
    parser.add_argument("--from", dest="key", default=None,
                        help="hex roll key; omitted, a fresh one is drawn and printed")
    parser.add_argument("--archetype", default="", help="the brief's archetype")
    parser.add_argument("--reroll", type=int, default=0,
                        help="reroll number; salts the index and eliminates every direction shown")
    parser.add_argument("--scope", default=SCOPES[0], choices=SCOPES,
                        help="direction = the page's spine, surface = a per-surface draw")
    args = parser.parse_args(argv)

    count = parse_count(args.spine_count)
    if count is None:
        print(f"spine-count must be an integer {MIN_SPINES}-{MAX_SPINES}, got {args.spine_count!r}. "
              f"The SPINES contract is {MIN_SPINES}-{MAX_SPINES} candidate spines written into the "
              f"design_plan BEFORE the roll: fewer than {MIN_SPINES} cannot escape the argmax "
              f"(the floor of {FLOOR} needs a tail), more than {MAX_SPINES} pads with spines no one "
              "would build.", file=sys.stderr)
        return 1
    if args.archetype and args.archetype not in ARCHETYPES:
        print(f"unknown archetype {args.archetype!r}; the nine are: " + ", ".join(ARCHETYPES),
              file=sys.stderr)
        return 1
    if args.reroll < 0:
        print(f"--reroll takes a positive roll number, got {args.reroll}", file=sys.stderr)
        return 1

    key = args.key or os.urandom(4).hex()
    print(report(count, key, args.scope, args.archetype, args.reroll))
    return 0


if __name__ == "__main__":
    sys.exit(main())
