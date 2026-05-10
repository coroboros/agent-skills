#!/usr/bin/env python3
"""Multi-artifact validator for the suno-produce skill.

Auto-dispatches by filename:
  - TRACK.md   → check_track   (Suno v5.5 prompt-bundle validator)
  - ALBUM.md   → check_album   (album/EP concept + tracklist validator)
  - ARTIST.md  → check_artist  (artist-identity + voice-consent validator)

Stdlib only. Python 3.7+.

Usage:
    python3 validate.py path/to/TRACK.md
    python3 validate.py path/to/ALBUM.md
    python3 validate.py path/to/ARTIST.md
    python3 validate.py path/to/album-folder/   # walks **/{TRACK,ALBUM,ARTIST}.md

Exit codes:
    0 — all GREEN
    1 — at least one RED
    2 — at least one YELLOW (no RED)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Common constants
# ─────────────────────────────────────────────────────────────────────────────

RUNNING_SUNO_VERSION = "v5.5"

ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# ─────────────────────────────────────────────────────────────────────────────
# TRACK-specific constants (Suno v5.5 prompt rules)
# ─────────────────────────────────────────────────────────────────────────────

TIER1_TAGS = {
    "intro", "verse", "pre-chorus", "chorus", "post-chorus",
    "bridge", "outro", "instrumental", "final chorus",
}

NUMBERED_TIER1_PREFIXES = ("verse ", "chorus ", "pre-chorus ", "post-chorus ", "bridge ")

TIER3_TAGS = {
    "hook", "drop", "build", "break", "solo",
    "interlude", "refrain", "breakdown",
    "section 1", "section 2", "section 3",
}

SFX_TAGS = {
    "applause", "vinyl crackle", "tape hiss", "gunshot",
    "crowd noise", "siren", "doorbell", "rain", "thunder",
    "phone ring", "footsteps", "explosion", "knock",
}

INLINE_CUE_TAGS = {
    "whispered", "spoken word", "spoken", "belted", "falsetto",
    "harmonized", "layered harmonies", "layered vocals",
    "ad-lib", "ad-libs", "hummed", "shouted", "doubled", "fading",
}

ERA_MARKERS = [
    ("60s", 1960), ("70s", 1970), ("80s", 1980), ("90s", 1990),
    ("2000s", 2000), ("2010s", 2010), ("2020s", 2020),
]

GENRE_KEYWORDS = [
    "indie folk", "indie pop", "alt rock", "post-rock", "post-punk",
    "industrial", "ambient", "drone", "cinematic", "orchestral",
    "trap", "melodic trap", "drill", "hip-hop", "boom bap",
    "synthpop", "synthwave", "dance-pop",
    "house", "techno", "melodic techno", "drum and bass",
    "phonk", "afrobeats", "r&b", "soul", "gospel", "jazz",
    "lo-fi hip-hop", "lo-fi", "shoegaze", "dream pop", "country",
    "americana", "folk", "blues", "metal", "punk", "hardcore",
]

VOCAL_DESCRIPTORS = [
    "male vocal", "female vocal", "male tenor", "female soprano",
    "male baritone", "male bass", "female alto",
    "soft male", "soft female", "raspy male", "breathy female",
    "autotuned vocal", "vocoded vocal", "doubled vocal", "layered vocal",
    "soprano", "alto", "tenor", "baritone",
    "whispered vocal", "spoken vocal", "rapped vocal",
]

# High-confidence citation patterns — explicit intent to reference an artist or
# copyrighted entity. These get RED in both Style and Lyrics. Suno's filter
# strips these phrasings anyway, so the cost of blocking is zero and the legal
# / functional payoff is real (rights exposure, model collapse on average tag).
#
# Whitespace inside each pattern is `[ \t]+` rather than `\s+` so a citation that
# straddles a line break does not capture the next line's text into the issue
# value (a non-bug for verdict, but the issue/fix message would otherwise leak
# the cross-line content). Multi-word capture group also uses `[ \t]+`.
#
# Known tolerable false-positive surfaces:
# - `\b[àa][ \t]+la[ \t]+<Capitalized>` will fire on culinary phrases like
#   `à la King`, `a la Russe`. Real-world rate inside Suno prompts is near zero
#   and the user can rephrase as `à la mode` (lowercase) or remove the descriptor.
# - The possessive pattern `<Name>'s sound|style|voice|era|...` requires the
#   name to be at least TWO words. Single-word possessives like `London's sound`
#   or `Spring's sound` would have fired RED on a pure `[A-Z][\w-]+` form; the
#   `(?:[ \t]+[A-Z][\w-]+){1,2}` quantifier (1-2 trailing words, not 0-2) raises
#   the bar. Real artist names are almost always multi-word; single-word artist
#   names (`Madonna`, `Drake`) get caught by the other four patterns regardless.
ARTIST_CITATION_PATTERNS = (
    re.compile(r"\bin[ \t]+(?:the[ \t]+)?style[ \t]+of[ \t]+([A-Z][\w'-]+(?:[ \t]+[A-Z][\w'-]+){0,2})", re.UNICODE),
    re.compile(r"\bsounds?[ \t]+like[ \t]+([A-Z][\w'-]+(?:[ \t]+[A-Z][\w'-]+){0,2})", re.UNICODE),
    re.compile(r"\bvoice[ \t]+(?:of|like)[ \t]+([A-Z][\w'-]+(?:[ \t]+[A-Z][\w'-]+){0,2})", re.UNICODE),
    re.compile(r"\b[àa][ \t]+la[ \t]+([A-Z][\w'-]+(?:[ \t]+[A-Z][\w'-]+){0,2})", re.UNICODE),
    re.compile(r"\b([A-Z][\w-]+(?:[ \t]+[A-Z][\w-]+){1,2})['’]s[ \t]+(?:sound|style|voice|era|track|hit|catalog)\b", re.UNICODE),
)

# Title-case proper-noun pairs in Style — generic flag for "looks like an artist
# name". YELLOW because false positives (legitimate Suno descriptors capitalized
# by users) are common. The whitelist covers the canonical instruments, drums,
# textures, and production-pipeline terms that real Suno prompts use. New entries
# go here when a real prompt produces a false positive.
NON_ARTIST_PHRASES = {
    # Existing baseline
    "Drum Bass", "Hip Hop", "Lo Fi", "Boom Bap", "Pedal Steel",
    "Dance Pop", "Synth Pop", "Drum And", "Drill And", "Wood Block",
    "Half Time", "Half-Time", "Stereo Wide", "Wide Stereo",
    "Plate Reverb", "Spring Reverb", "Tape Hiss", "Vinyl Crackle",
    "Sub Bass", "808 Sub", "Acoustic Guitar", "Electric Guitar",
    "Upright Bass", "Brushed Drums", "Female Vocal", "Male Vocal",
    "Close Mic", "Room Mic",
    # Drums and percussion
    "Snare Drum", "Bass Drum", "Hi Hat", "Hi-Hat", "Floor Tom", "Tom Fill",
    "Crash Cymbal", "Ride Cymbal", "Drum Kit", "Drum Machine", "Drum Loop",
    "Drum Pad", "Brush Drums", "Brushed Snare",
    # Bass
    "Slap Bass", "Walking Bass", "Fretless Bass", "Synth Bass",
    # Synth and lead
    "Lead Synth", "Synth Lead", "Synth Pad", "Pad Wash", "Analog Synth",
    "Sub Drop", "Bass Drop",
    # Vocal forms
    "Lead Vocal", "Backing Vocal", "Vocal Chop", "Vocal Loop", "Vocal Stack",
    "Harmony Stack", "Choral Stack",
    # Guitar
    "Lead Guitar", "Rhythm Guitar", "Slide Guitar", "Steel Guitar",
    "Bass Guitar", "Twelve String", "Twelve-String", "Nylon String",
    "Classical Guitar",
    # Effects and processing
    "Tape Echo", "Tape Saturation", "Tape Wobble", "Slap Back", "Slap-Back",
    "Reverb Tail", "Delay Tail", "Spring Echo", "Plate Echo", "Stereo Field",
    "Wide Pan", "Side Chain", "Side-Chain", "Sidechain Pump",
    # Two-word genres in title case (rare but legitimate when users capitalize)
    "French House", "Trip Hop", "Indie Pop", "Indie Rock", "Pop Rock",
    "Pop Punk", "Folk Pop", "Folk Rock", "Power Pop", "Soft Rock",
    "Hard Rock", "Glam Rock", "Prog Rock", "Post Rock", "Math Rock",
    "Surf Rock", "Garage Rock", "Punk Rock", "Acid House", "Deep House",
    "Tech House", "Big Band", "Doo Wop", "Future Bass", "Drum Loop",
}

# Inline-cue keywords that justify a non-canonical bracket as
# instrumentation / texture / production / performance — the dominant Suno v5.5
# bracket idiom (see references/style-and-lyrics.md § Stacking metatags inside
# sections). Generous on purpose: false positive on a real cue is worse than
# false negative on an adversarial bracket.
INLINE_CUE_KEYWORDS = (
    "guitar", "drum", "bass", "synth", "piano", "string", "808", "kick", "hat",
    "crash", "pad", "lead", "horn", "brass", "wood", "rhodes", "organ",
    "snare", "tom", "ride", "tambourine", "shaker", "percussion", "cello",
    "violin", "viola", "harp", "banjo", "mandolin", "fiddle", "harmonica",
    "mic", "reverb", "delay", "echo", "phaser", "flanger", "chorus effect",
    "saturation", "compression", "distortion", "sidechain", "wobble",
    "filtered", "muted", "gated",
    "acoustic", "electric", "fingerpicked", "strummed", "plucked", "bowed",
    "clean", "saturated", "analog", "digital", "dry", "wet",
    "metallic", "sparse", "wide", "narrow", "warm", "cold", "hollow",
    "tape", "vinyl", "lo-fi", "hi-fi", "compressed",
    "vocal", "harmonies", "harmony", "chop", "loop", "sample", "stab",
    "intensity", "stripped", "building", "fading", "soaring", "rising",
    "drop", "evolving", "granular", "swell", "drone", "arp", "arpeggio",
)

# ─────────────────────────────────────────────────────────────────────────────
# ALBUM-specific constants
# ─────────────────────────────────────────────────────────────────────────────

ALBUM_VALID_FORMATS = {"EP", "Album", "Mixtape", "Single"}
ALBUM_REQUIRED_SECTIONS = ["Concept", "Arc", "Tracklist", "Transitions"]
ALBUM_ARC_REQUIRED_LABELS = ["Opening", "Development", "Climax", "Closing"]

# ─────────────────────────────────────────────────────────────────────────────
# ARTIST-specific constants
# ─────────────────────────────────────────────────────────────────────────────

ARTIST_VALID_RIGHTS_POSTURES = {"license-only", "licensed", "public-domain", "unknown"}
ARTIST_REQUIRED_SECTIONS = [
    "Artist identity",
    "Voice and Custom Model",
    "Recurring instrumentation",  # match the section header start, not the full title
    "Rights posture",
]


# ─────────────────────────────────────────────────────────────────────────────
# Frontmatter parser — supports inline lists, block-form nested mappings
# ─────────────────────────────────────────────────────────────────────────────

def parse_value(val):
    """Parse a YAML scalar / inline list value."""
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        return val[1:-1]
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        return [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
    if val.lower() in ("null", "none", "~", ""):
        return None
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        pass
    return val


def parse_frontmatter(text):
    """Parse YAML-ish frontmatter. Returns (dict | None, body_str, fm_line_count).

    Handles the restricted schema this skill uses:
    - top-level scalar key: value
    - top-level inline list key: [a, b, c]
    - top-level null / none / ~ / empty → None
    - block-form nested mapping (one level deep — sufficient for slider_bias)

    Does NOT support: block-form lists, deeply nested mappings, anchors/aliases.
    """
    if not text.startswith("---\n"):
        return None, text, 0
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text, 0
    fm_text = text[4:end]
    body = text[end + 5:]
    fm_line_count = fm_text.count("\n") + 3

    fm = {}
    current_parent = None  # active block-mapping parent key

    for raw_line in fm_text.splitlines():
        rstripped = raw_line.rstrip()
        if not rstripped or rstripped.lstrip().startswith("#"):
            continue
        stripped = raw_line.lstrip()
        indent = len(raw_line) - len(stripped)
        if ":" not in stripped:
            continue
        key, _, val = stripped.partition(":")
        key = key.strip()
        val = val.strip()

        if indent > 0 and current_parent is not None:
            if not isinstance(fm.get(current_parent), dict):
                fm[current_parent] = {}
            fm[current_parent][key] = parse_value(val)
            continue

        if val == "":
            # Possibly a block-mapping parent — open a nested dict and track it.
            current_parent = key
            fm[key] = {}
        else:
            current_parent = None
            fm[key] = parse_value(val)

    return fm, body, fm_line_count


# ─────────────────────────────────────────────────────────────────────────────
# Body section helpers
# ─────────────────────────────────────────────────────────────────────────────

def find_fenced_section(body, heading_regex):
    """Find the first fenced text block under a Markdown heading matching `heading_regex`.

    Returns (content_str | None, content_start_line_in_body | None).
    """
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if re.match(heading_regex, line, re.IGNORECASE):
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("```"):
                    for k in range(j + 1, len(lines)):
                        if lines[k].startswith("```"):
                            content = "\n".join(lines[j + 1:k])
                            return content, j + 2
                    break
    return None, None


def find_section(body, heading_regex):
    """Find a Markdown section by its `## Heading` line. Returns (lines_in_section, start_line_in_body)."""
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if re.match(heading_regex, line, re.IGNORECASE):
            section_lines = []
            for j in range(i + 1, len(lines)):
                if re.match(r"^##\s+", lines[j]):
                    break
                section_lines.append(lines[j])
            return section_lines, i + 1
    return None, None


# ─────────────────────────────────────────────────────────────────────────────
# TRACK.md helpers
# ─────────────────────────────────────────────────────────────────────────────

def count_descriptors(style_text):
    if not style_text:
        return 0
    return len([d.strip() for d in style_text.split(",") if d.strip()])


def find_brackets(text):
    out = []
    for line_idx, line in enumerate(text.splitlines()):
        for match in re.finditer(r"\[([^\]]+)\]", line):
            tag = match.group(1).strip().lower()
            out.append((tag, line_idx + 1))
    return out


def is_canonical_tier1(tag_lower):
    if tag_lower in TIER1_TAGS:
        return True
    for prefix in NUMBERED_TIER1_PREFIXES:
        if tag_lower.startswith(prefix) and tag_lower[len(prefix):].strip().isdigit():
            return True
    return False


def looks_like_inline_cue(tag_lower):
    if "," in tag_lower:
        return True
    return any(kw in tag_lower for kw in INLINE_CUE_KEYWORDS)


def find_citation_matches(text):
    """Return list of (pattern_phrase, captured_name, in_text_offset) for any
    artist-citation pattern hit in `text`. The caller resolves line numbers
    against the surrounding section.
    """
    hits = []
    for rx in ARTIST_CITATION_PATTERNS:
        for m in rx.finditer(text):
            phrase = m.group(0)
            name = m.group(1) if m.lastindex else phrase
            hits.append((phrase, name, m.start()))
    return hits


def offset_to_line(text, offset):
    """1-indexed line number of `offset` inside `text`."""
    return text.count("\n", 0, offset) + 1


def parse_sliders(body):
    """Find numeric slider values under `## Sliders`. Strips `**` and `__` markdown
    emphasis before matching so `- **Weirdness**: 40` parses cleanly. Returns a
    list of (name, value, line_in_body)."""
    out = []
    lines = body.splitlines()
    in_sliders = False
    for i, line in enumerate(lines):
        if re.match(r"^##\s+Sliders\s*$", line):
            in_sliders = True
            continue
        if in_sliders:
            if line.startswith("## "):
                break
            clean = line.replace("**", "").replace("__", "")
            m = re.search(
                r"\b(weirdness|style\s*influence|audio\s*influence|styleweight|audioweight|weirdnessconstraint)\b"
                r"\s*[:=]?\s*(\d+(?:\.\d+)?)",
                clean, re.IGNORECASE,
            )
            if m:
                out.append((m.group(1), float(m.group(2)), i + 1))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Verdict helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_report(file_path, errors, warnings, info):
    if errors:
        verdict = "RED"
    elif warnings:
        verdict = "YELLOW"
    else:
        verdict = "GREEN"
    return {
        "verdict": verdict,
        "file": str(file_path),
        "errors": errors,
        "warnings": warnings,
        "info": info,
    }


def missing_frontmatter_report(file_path):
    return make_report(
        file_path,
        errors=[{
            "check": "frontmatter",
            "line": 1,
            "value": "missing",
            "expected": "YAML frontmatter delimited by `---`",
            "fix": "Add `---` frontmatter at the top of the file",
        }],
        warnings=[],
        info=[],
    )


# ─────────────────────────────────────────────────────────────────────────────
# TRACK.md validator
# ─────────────────────────────────────────────────────────────────────────────

def check_track(path):
    text = Path(path).read_text(encoding="utf-8")
    fm, body, fm_offset = parse_frontmatter(text)
    if fm is None:
        return missing_frontmatter_report(path)

    errors = []
    warnings = []
    info = []

    sv = fm.get("suno_version")
    info.append({"check": "suno_version", "value": sv, "running": RUNNING_SUNO_VERSION})
    if sv and sv != RUNNING_SUNO_VERSION:
        warnings.append({
            "check": "suno_version_mismatch",
            "line": 2,
            "value": sv,
            "expected": RUNNING_SUNO_VERSION,
            "fix": f"Re-validate against {RUNNING_SUNO_VERSION} or run the future `migrate` verb",
        })

    title = fm.get("title", "")
    if not isinstance(title, str) or not title:
        errors.append({
            "check": "title_required",
            "line": 3,
            "value": title,
            "expected": "non-empty string",
            "fix": "Set `title:` in frontmatter",
        })
    elif len(title) > 100:
        errors.append({
            "check": "title_length",
            "line": 3,
            "value": len(title),
            "expected": "≤ 100",
            "fix": f"Shorten title by {len(title) - 100} chars",
        })

    style, style_line = find_fenced_section(body, r"^###\s+Style of Music\s*$")
    lyrics, lyrics_line = find_fenced_section(body, r"^###\s+Lyrics\s*$")
    exclude, exclude_line = find_fenced_section(body, r"^###\s+Exclude Styles\s*$")

    if style is None:
        errors.append({
            "check": "missing_section",
            "line": fm_offset,
            "value": "no Style of Music block",
            "expected": "fenced ### Style of Music block",
            "fix": "Add a fenced `### Style of Music` section",
        })
    else:
        style_file_line = fm_offset + style_line
        if len(style) > 1000:
            errors.append({
                "check": "style_length",
                "line": style_file_line,
                "value": len(style),
                "expected": "≤ 1000",
                "fix": f"Trim Style by {len(style) - 1000} chars",
            })
        desc_count = count_descriptors(style)
        if desc_count < 4 or desc_count > 7:
            warnings.append({
                "check": "descriptor_count",
                "line": style_file_line,
                "value": desc_count,
                "expected": "4–7",
                "fix": "Adjust Style descriptor count (genre + era + mood + instruments + vocal direction)",
            })
        style_lower = style.lower()
        genres_found = sorted({g for g in GENRE_KEYWORDS if g in style_lower})
        primaries = [g for g in genres_found if not any(g != g2 and g in g2 for g2 in genres_found)]
        if len(primaries) > 2:
            warnings.append({
                "check": "genre_count",
                "line": style_file_line,
                "value": primaries,
                "expected": "≤ 2",
                "fix": "Reduce to one or two primary genres; reinforce with mood and instrumentation",
            })
        eras_in_style = [(marker, year) for marker, year in ERA_MARKERS if marker in style_lower]
        if len(eras_in_style) > 1:
            year_min = min(y for _, y in eras_in_style)
            year_max = max(y for _, y in eras_in_style)
            if year_max - year_min >= 30:
                warnings.append({
                    "check": "conflicting_eras",
                    "line": style_file_line,
                    "value": [m for m, _ in eras_in_style],
                    "expected": "single coherent era",
                    "fix": "Pick one era; the model averages between them and produces a period-incoherent mix",
                })
        if fm.get("voice_profile"):
            for vd in VOCAL_DESCRIPTORS:
                if vd in style_lower:
                    warnings.append({
                        "check": "voice_attached_vocal_descriptor",
                        "line": style_file_line,
                        "value": vd,
                        "expected": "no vocal descriptors when Voice attached",
                        "fix": f"Remove `{vd}` from Style — it conflicts with the cloned Voice and produces blended timbre",
                    })
                    break
        # Citation patterns ("in the style of X", "voice of X", "à la X",
        # "X's sound") are high-confidence intent — RED. Suno filters these
        # phrasings; using them creates rights exposure for zero functional
        # benefit. Article §5.1.5 anti-pattern; Rules § "Describe the sound,
        # never an artist".
        for phrase, _name, off in find_citation_matches(style):
            errors.append({
                "check": "artist_citation_in_style",
                "line": style_file_line + offset_to_line(style, off) - 1,
                "value": phrase,
                "expected": "describe the sonic fingerprint, not artist or copyrighted citations",
                "fix": (
                    f"Remove `{phrase}` — Suno filters/ignores artist citations and you "
                    "carry rights exposure for nothing. Translate to sound: era + "
                    "production texture + vocal timbre (e.g., \"late-90s post-grunge, "
                    "raspy male belt, dry close-mic\")."
                ),
            })
        # Title-case proper-noun pairs in Style — generic flag. Whitelisted
        # phrases skip; everything else gets YELLOW (false positives are common
        # so we warn rather than block).
        artist_candidates = re.findall(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", style)
        flagged = [c for c in artist_candidates if c not in NON_ARTIST_PHRASES]
        if flagged:
            warnings.append({
                "check": "artist_name_in_style",
                "line": style_file_line,
                "value": flagged,
                "expected": "describe the sonic fingerprint, not artist names",
                "fix": (
                    "Replace artist-name candidates with sound-fingerprint descriptors. "
                    "Reasons: (1) legal — artist names in prompts create rights exposure; "
                    "(2) functional — Suno filters or ignores them and the model collapses "
                    "to an averaged tag. Use era + texture + vocal timbre instead."
                ),
            })

    if lyrics is not None:
        lyrics_file_line = fm_offset + lyrics_line
        if len(lyrics) > 5000:
            errors.append({
                "check": "lyrics_length",
                "line": lyrics_file_line,
                "value": len(lyrics),
                "expected": "≤ 5000",
                "fix": f"Trim Lyrics by {len(lyrics) - 5000} chars",
            })
        bpm_match = re.search(r"\b\d{2,3}\s*bpm\b", lyrics, re.IGNORECASE)
        if bpm_match:
            match_line_in_section = lyrics[:bpm_match.start()].count("\n") + 1
            errors.append({
                "check": "bpm_in_lyrics",
                "line": lyrics_file_line + match_line_in_section - 1,
                "value": bpm_match.group(0),
                "expected": "BPM in Style of Music field, never in Lyrics",
                "fix": "Move BPM specification to the Style of Music field",
            })
        # Citation patterns also apply to Lyrics — Suno's filter scrubs
        # artist citations from either field, and a citation written as a
        # lyric still creates rights exposure.
        for phrase, _name, off in find_citation_matches(lyrics):
            errors.append({
                "check": "artist_citation_in_lyrics",
                "line": lyrics_file_line + offset_to_line(lyrics, off) - 1,
                "value": phrase,
                "expected": "describe the sonic fingerprint, not artist or copyrighted citations",
                "fix": (
                    f"Remove `{phrase}` — Suno filters/ignores artist citations even "
                    "inside the Lyrics field. Rewrite as a description (era, mood, "
                    "delivery) or remove the line."
                ),
            })
        for tag, in_section_line in find_brackets(lyrics):
            file_line = lyrics_file_line + in_section_line - 1
            if tag in SFX_TAGS:
                errors.append({
                    "check": "sfx_bracket_tag",
                    "line": file_line,
                    "value": f"[{tag}]",
                    "expected": "no SFX bracket tags",
                    "fix": (
                        f"Remove [{tag}] — SFX brackets are unreliable in v5/v5.5. "
                        "Generate ambience in Suno Sounds and layer in Studio."
                    ),
                })
            elif tag in INLINE_CUE_TAGS or is_canonical_tier1(tag):
                continue
            elif tag in TIER3_TAGS:
                warnings.append({
                    "check": "tier3_bracket_tag",
                    "line": file_line,
                    "value": f"[{tag}]",
                    "expected": "Tier 1 canonical structural tags",
                    "fix": (
                        f"[{tag}] is community-validated but inconsistent — prefer Tier 1 "
                        "([Verse], [Chorus], [Bridge], etc.) when possible"
                    ),
                })
            elif looks_like_inline_cue(tag):
                continue
            else:
                warnings.append({
                    "check": "unrecognized_bracket_tag",
                    "line": file_line,
                    "value": f"[{tag}]",
                    "expected": "Tier 1 structural tag or recognised inline cue",
                    "fix": (
                        f"[{tag}] is not in the canonical metatag set — Suno may sing it as a "
                        "lyric or ignore it"
                    ),
                })

    if exclude is not None:
        exclude_file_line = fm_offset + exclude_line
        excludes = [e.strip() for e in exclude.split(",") if e.strip()]
        if len(excludes) > 3:
            warnings.append({
                "check": "exclude_count",
                "line": exclude_file_line,
                "value": len(excludes),
                "expected": "≤ 3",
                "fix": "Cap exclusions at three; positives define, negatives refine",
            })

    for slider_name, value, line_in_body in parse_sliders(body):
        if value < 0 or value > 100:
            errors.append({
                "check": "slider_range",
                "line": fm_offset + line_in_body,
                "value": value,
                "expected": "0–100 (UI percentage) or 0.00–1.00 (API float)",
                "fix": f"Bring {slider_name.strip()} into range",
            })

    return make_report(path, errors, warnings, info)


# ─────────────────────────────────────────────────────────────────────────────
# ALBUM.md validator
# ─────────────────────────────────────────────────────────────────────────────

TRACKLIST_LINE_RE = re.compile(
    r"^\s*\d+\.\s+.+?\s+—\s+\d+\s*BPM\s+—\s+.+?\s+—\s+.+$",
    re.IGNORECASE,
)


def check_album(path):
    text = Path(path).read_text(encoding="utf-8")
    fm, body, fm_offset = parse_frontmatter(text)
    if fm is None:
        return missing_frontmatter_report(path)

    errors = []
    warnings = []
    info = []

    title = fm.get("title")
    if not isinstance(title, str) or not title:
        errors.append({
            "check": "title_required",
            "line": 2,
            "value": title,
            "expected": "non-empty string",
            "fix": "Set `title:` in frontmatter",
        })
    elif len(title) > 100:
        errors.append({
            "check": "title_length",
            "line": 2,
            "value": len(title),
            "expected": "≤ 100",
            "fix": f"Shorten title by {len(title) - 100} chars",
        })

    release_format = fm.get("release_format")
    if release_format and release_format not in ALBUM_VALID_FORMATS:
        errors.append({
            "check": "release_format",
            "line": 5,
            "value": release_format,
            "expected": " | ".join(sorted(ALBUM_VALID_FORMATS)),
            "fix": f"Set `release_format:` to one of: {', '.join(sorted(ALBUM_VALID_FORMATS))}",
        })

    created = fm.get("created")
    if created and isinstance(created, str) and not ISO_DATE_RE.match(created):
        warnings.append({
            "check": "created_format",
            "line": 6,
            "value": created,
            "expected": "ISO date YYYY-MM-DD",
            "fix": "Use ISO date format in `created:`",
        })

    # Required sections
    for section_name in ALBUM_REQUIRED_SECTIONS:
        section_lines, _ = find_section(body, rf"^##\s+{re.escape(section_name)}\s*$")
        if section_lines is None:
            errors.append({
                "check": "missing_section",
                "line": fm_offset,
                "value": section_name,
                "expected": f"## {section_name} section",
                "fix": f"Add a `## {section_name}` section",
            })

    # Arc section sanity — should mention all four arc labels
    arc_lines, arc_start = find_section(body, r"^##\s+Arc\s*$")
    if arc_lines is not None:
        arc_text = "\n".join(arc_lines).lower()
        for label in ALBUM_ARC_REQUIRED_LABELS:
            if label.lower() not in arc_text:
                warnings.append({
                    "check": "arc_label_missing",
                    "line": fm_offset + arc_start,
                    "value": label,
                    "expected": "all four labels (Opening / Development / Climax / Closing)",
                    "fix": f"Add a `- {label}: ...` line to the Arc section",
                })

    # Tracklist consistency
    tracklist_lines, tracklist_start = find_section(body, r"^##\s+Tracklist\s*$")
    tracklist_count = 0
    if tracklist_lines is not None:
        for line in tracklist_lines:
            if line.strip() and re.match(r"^\s*\d+\.", line):
                tracklist_count += 1
                if not TRACKLIST_LINE_RE.match(line.strip()):
                    warnings.append({
                        "check": "tracklist_line_format",
                        "line": fm_offset + tracklist_start,
                        "value": line.strip(),
                        "expected": "`nn. Title — BPM — key — feel`",
                        "fix": "Use the canonical tracklist line shape",
                    })

        declared_count = fm.get("track_count")
        if isinstance(declared_count, int) and declared_count != tracklist_count:
            errors.append({
                "check": "track_count_mismatch",
                "line": 4,
                "value": f"frontmatter={declared_count}, tracklist={tracklist_count}",
                "expected": "track_count matches tracklist line count",
                "fix": f"Set `track_count: {tracklist_count}` or adjust the tracklist",
            })

    info.append({"check": "tracklist_count", "value": tracklist_count, "running": "actual"})

    return make_report(path, errors, warnings, info)


# ─────────────────────────────────────────────────────────────────────────────
# ARTIST.md validator
# ─────────────────────────────────────────────────────────────────────────────

def check_artist(path):
    text = Path(path).read_text(encoding="utf-8")
    fm, body, fm_offset = parse_frontmatter(text)
    if fm is None:
        return missing_frontmatter_report(path)

    errors = []
    warnings = []
    info = []

    artist = fm.get("artist")
    if not isinstance(artist, str) or not artist:
        errors.append({
            "check": "artist_required",
            "line": 2,
            "value": artist,
            "expected": "non-empty string",
            "fix": "Set `artist:` in frontmatter",
        })

    voice_profile = fm.get("voice_profile")
    voice_consent = fm.get("voice_consent")
    if voice_profile:
        if not voice_consent:
            errors.append({
                "check": "voice_consent_required",
                "line": 4,
                "value": voice_consent,
                "expected": "voice_consent declared when voice_profile is set",
                "fix": (
                    'Set `voice_consent:` to one of: "self", '
                    '"licensed: <source>", "public-domain: <source>"'
                ),
            })
        else:
            valid_consent = (
                voice_consent == "self"
                or voice_consent.startswith("licensed:")
                or voice_consent.startswith("public-domain:")
            )
            if not valid_consent:
                warnings.append({
                    "check": "voice_consent_format",
                    "line": 4,
                    "value": voice_consent,
                    "expected": '"self" | "licensed: <source>" | "public-domain: <source>"',
                    "fix": "Use one of the canonical consent forms",
                })

    custom_model = fm.get("custom_model")
    custom_model_training_set = fm.get("custom_model_training_set")
    if custom_model and not custom_model_training_set:
        warnings.append({
            "check": "custom_model_training_set_recommended",
            "line": 6,
            "value": custom_model_training_set,
            "expected": "training-set posture declared when custom_model is set",
            "fix": (
                'Set `custom_model_training_set:` to one of: "self-authored", '
                '"licensed: <source>"'
            ),
        })

    rights_posture = fm.get("rights_posture")
    if rights_posture and rights_posture not in ARTIST_VALID_RIGHTS_POSTURES:
        warnings.append({
            "check": "rights_posture_format",
            "line": 9,
            "value": rights_posture,
            "expected": " | ".join(sorted(ARTIST_VALID_RIGHTS_POSTURES)),
            "fix": f"Use one of: {', '.join(sorted(ARTIST_VALID_RIGHTS_POSTURES))}",
        })

    slider_bias = fm.get("slider_bias")
    if isinstance(slider_bias, dict):
        for k, v in slider_bias.items():
            if v is None:
                continue
            try:
                fv = float(v)
            except (TypeError, ValueError):
                warnings.append({
                    "check": "slider_bias_value",
                    "line": 8,
                    "value": f"{k}={v!r}",
                    "expected": "numeric (0–100 percentage or 0.00–1.00 float)",
                    "fix": f"Use a number for slider_bias.{k}",
                })
                continue
            if fv < 0 or fv > 100:
                errors.append({
                    "check": "slider_bias_range",
                    "line": 8,
                    "value": f"{k}={fv}",
                    "expected": "0–100 (UI percentage) or 0.00–1.00 (API float)",
                    "fix": f"Bring slider_bias.{k} into range",
                })

    created = fm.get("created")
    if created and isinstance(created, str) and not ISO_DATE_RE.match(created):
        warnings.append({
            "check": "created_format",
            "line": 10,
            "value": created,
            "expected": "ISO date YYYY-MM-DD",
            "fix": "Use ISO date format in `created:`",
        })

    # Required sections — match by section-header start so users can have
    # variant headings (e.g., "Recurring instrumentation and texture").
    for needle in ARTIST_REQUIRED_SECTIONS:
        section_lines, _ = find_section(body, rf"^##\s+{re.escape(needle)}.*$")
        if section_lines is None:
            errors.append({
                "check": "missing_section",
                "line": fm_offset,
                "value": needle,
                "expected": f"`## {needle}…` section",
                "fix": f"Add a `## {needle}` section",
            })

    info.append({"check": "voice_profile", "value": voice_profile, "running": "declared"})
    info.append({"check": "custom_model", "value": custom_model, "running": "declared"})

    return make_report(path, errors, warnings, info)


# ─────────────────────────────────────────────────────────────────────────────
# Dispatch
# ─────────────────────────────────────────────────────────────────────────────

def detect_artifact_type(path):
    """Pick a validator by filename. Returns 'track' | 'album' | 'artist' | None."""
    name = Path(path).name.upper()
    if name == "TRACK.MD":
        return "track"
    if name == "ALBUM.MD":
        return "album"
    if name == "ARTIST.MD":
        return "artist"
    return None


def check_file(path):
    kind = detect_artifact_type(path)
    if kind == "track":
        return check_track(path)
    if kind == "album":
        return check_album(path)
    if kind == "artist":
        return check_artist(path)
    return {
        "verdict": "RED",
        "file": str(path),
        "errors": [{
            "check": "unsupported_filename",
            "line": 0,
            "value": Path(path).name,
            "expected": "TRACK.md | ALBUM.md | ARTIST.md",
            "fix": "Rename to one of the canonical filenames or pass a directory to walk",
        }],
        "warnings": [],
        "info": [],
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def collect_files(target):
    if target.is_file():
        return [target]
    if target.is_dir():
        files = []
        for name in ("TRACK.md", "ALBUM.md", "ARTIST.md"):
            files.extend(sorted(target.rglob(name)))
        return sorted(set(files))
    return []


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Validate Suno v5.5 production artifacts (TRACK.md / ALBUM.md / ARTIST.md). "
            "Auto-dispatches by filename."
        ),
    )
    parser.add_argument("path", help="Path to a single artifact file or a directory to walk")
    args = parser.parse_args()

    target = Path(args.path)
    if not target.exists():
        print(json.dumps({"error": f"path not found: {target}"}, indent=2), file=sys.stderr)
        sys.exit(1)

    files = collect_files(target)
    if not files:
        print(
            json.dumps({"error": f"no TRACK.md/ALBUM.md/ARTIST.md found under {target}"}, indent=2),
            file=sys.stderr,
        )
        sys.exit(1)

    reports = [check_file(f) for f in files]

    if len(reports) == 1:
        print(json.dumps(reports[0], indent=2))
    else:
        print(json.dumps({
            "summary": {
                "total": len(reports),
                "green": sum(1 for r in reports if r["verdict"] == "GREEN"),
                "yellow": sum(1 for r in reports if r["verdict"] == "YELLOW"),
                "red": sum(1 for r in reports if r["verdict"] == "RED"),
            },
            "reports": reports,
        }, indent=2))

    has_red = any(r["verdict"] == "RED" for r in reports)
    has_yellow = any(r["verdict"] == "YELLOW" for r in reports)
    if has_red:
        sys.exit(1)
    if has_yellow:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
