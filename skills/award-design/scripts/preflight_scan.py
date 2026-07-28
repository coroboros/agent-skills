#!/usr/bin/env python3
"""Deterministic anti-slop scanner — award-design pre-flight, Phase 5.

Scans built frontend sources for countable AI-design tells. Heuristic by
design: it catches, it never clears — a clean run ticks no pre-flight box.
Line-based matching keeps rules cheap and auditable; multi-line constructs
(an `<img>` split across lines) may escape a rule, which is the accepted
trade-off: false negatives over false positives. Two rules honor that bias
structurally: EMDASH fires on density (> ~1 per 100 visible words, min 3),
never on a single legitimate dash; H1-COUNT / MAIN-LANDMARK skip near-empty
documents so an SPA shell rendering from JS is not a false fail. FONT-COUNT
is project-level: it counts distinct first families across stylesheets
(fallback stacks count as one) and flags past 3 families + 1 mono outlier.
COPY-LANG is per-file density: it fires only past 4 distinct + 6 total
non-English function words in a file's visible text, so a register device
("Maison"), a "Des Moines", or an AUX label never trips it; its month
channel fires at 2 distinct non-English month names — date chrome is the
cheapest bleed vector and a closed vocabulary. The OPTICAL-* family reads
the craft pass back off the stylesheet (REVIEW-only) and stays silent unless
the project is a real built page — a stylesheet with no document, or a
document with no stylesheet, has no craft pass to have skipped.

Usage:
    python3 preflight_scan.py <path> [<path>...] [--archetype NAME]

`--archetype` applies declared archetype grammar: editorial and
corporate-luxury suppress EMDASH (a deliberate typographic choice there);
brutalist suppresses META-LABEL (ASCII process flags are its register).

Exit codes: 0 = no FAIL findings, 1 = FAIL findings present, 2 = usage error
or zero files scanned (a wrong path must never read as a clean build).
"""

import argparse
import json
import math
import re
import struct
import sys
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

FAIL = "FAIL"
REVIEW = "REVIEW"

# Text-bearing sources (visible copy + markup) vs all scannable sources.
TEXT_EXTS = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro", ".mdx", ".md"}
CODE_EXTS = TEXT_EXTS | {".js", ".ts", ".css", ".scss"}
EXCLUDED_DIRS = {"node_modules", ".git", ".next", ".astro", "coverage", "vendor", "__pycache__",
                 "dist", "build", ".output", ".nuxt", ".svelte-kit", ".vercel"}

# Vendor engines (three/lenis/gsap bundles, vendor/ trees) are not build-
# authored surface — per-file rules skip them; their text stays in the project
# blob so guard detection (REDUCED-MOTION, :focus-visible) still sees them.
VENDOR_NAME_RE = re.compile(r"^(?:three|lenis|gsap)[.\-]", re.IGNORECASE)


def _is_vendor(path):
    return (any(part.lower() == "vendor" for part in path.parts)
            or bool(VENDOR_NAME_RE.match(path.name)))

# ── Tooling gates — static proxies (REVIEW-only: a proxy never FAILs on a guess) ──
# EASE-OVERSHOOT: the page runs ONE declared motion register (decelerating-
# mechanical, playful-elastic, or cinematic — the effect-grammar verdict). The
# scanner cannot read the DESIGN.md (excluded), so it names every overshoot/
# elastic curve in build code for the reviewer to judge against the declared
# register.
EASE_RULE_ID = "EASE-OVERSHOOT"
EASE_EXTS = {".js", ".mjs", ".html", ".htm", ".css", ".scss"}
CUBIC_BEZIER_RE = re.compile(
    r"cubic-bezier\(\s*(-?\d*\.?\d+)\s*,\s*(-?\d*\.?\d+)\s*,"
    r"\s*(-?\d*\.?\d+)\s*,\s*(-?\d*\.?\d+)\s*\)")
# Closed vocabulary: GSAP's spring-family eases + the framer-motion spring type.
SPRING_TOKEN_RE = re.compile(
    r"\b(?:elastic|back|bounce)\.(?:inOut|in|out)\b|\btype:\s*['\"]spring['\"]")
EASE_DESCRIPTION = (
    "overshoot/elastic easing in build code — the page declares ONE motion register; "
    "the scanner cannot read the DESIGN.md, so judge each named curve against the "
    "declared register (interaction-signatures.md)")


def _bezier_character(y1, y2):
    over = y1 > 1 or y2 > 1
    under = y1 < 0 or y2 < 0
    if over and under:
        return "elastic (winds up, then overshoots)"
    if over:
        return "overshoot (travels past the target before settling)"
    return "anticipation (pulls back before the travel)"


# IMG-NATIVE-RES: shipped-dims-vs-layout — the CALDERA defect (1280×720 frames
# rendered up to 2880×1800 device px behind a self-graded asset table). Rendered
# width is unknowable without a browser, so the floor rides layout signals — a
# `sizes` attribute (slot computed at the 1920 audit ceiling), cover-fit CSS,
# a full-bleed form / hero context, fetchpriority="high", or a numbered scrub
# sequence — and every finding carries px measured from the file header
# (PNG IHDR / JPEG SOF / GIF / WebP VP8·VP8L·VP8X; AVIF is skipped: ISOBMFF
# box-walking exceeds stdlib parsing and builds ship a same-dims WebP/JPEG
# sibling that carries the number), so the §7 asset-fidelity box reads machine
# numbers, never the builder's own table. Unresolvable refs and JSX-side images
# escape (false-negative bias).
IMG_RULE_ID = "IMG-NATIVE-RES"
IMG_FULL_BLEED_FLOOR = 1920  # 1.0× CSS px at the widest audited width (320–1920)
IMG_SEQUENCE_MIN = 12
IMG_RASTER_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif"}
IMG_REF_SUFFIX = r"\.(?:png|jpe?g|webp|gif|avif)"
IMG_CSS_URL_RE = re.compile(
    r"url\(\s*['\"]?([^'\")]+" + IMG_REF_SUFFIX + r")['\"]?\s*\)", re.IGNORECASE)
IMG_JS_DIR_RE = re.compile(r"['\"]([\w./-]*/)['\"]")
IMG_VARIANT_SUFFIX_RE = re.compile(r"[-_@](?:\d{2,4}w?|\d+x|[1248]k)$", re.IGNORECASE)
IMG_SEQ_NAME_RE = re.compile(r"^(.*?)(\d{2,})$")
IMG_COVER_RE = re.compile(r"\bcover\b|\b100vw\b")
IMG_HERO_HINT_RE = re.compile(r"hero|full-bleed|cover|bleed")
IMG_SIZES_MEDIA_RE = re.compile(r"\(\s*max-width\s*:\s*(\d+)px\s*\)")
IMG_DESCRIPTION = (
    "shipped image resolution under its layout floor — px measured from file "
    "headers, never the builder's table; a static scan cannot know rendered px, "
    "so the §7 asset-fidelity box judges the measured number (imagery.md — "
    "Native resolution or nothing)")


def _image_dims(path):
    """(width, height) from the file header, or None (AVIF, truncated, unknown)."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    try:
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", data[16:24])
        if data[:6] in (b"GIF87a", b"GIF89a"):
            return struct.unpack("<HH", data[6:10])
        if data[:2] == b"\xff\xd8":
            i = 2
            while i < len(data) - 9:
                if data[i] != 0xFF:
                    i += 1
                    continue
                marker = data[i + 1]
                if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                              0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    h, w = struct.unpack(">HH", data[i + 5:i + 9])
                    return (w, h)
                if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                    i += 2
                    continue
                i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
        if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            fmt = data[12:16]
            if fmt == b"VP8X":
                return (int.from_bytes(data[24:27], "little") + 1,
                        int.from_bytes(data[27:30], "little") + 1)
            if fmt == b"VP8 ":
                return (struct.unpack("<H", data[26:28])[0] & 0x3FFF,
                        struct.unpack("<H", data[28:30])[0] & 0x3FFF)
            if fmt == b"VP8L":
                b0, b1, b2, b3 = data[21:25]
                return (1 + (((b1 & 0x3F) << 8) | b0),
                        1 + (((b3 & 0x0F) << 10) | (b2 << 2) | ((b1 & 0xC0) >> 6)))
    except (struct.error, IndexError):
        return None
    return None


def _sizes_floor(sizes):
    """Largest slot a `sizes` attribute commits, in CSS px at the 1920 ceiling."""
    floor = 0.0
    for entry in sizes.split(","):
        entry = entry.strip()
        media = IMG_SIZES_MEDIA_RE.search(entry)
        cap = min(int(media.group(1)), IMG_FULL_BLEED_FLOOR) if media else IMG_FULL_BLEED_FLOOR
        vw = re.search(r"(\d+(?:\.\d+)?)vw\s*$", entry)
        px = re.search(r"(\d+(?:\.\d+)?)px\s*$", entry)
        if vw:
            floor = max(floor, float(vw.group(1)) / 100 * cap)
        elif px:
            floor = max(floor, float(px.group(1)))
    return min(int(round(floor)), IMG_FULL_BLEED_FLOOR)


def _srcset_refs(srcset):
    if not srcset:
        return []
    return [entry.strip().split()[0] for entry in srcset.split(",") if entry.strip()]


class _ImageRefParser(HTMLParser):
    """Collects <img>/<source> refs with their layout floor: a `sizes` slot, or
    the full-bleed floor when the tag sits in a full-bleed form / hero-classed
    ancestor or carries fetchpriority="high"."""

    def __init__(self):
        super().__init__()
        self.stack = []  # (tag, context_is_full_bleed)
        self.refs = []   # (ref, line, floor, signal)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        heroish = (bool(IMG_HERO_HINT_RE.search(a.get("class") or ""))
                   or "full-bleed" in (a.get("data-ad-form") or ""))
        context = heroish or (bool(self.stack) and self.stack[-1][1])
        if tag in ("img", "source"):
            floor, signal = 0, ""
            sizes = a.get("sizes")
            if sizes:
                floor = _sizes_floor(sizes)
                signal = f'sizes="{sizes}"'
            if not floor and (context or a.get("fetchpriority") == "high"):
                floor = IMG_FULL_BLEED_FLOOR
                signal = ("fetchpriority=high hero" if a.get("fetchpriority") == "high"
                          else "full-bleed/hero context")
            line = self.getpos()[0]
            src = a.get("src")
            for ref in _srcset_refs(a.get("srcset") or "") + ([src] if src else []):
                if re.search(IMG_REF_SUFFIX + r"$", ref.split("?")[0], re.IGNORECASE):
                    self.refs.append((ref, line, floor, signal))
        if tag not in VOID_TAGS:
            self.stack.append((tag, context))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def _css_image_refs(text):
    """url() refs with the full-bleed floor when the enclosing block cover-fits."""
    refs = []
    for match in IMG_CSS_URL_RE.finditer(text):
        start = text.rfind("{", 0, match.start())
        end = text.find("}", match.end())
        block = text[max(start, 0):end if end != -1 else len(text)]
        floor = IMG_FULL_BLEED_FLOOR if IMG_COVER_RE.search(block) else 0
        line = text.count("\n", 0, match.start()) + 1
        refs.append((match.group(1), line, floor, "cover-fit block" if floor else ""))
    return refs


def _resolve_candidate(ref, base_file, roots, want_dir):
    ref = ref.split("?", 1)[0].split("#", 1)[0]
    if not ref or re.match(r"^(?:[a-z][\w+.-]*:)?//", ref) or ref.startswith("data:"):
        return None
    candidates = []
    if ref.startswith("/"):
        candidates += [root / ref.lstrip("/") for root in roots]
    else:
        candidates.append(base_file.parent / ref)
        candidates += [root / ref for root in roots]
    for cand in candidates:
        try:
            if (cand.is_dir() if want_dir else cand.is_file()):
                return cand.resolve()
        except OSError:
            continue
    return None


def _sequence_groups(dirpath):
    """Numbered raster groups (≥ IMG_SEQUENCE_MIN files) under a referenced dir —
    the scrub-sequence signal; the numbering guard keeps a generic './' literal
    from sweeping a whole asset tree."""
    groups = {}
    for path in sorted(dirpath.rglob("*")):
        if path.is_file() and path.suffix.lower() in IMG_RASTER_EXTS:
            match = IMG_SEQ_NAME_RE.match(path.stem)
            if match:
                groups.setdefault((path.parent, match.group(1)), []).append(path)
    return {key: paths for key, paths in groups.items() if len(paths) >= IMG_SEQUENCE_MIN}


def _img_native_res_findings(texts, roots):
    findings = []
    groups = {}     # (file, stem) → {floor, signal, loc, paths}
    seq_seen = set()      # resolved dirs already walked
    seq_emitted = set()   # (parent, prefix) groups already reported
    for path, text in sorted(texts.items()):
        if _is_vendor(path):
            continue
        ext = path.suffix.lower()
        refs = []
        if ext in {".html", ".htm"}:
            parser = _ImageRefParser()
            try:
                parser.feed(text)
            except Exception:
                pass  # a malformed document is other rules' problem
            refs = parser.refs
        elif ext in {".css", ".scss"}:
            refs = _css_image_refs(text)
        if ext in {".html", ".htm", ".js", ".mjs"}:
            for match in IMG_JS_DIR_RE.finditer(text):
                seq_dir = _resolve_candidate(match.group(1), path, roots, want_dir=True)
                if seq_dir is None or seq_dir in seq_seen:
                    continue
                seq_seen.add(seq_dir)
                line = text.count("\n", 0, match.start()) + 1
                for (parent, prefix), frames in sorted(_sequence_groups(seq_dir).items()):
                    if (parent, prefix) in seq_emitted:
                        continue
                    seq_emitted.add((parent, prefix))
                    dims = [d for d in (_image_dims(p) for p in frames) if d]
                    if not dims:
                        continue
                    width, height = max(dims)
                    if width < IMG_FULL_BLEED_FLOOR:
                        findings.append(Finding(
                            IMG_RULE_ID, REVIEW, IMG_DESCRIPTION, f"{path}:{line}",
                            f"{len(frames)}-frame scrub sequence {parent}: largest frame "
                            f"{width}×{height} px < floor {IMG_FULL_BLEED_FLOOR} px "
                            "(scrub surfaces render full-bleed; §7 holds rendered ≤ shipped)"))
        for ref, line, floor, signal in refs:
            key = (path, IMG_VARIANT_SUFFIX_RE.sub("", Path(ref.split("?")[0]).stem))
            group = groups.setdefault(
                key, {"floor": 0, "signal": "", "loc": f"{path}:{line}", "paths": set()})
            if floor > group["floor"]:
                group["floor"], group["signal"] = floor, signal
            resolved = _resolve_candidate(ref, path, roots, want_dir=False)
            if resolved:
                group["paths"].add(resolved)
    for group in sorted(groups.values(), key=lambda g: g["loc"]):
        if not group["floor"] or not group["paths"]:
            continue
        dims = [(d, p) for p in sorted(group["paths"]) if (d := _image_dims(p))]
        if not dims:
            continue
        (width, height), best = max(dims, key=lambda t: t[0][0])
        if width < group["floor"]:
            findings.append(Finding(
                IMG_RULE_ID, REVIEW, IMG_DESCRIPTION, group["loc"],
                f"largest shipped variant {width}×{height} px ({best.name}, "
                f"{len(dims)} variant(s) measured) < layout floor {group['floor']} px "
                f"({group['signal']})"))
    return findings


ARCHETYPE_SUPPRESSIONS = {
    "editorial": {"EMDASH"},
    "corporate-luxury": {"EMDASH"},
    "brutalist": {"META-LABEL"},
}
MAX_EXCERPTS_PER_RULE = 10

# QUOTED-EXEMPLAR: winner strings quoted in references/copy-recipes.md — they
# calibrate, they never ship. Single source: every entry here must appear
# verbatim in that file (the test suite enforces the lockstep).
BANNED_EXEMPLARS = (
    "Réveillez votre croissance",
    "We have reinvented the future of logistics through the yard",
    "Global digital design studio partnering with brands and businesses",
    "Beauty is the symbol of the morally good",
    "AI research and products that put safety at the frontier",
    "We do not chase trends or produce work that looks like everyone else",
    "Please drive around to learn more about me",
    "A fast and flexible JavaScript library to animate the web",
    "AI-native technology that turns manual tasks into connected missions",
    "Exat consists of a whopping 1715 glyphs per style",
    "The Oldest Fine Leather Goods House in the World",
    "The yard of the future starts today",
    "Is Your Big Idea Ready to Go Wild",
    "Type designer & animator, working for brands globally",
    "Hold and drag to navigate the content",
    "Scroll to unlock the immersive film experience",
)

# Line rules: (id, severity, description, pattern, extensions).
LINE_RULES = [
    ("AI-PURPLE", FAIL,
     "banned AI-purple hex (#a855f7 / #8b5cf6 / #ec4899 / #6366f1)",
     re.compile(r"#(?:a855f7|8b5cf6|ec4899|6366f1)\b", re.IGNORECASE), CODE_EXTS),
    ("PURE-BW", FAIL,
     "pure #000 / #fff (also white/black keywords, rgb(255,255,255), oklch(1 0 0), "
     "bg-black / text-white) — use off-blacks and off-whites",
     # Keyword branch: only in color-bearing properties, keyword flanked so
     # `white-space`, `whitesmoke`, and `var(--white-soft)` never match; the
     # functional branches require a closing paren right after the channels so
     # alpha-carrying forms (`rgb(0 0 0 / .4)` scrims) stay unmatched, matching
     # the bg-white/5 exemption.
     re.compile(
         r"(?i)(?:color|background(?:-color)?|fill|stroke|border(?:-[a-z]+)*|outline|"
         r"box-shadow|text-shadow)\s*:\s*[^;{}\n]*#(?:000000|000|fff|ffffff)\b"
         r"|(?:color|background(?:-color)?|fill|stroke|border(?:-[a-z]+)*)"
         r"\s*:\s*[^;{}\n]*(?<=[\s:,])(?:white|black)(?![-\w])"
         r"|\brgb\(\s*(?:255[\s,]+255[\s,]+255|0[\s,]+0[\s,]+0)\s*\)"
         r"|\boklch\(\s*(?:1(?:\.0+)?|100%|0(?:\.0+)?|0%)\s+0\s+0\s*\)"
         r"|\b(?:bg|text|border|from|to|via|fill|stroke)-(?:black|white)\b(?!/)"), CODE_EXTS),
    ("H-SCREEN", FAIL,
     "h-screen / bare 100vh — use dvh units (iOS Safari URL-bar toggle breaks vh)",
     re.compile(r"\bh-screen\b|(?<![-\w.])100vh\b"), CODE_EXTS),
    ("SCROLL-LISTENER", FAIL,
     "window scroll listener — use ScrollTrigger, useScroll, IntersectionObserver, or CSS scroll-driven",
     re.compile(r"addEventListener\(\s*['\"]scroll['\"]"), CODE_EXTS),
    ("MARKERS", FAIL,
     "ScrollTrigger markers left on — debug scaffolding never ships",
     re.compile(r"markers:\s*true"), CODE_EXTS),
    ("SIDE-STRIPE", FAIL,
     "colored side-stripe accent border on a card/callout — the 2018-SaaS tell",
     re.compile(r"border-(?:left|right)\s*:\s*(?:[2-9]|\d{2,})px|\bborder-[lr]-(?:2|4|8)\b"), CODE_EXTS),
    ("META-LABEL", FAIL,
     "index meta-label (SECTION 01 / Step 2 / PHASE 03) — name the topic, not the count",
     # Upper- and title-case only: "Section 01" is a label, "see section 01"
     # is running prose and stays unmatched.
     re.compile(r"\b(?:SECTION|QUESTION|STAGE|STEP|PHASE|PASS"
                r"|Section|Question|Stage|Step|Phase|Pass)\s?0?\d\b"), TEXT_EXTS),
    ("LOREM", FAIL,
     "lorem ipsum — write real draft copy",
     re.compile(r"lorem ipsum", re.IGNORECASE), TEXT_EXTS),
    ("PLACEHOLDER-NAME", FAIL,
     "placeholder name / startup-slop brand (John Doe, Sarah Chen, Acme, SmartFlow)",
     re.compile(r"\b(?:John Doe|Jane Doe|Sarah Chen|Jack Su|Acme|SmartFlow|FlowKit|ProSync|Cloudly)\b"),
     TEXT_EXTS),
    ("FAKE-STAT", FAIL,
     "fake round statistic (99.99%, 10,000+) — real data has texture",
     re.compile(r"99\.9\d*\s*%|(?:10|50),?000\+|\d+×\s*faster|\+\d+%\s*conversion"), TEXT_EXTS),
    ("SCROLL-CUE", FAIL,
     "scroll cue (Scroll to explore, ↓) — design the affordance, don't label it",
     re.compile(r"(?i)scroll (?:to (?:explore|discover|walk)|down (?:to|for)|for more)"
                r"|↓\s*scroll|scroll\s*↓"), TEXT_EXTS),
    ("DEADLINK", FAIL,
     'dead `#` link — href="#" goes nowhere; wire a real target or use a <button>',
     re.compile(r"""href\s*=\s*(?:"#"|'#')"""), TEXT_EXTS),
    ("MOVING-BG-POS", FAIL,
     "JS-driven background-position — a per-frame repaint that pops; move a "
     "translated layer instead (motion-palette.md, moving windows)",
     re.compile(r"""\.style\.backgroundPosition|setProperty\(\s*['"]background-position"""),
     CODE_EXTS),
    ("BG-ATTACH-FIXED", REVIEW,
     "background-attachment: fixed — the mobile banding/repaint tell; translate "
     "a layer instead (motion-palette.md, moving windows)",
     re.compile(r"background-attachment\s*:\s*fixed"), CODE_EXTS),
    ("TRACKED-CLIP", REVIEW,
     "clip-path positioned by custom property — fine when static; a pointer/rAF-"
     "tracked var() repaints every frame (confirm the JS pairing; "
     "motion-palette.md, moving windows)",
     re.compile(r"clip-path\s*:[^;{}]*\bat\s+var\("), CODE_EXTS),
    ("TRACKED-ORIGIN", REVIEW,
     "transform-origin from a custom property — fine when static; a pointer/rAF-"
     "tracked var() re-rasterizes the layer every frame (confirm the JS pairing; "
     "motion-palette.md, moving windows)",
     re.compile(r"transform-origin\s*:[^;{}]*var\("), CODE_EXTS),
    ("CLICHE-COPY", FAIL,
     "AI copy cliché (Unleash your / Supercharge / Elevate your / where X meets Y) — "
     "write the promise from the build's own lexicon",
     # Phrase-level only — single common words never match (false-negative bias).
     re.compile(r"(?i)\b(?:unleash your|supercharge|empower your|elevate your"
                r"|built for the modern|in today['’]s digital|reimagine the way"
                r"|next-generation|seamlessly|where \w+ meets \w+)\b"), TEXT_EXTS),
    ("QUOTED-EXEMPLAR", FAIL,
     "winner catalog string shipped verbatim — copy-recipes.md quotes calibrate, never ship",
     re.compile("|".join(re.escape(s) for s in BANNED_EXEMPLARS), re.IGNORECASE), TEXT_EXTS),
    ("TRUNCATION", FAIL,
     "truncation tell (// ..., [remaining, for brevity) — the output is incomplete",
     re.compile(r"//\s*\.\.\.|/\*\s*\.\.\.\s*\*/|\[remaining |for brevity"
                r"|rest of (?:the )?code|similar to above|add more as needed"), CODE_EXTS),
    ("DISPLAY-FONT", REVIEW,
     "Inter/Roboto/Arial/system-ui in font-family — verify it is not the display face",
     re.compile(r"(?i)font-family\s*:\s*['\"]?(?:Inter|Roboto|Arial|system-ui)\b"
                r"|font-\[(?:Inter|Roboto|Arial)\]"), CODE_EXTS),
    ("IMG-ALT", FAIL,
     "<img> without alt",
     re.compile(r"<img\b(?![^>]*\balt\s*=)[^>]*>"), TEXT_EXTS),
    ("IMG-DIMENSIONS", REVIEW,
     "<img> without width/height attributes — verify CSS reserves the space (aspect-ratio), or ship CLS",
     re.compile(r"<img\b(?!(?=[^>]*\bwidth\s*=)(?=[^>]*\bheight\s*=))[^>]*>"), TEXT_EXTS),
    ("OUTLINE-NONE", FAIL,  # downgraded to REVIEW when :focus-visible exists project-wide
     "outline removed — needs a visible :focus-visible replacement",
     re.compile(r"outline\s*:\s*(?:none|0)\b|\boutline-none\b"), CODE_EXTS),
    ("UNSPLASH", REVIEW,
     "unsplash hotlink — breaks often and reads stock; use generated or seeded assets",
     re.compile(r"(?:images|source)\.unsplash\.com"), CODE_EXTS),
    ("NOJS-HIDDEN", REVIEW,
     "initial hidden state in base CSS — a dead script ships a blackout; hide via JS-added classes",
     re.compile(r"(?i)^(?!.*(?:@keyframes|\bfrom\b|\bto\b|\d+%|:hover|:focus|:active|\.no-js|html\.js))"
                r".*(?:opacity:\s*0(?![.\d])|visibility:\s*hidden)"), {".css", ".scss"}),
    ("EMOJI-UI", REVIEW,
     "emoji in markup — icons come from an icon set, never emoji",
     re.compile(r"[\U0001F300-\U0001FAFF☀-⛿✀-➿]"), TEXT_EXTS),
]

# COPY-LANG: the language law (copy-recipes.md) — copy ships in English unless
# the brief's exact ask names another language. Function words only, each safe
# against English prose and code tokens ("et", "pour", "con", "per", "die",
# "mit" are excluded as collisions); the thresholds keep register devices and
# addresses silent — false-negative bias, the §6 box holds the judgment.
NON_ENGLISH_STOPWORDS = {
    "French": frozenset(("les", "des", "une", "est", "dans", "avec", "vous",
                         "nous", "votre", "notre", "cette", "sont", "chez",
                         "aux", "très", "être", "déjà", "qui", "que", "pas")),
    "Spanish": frozenset(("los", "las", "una", "que", "para", "pero", "porque",
                          "nuestro", "nuestra", "también", "está", "más",
                          "desde", "hasta", "usted")),
    "German": frozenset(("und", "nicht", "für", "eine", "einen", "auch",
                         "über", "sind", "wird", "durch", "sehr", "ihre",
                         "können", "beim")),
    "Italian": frozenset(("gli", "della", "delle", "sono", "più", "questo",
                          "questa", "anche", "nella", "degli", "perché",
                          "così", "tutti", "siamo")),
}
COPY_LANG_MIN_DISTINCT = 4
COPY_LANG_MIN_TOTAL = 6
# Second channel: month names — the cheapest bleed vector is data chrome
# (French months beside English row states). Closed vocabulary, so 2 distinct
# suffice; English-colliding forms (mars, mai, mayo, maio, november) excluded.
NON_ENGLISH_MONTHS = frozenset((
    "janvier", "février", "avril", "juin", "juillet", "août",
    "septembre", "octobre", "novembre", "décembre",
    "enero", "febrero", "marzo", "junio", "julio", "agosto",
    "septiembre", "octubre", "noviembre", "diciembre",
    "gennaio", "febbraio", "aprile", "giugno", "luglio", "settembre",
    "ottobre", "dicembre",
    "januar", "februar", "märz", "oktober", "dezember",
    "janeiro", "fevereiro", "março", "junho", "julho", "setembro",
    "outubro", "novembro", "dezembro"))
COPY_LANG_MIN_MONTHS = 2
SCRIPT_STYLE_RE = re.compile(r"<(script|style)\b.*?</\1\s*>", re.S | re.I)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
WORD_RE = re.compile(r"[a-zà-öø-ÿ]+")

# EMDASH is a density rule, not a per-hit rule: the pre-flight box reads
# "≤ ~1 per 100 words of visible copy", so one legitimate dash never fails.
# Fires only past a minimum count AND the density threshold.
EMDASH_RE = re.compile(r"[—–]")
EMDASH_DENSITY = 0.01
EMDASH_MIN_COUNT = 3
# Pure comment lines are not visible copy — their dashes don't count.
HTML_COMMENT_LINE = re.compile(r"^\s*<!--.*-->\s*$")
TAG_RE = re.compile(r"<[^>]+>")
# Page-structure rules (H1-COUNT / MAIN-LANDMARK) skip near-empty documents —
# an SPA shell (<body><div id="root">) renders its h1/main from JS.
PAGE_MIN_WORDS = 30

# FONT-COUNT: the capture stops at the first comma/quote, so a fallback stack
# ("Söhne, Helvetica Neue, sans-serif") counts as one family, not three.
FONT_FAMILY_DECL = re.compile(r"font-family\s*:\s*['\"]?([^,;'\"]+)")
FONT_COUNT_MAX = 4  # 3 families + 1 mono outlier

# STAMP: Phase 4 writes the rotation ledger as the main stylesheet's first line.
STAMP_PREFIX = "/* award-design ·"
# STAMP-ARCHETYPE-MISMATCH: the archetype is the second `·`-delimited stamp
# field (`/* award-design · immersive-cinematic · <palette> · … */`). The stamp
# is builder-written; the archetype the audit scopes by is reviewer-supplied
# (--archetype), so a stamp whose archetype disagrees is caught, never obeyed.
STAMP_ARCHETYPE_RE = re.compile(r"/\*\s*award-design\s*·\s*([a-z0-9-]+)")

# Signals for the project-level REDUCED-MOTION rule.
MOTION_SIGNAL = re.compile(
    r"@keyframes|animation\s*:|animation-name|\bgsap\b|ScrollTrigger"
    r"|framer-motion|motion/react|whileInView")
MOTION_GUARD = re.compile(r"prefers-reduced-motion|useReducedMotion")
FOCUS_VISIBLE = re.compile(r":focus-visible")
# Eyebrow/kicker density signature — counts each eyebrow opening tag once, by
# any marker so vanilla-CSS builds are seen, not only Tailwind ones: a
# `data-slot="kicker"` slot, a semantic `class` carrying
# `kicker`/`eyebrow`, or the Tailwind uppercase+tracking utility pair. Keying
# only off `tracking-` counted zero on every `<p class="kicker">` build — the
# false negative that let a mono-caps kicker stamped over every section ship
# unflagged (COPY-ECHO is already class-agnostic for the same reason).
EYEBROW_SIGNATURE = re.compile(
    r"<[a-z][^>]*?(?:"
    r"data-slot=[\"']kicker[\"']"
    r"|class=[\"'][^\"']*\b(?:kicker|eyebrow)\b[^\"']*[\"']"
    r"|uppercase[^>\"'`]*tracking-|tracking-\[[^\]]*\][^>\"'`]*uppercase"
    r")[^>]*>",
    re.IGNORECASE)
SECTION_TAG = re.compile(r"<section\b")
H1_TAG = re.compile(r"<h1\b")
MAIN_TAG = re.compile(r"<main\b")
BODY_TAG = re.compile(r"<body\b")


class Finding:
    def __init__(self, rule_id, severity, description, location, excerpt):
        self.rule_id = rule_id
        self.severity = severity
        self.description = description
        self.location = location  # "file:line" or "project"
        self.excerpt = excerpt


def iter_files(paths):
    for raw in paths:
        root = Path(raw)
        if root.is_file():
            if root.suffix.lower() in CODE_EXTS and root.name != "DESIGN.md":
                yield root
            continue
        if not root.is_dir():
            print(f"warning: path not found, skipped: {root}", file=sys.stderr)
            continue
        for path in sorted(root.rglob("*")):
            if any(part in EXCLUDED_DIRS for part in path.relative_to(root).parts[:-1]):
                continue
            # DESIGN.md is the spec, not the build — its Don'ts legitimately
            # quote banned phrases as prohibitions and would never scan clean.
            if path.name == "DESIGN.md":
                continue
            if path.is_file() and path.suffix.lower() in CODE_EXTS:
                yield path


PROJECT_RULE_IDS = {"EMDASH", "H1-COUNT", "MAIN-LANDMARK", "REDUCED-MOTION", "EYEBROW-DENSITY",
                    "FONT-COUNT", "STAMP", "COPY-LANG", "FORM-SLOT", "COPY-ECHO"}


# FORM-SLOT: inside a section-form root ([data-ad-form]) the form owns the
# layout and every direct child must be a named slot — a slotless child is
# freeform layout smuggled back inside the form, the exact defect class the
# forms exist to kill. Slot names are validated against the library manifest's
# forms contract when it is readable; a missing manifest skips only the
# name check, never the direct-child check.
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input",
             "link", "meta", "param", "source", "track", "wbr"}


def _load_form_contracts():
    manifest = Path(__file__).resolve().parent.parent / "assets" / "components" / "manifest.json"
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        return {f["id"]: {s["name"] for s in f.get("slots", [])}
                for f in data.get("forms", [])}
    except (OSError, ValueError, KeyError, TypeError):
        return {}


class _FormSlotParser(HTMLParser):
    """Tracks [data-ad-form] roots; flags a direct child element without
    data-slot, and a slot name outside the form's manifest contract."""

    def __init__(self, contracts):
        super().__init__()
        self.contracts = contracts
        self.stack = []  # (tag, is_form_root, form_id)
        self.violations = []  # (line, message)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.stack and self.stack[-1][1]:
            form_id = self.stack[-1][2]
            slot = a.get("data-slot")
            line = self.getpos()[0]
            if slot is None:
                self.violations.append(
                    (line, f"<{tag}> is a direct child of [data-ad-form=\"{form_id}\"] with no data-slot"))
            elif form_id in self.contracts and slot not in self.contracts[form_id]:
                self.violations.append(
                    (line, f"slot \"{slot}\" is not in the {form_id} form's contract"))
        if tag not in VOID_TAGS:
            self.stack.append((tag, "data-ad-form" in a, a.get("data-ad-form", "")))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


# COPY-ECHO: a kicker/eyebrow directly above a heading that repeats one of its
# content words reads as redundant labelling — "THE 2026 SEASON" over "Book your
# season." (the ARDEN copy defect). META-LABEL and EYEBROW-DENSITY are pattern/
# count rules that cannot see a cross-block word echo, so this parses markup
# structure — class-agnostic, since the skill's own output is vanilla CSS whose
# kickers carry no Tailwind signature. Scoped to the kicker->heading pair, the
# high-signal case; the heading->first-line pair is judged in preflight §6 (a body
# line naturally re-uses the heading's topic, so a mechanical rule there is noise).
# REVIEW — the brand/product proper noun is a legitimate shared word, judged.
COPY_ECHO_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "span", "small", "strong", "em", "li", "figcaption"}
COPY_ECHO_HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
COPY_ECHO_CONTENT_WORD = re.compile(r"[a-z]{4,}")
COPY_ECHO_KICKER_MAX = 44
COPY_ECHO_STOPWORDS = frozenset({
    "your", "yours", "ours", "with", "from", "this", "that", "these", "those",
    "into", "onto", "over", "under", "about", "will", "would", "could", "should",
    "have", "been", "being", "were", "their", "them", "they", "then", "than",
    "what", "when", "where", "which", "while", "here", "there", "just", "also",
    "very", "more", "most", "such", "only", "even", "each", "both", "does",
})


def _copy_echo_words(text):
    return {w for w in COPY_ECHO_CONTENT_WORD.findall(text.lower())
            if w not in COPY_ECHO_STOPWORDS}


class _CopyEchoParser(HTMLParser):
    """Emits top-level text blocks in reading order, each carrying its full nested
    text (a styled word inside a heading stays part of the heading, never a
    separate block). Nesting is resolved by emitting only elements with no tracked
    ancestor and folding descendant text up into them."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []  # (tag, text, line)
        self.stack = []   # frames: {"tag","line","chunks","top"}

    def handle_starttag(self, tag, attrs):
        if tag in COPY_ECHO_TAGS:
            self.stack.append({"tag": tag, "line": self.getpos()[0], "chunks": [], "top": not self.stack})

    def handle_data(self, data):
        for frame in self.stack:  # fold text into every open frame → parents keep nested text
            frame["chunks"].append(data)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                frame = self.stack[i]
                del self.stack[i:]
                if frame["top"]:
                    text = " ".join("".join(frame["chunks"]).split())
                    if text:
                        self.blocks.append((frame["tag"], text, frame["line"]))
                break


def _copy_echo_findings(text):
    parser = _CopyEchoParser()
    try:
        parser.feed(text)
    except Exception:
        return []  # a malformed document is other rules' problem
    out = []
    blocks = parser.blocks
    for i, (tag, htext, line) in enumerate(blocks):
        if tag not in COPY_ECHO_HEADINGS or i == 0:
            continue
        ptag, ptext, _ = blocks[i - 1]
        is_kicker = (ptag not in COPY_ECHO_HEADINGS and len(ptext) <= COPY_ECHO_KICKER_MAX
                     and not re.search(r"[.!?]", ptext))
        if not is_kicker:
            continue
        shared = _copy_echo_words(ptext) & _copy_echo_words(htext)
        if shared:
            out.append((line,
                        f'kicker "{ptext}" and heading "{htext}" share the word '
                        f'"{sorted(shared)[0]}" — read the pair; cut or reword one '
                        f'(a brand/product proper noun is exempt, judged in §6)'))
        if len(out) >= 12:
            break
    return out


# ── OPTICAL-* — the craft pass as decidable stylesheet facts (REVIEW-only) ──
# optical-craft.md is *installed* at build time, never detected, so these five
# rules only read back the mechanical half of it: a tracking value that never
# moved across the ramp, headline balance never asked for, statistics that
# jitter, a shadow with no temperature, an unstyled selection. Every one is a
# fact about the stylesheet, so every one is decidable — and every one is
# REVIEW, because the judgment (is this register deliberate?) is the reviewer's.
#
# All five share one precondition: a real built page — at least one stylesheet
# AND a document carrying real copy. A stylesheet-only tree or a markup
# fragment has no craft pass to have skipped, and flagging one would be the
# scanner guessing.
OPTICAL_RULE_IDS = {"OPTICAL-TRACKING", "OPTICAL-BALANCE", "OPTICAL-TABULAR",
                    "OPTICAL-SHADOW", "OPTICAL-SELECTION"}
OPTICAL_STYLE_EXTS = {".css", ".scss"}
# Astro is this skill's default framework for four archetypes and routinely
# ships every rule inside a component `<style>` block with no .css file at all —
# so the family reads those too, or it is blind on the stack it recommends.
OPTICAL_STYLE_BLOCK_RE = re.compile(r"<style\b[^>]*>(.*?)</style\s*>", re.DOTALL | re.IGNORECASE)
# Document extensions only — a README beside a stylesheet is not a page.
OPTICAL_PAGE_EXTS = TEXT_EXTS - {".md", ".mdx"}
# optical-craft.md: body tracks at 0, headings 24–48px at -0.01/-0.02em, display
# ≥64px at -0.03/-0.045em. So the curve must have moved by the heading band —
# below it, a shared value is legitimately correct.
OPTICAL_DISPLAY_FLOOR_PX = 24
OPTICAL_MIN_DISPLAY_SIZES = 3
CSS_BLOCK_RE = re.compile(r"[^{}]*\{([^{}]*)\}")
FONT_SIZE_DECL_RE = re.compile(r"(?<![-\w])font-size\s*:\s*([^;}]+)")
LETTER_SPACING_DECL_RE = re.compile(r"(?<![-\w])letter-spacing\s*:\s*([^;}]+)")
# em is relative to the element's own parent font-size and unknowable statically.
CSS_LENGTH_RE = re.compile(r"(-?\d*\.?\d+)\s*(rem|px)\b")
HEADLINE_TAG_RE = re.compile(r"<h[1-3]\b", re.IGNORECASE)
TEXT_WRAP_RE = re.compile(r"text-wrap\s*:\s*(?:balance|pretty)|\btext-(?:balance|pretty)\b")
# A stat surface, not a stray numeral: a named stat/metric/price slot whose own
# text carries a digit, or a counter element declaring its target as data.
STAT_SIGNATURE_RE = re.compile(
    r"<[a-z][^>]*?(?:class|data-slot)=[\"'][^\"']*\b(?:stat|stats|metric|metrics|counter"
    r"|kpi|price|pricing|figure-number|numeral|tally)\b[^\"']*[\"'][^>]*>\s*[^<]*\d"
    r"|<[a-z][^>]*\bdata-(?:count|target|value)\s*=\s*[\"']?-?\d",
    re.IGNORECASE)
TABULAR_RE = re.compile(r"tabular-nums|font-variant-numeric\s*:[^;}]*\btabular\b")
PURE_BLACK_SHADOW_RE = re.compile(
    r"box-shadow\s*:[^;}]*(?:rgba?\(\s*0\s*[,\s]\s*0\s*[,\s]\s*0\b|#000(?:000)?\b)",
    re.IGNORECASE)
SELECTION_RE = re.compile(r"::selection\b", re.IGNORECASE)
GROUND_TOKEN_RE = re.compile(
    r"--[\w-]*(?:bg|background|surface|paper|ground|canvas|shell|page|base|ink)[\w-]*"
    r"\s*:\s*([^;{}]+)", re.IGNORECASE)
# Channel spread that reads as a hue rather than a neutral, per space.
GROUND_NEUTRAL_RGB_SPREAD = 8      # of 255
GROUND_NEUTRAL_CHROMA = 0.01       # oklch C / oklab |a|,|b|
GROUND_NEUTRAL_SATURATION = 3.0    # hsl S%


def _css_decl_blocks(text):
    """(line_no, declaration_body) for every brace-delimited block. At-rule
    wrappers fold into the selector half, which is fine — only declarations
    are read."""
    for match in CSS_BLOCK_RE.finditer(text):
        yield text.count("\n", 0, match.start(1)) + 1, match.group(1)


def _max_length_px(value):
    """Largest px-equivalent length in a declaration value (clamp() included),
    or None when every term is a var() / em / keyword the scan cannot resolve."""
    lengths = [float(num) * (16.0 if unit == "rem" else 1.0)
               for num, unit in CSS_LENGTH_RE.findall(value)]
    return max(lengths) if lengths else None


def _is_chromatic(value):
    """True when a colour carries a hue rather than sitting on the grey axis."""
    value = value.strip().lower()
    match = re.search(r"oklch\(\s*[\d.%]+\s+([\d.]+)", value)
    if match:
        return float(match.group(1)) > GROUND_NEUTRAL_CHROMA
    match = re.search(r"oklab\(\s*[\d.%]+\s+(-?[\d.]+)\s+(-?[\d.]+)", value)
    if match:
        return (abs(float(match.group(1))) > GROUND_NEUTRAL_CHROMA
                or abs(float(match.group(2))) > GROUND_NEUTRAL_CHROMA)
    match = re.search(r"hsla?\(\s*[\d.]+(?:deg)?\s*[,\s]\s*([\d.]+)%", value)
    if match:
        return float(match.group(1)) > GROUND_NEUTRAL_SATURATION
    match = re.search(r"#([0-9a-f]{3}|[0-9a-f]{6})\b", value)
    if match:
        digits = match.group(1)
        if len(digits) == 3:
            digits = "".join(c * 2 for c in digits)
        channels = [int(digits[i:i + 2], 16) for i in (0, 2, 4)]
        return max(channels) - min(channels) > GROUND_NEUTRAL_RGB_SPREAD
    match = re.search(r"rgba?\(\s*(\d+)\s*[,\s]\s*(\d+)\s*[,\s]\s*(\d+)", value)
    if match:
        channels = [int(g) for g in match.groups()]
        return max(channels) - min(channels) > GROUND_NEUTRAL_RGB_SPREAD
    return False


def _ground_is_chromatic(style_blob):
    return any(_is_chromatic(match.group(1)) for match in GROUND_TOKEN_RE.finditer(style_blob))


def _stylesheets(texts):
    """(path, first_line, css) for every stylesheet file and every embedded
    `<style>` block. first_line anchors a finding back to the real line."""
    sheets = []
    for path, text in sorted(texts.items()):
        if _is_vendor(path):
            continue
        ext = path.suffix.lower()
        if ext in OPTICAL_STYLE_EXTS:
            sheets.append((path, 1, text))
        elif ext in TEXT_EXTS or ext == ".astro":
            for match in OPTICAL_STYLE_BLOCK_RE.finditer(text):
                sheets.append((path, text.count("\n", 0, match.start(1)) + 1, match.group(1)))
    return sheets


def _optical_findings(texts):
    """The five craft facts. Silent unless the project is a real built page."""
    sheets = _stylesheets(texts)
    # The markup half of the precondition: a document extension (never .md —
    # a README beside a stylesheet is not a page) carrying a body's worth of
    # copy. Its `<style>` blocks are already counted as stylesheets above, so
    # they are stripped here rather than read twice.
    pages = [OPTICAL_STYLE_BLOCK_RE.sub(" ", text)
             for path, text in texts.items()
             if path.suffix.lower() in OPTICAL_PAGE_EXTS and not _is_vendor(path)
             and len(TAG_RE.sub(" ", text).split()) >= PAGE_MIN_WORDS]
    if not sheets or not pages:
        return []

    style_blob = "\n".join(css for _, _, css in sheets)
    page_blob = "\n".join(pages)
    findings = []

    # OPTICAL-TRACKING — the ramp that never moved.
    tracking = {}   # display px → set of letter-spacing values
    for _, _, css in sheets:
        for _, body in _css_decl_blocks(css):
            size_decl = FONT_SIZE_DECL_RE.search(body)
            track_decl = LETTER_SPACING_DECL_RE.search(body)
            if not size_decl or not track_decl:
                continue
            size = _max_length_px(size_decl.group(1))
            if size is None or size < OPTICAL_DISPLAY_FLOOR_PX:
                continue
            tracking.setdefault(size, set()).add(" ".join(track_decl.group(1).split()).lower())
    values = {value for group in tracking.values() for value in group}
    if len(tracking) >= OPTICAL_MIN_DISPLAY_SIZES and len(values) == 1:
        sizes = ", ".join(f"{int(s) if s == int(s) else s}px" for s in sorted(tracking))
        findings.append(Finding(
            "OPTICAL-TRACKING", REVIEW,
            "one letter-spacing value across the whole display ramp — tracking is a curve "
            "that tightens as size grows, and a single value is the tell that no optical "
            "pass happened (optical-craft.md, Type optics)",
            "project",
            f"letter-spacing: {values.pop()} on all {len(tracking)} display sizes ({sizes})"))

    # OPTICAL-BALANCE — the cheapest line of typographic polish, unasked for.
    if HEADLINE_TAG_RE.search(page_blob) and not TEXT_WRAP_RE.search(style_blob):
        findings.append(Finding(
            "OPTICAL-BALANCE", REVIEW,
            "headlines ship with no text-wrap: balance (and body with no pretty) — widows "
            "and lonely last words are left to the line-breaker (optical-craft.md, Type optics)",
            "project",
            f"{len(HEADLINE_TAG_RE.findall(page_blob))} h1–h3 element(s), "
            f"zero text-wrap balance/pretty declarations in {len(sheets)} stylesheet(s)"))

    # OPTICAL-TABULAR — proportional figures in a column never line up.
    if STAT_SIGNATURE_RE.search(page_blob) and not TABULAR_RE.search(style_blob):
        findings.append(Finding(
            "OPTICAL-TABULAR", REVIEW,
            "numeric stat surfaces with no font-variant-numeric: tabular-nums — proportional "
            "figures jitter as values change and never align in a column "
            "(optical-craft.md, Type optics)",
            "project",
            f"{len(STAT_SIGNATURE_RE.findall(page_blob))} stat/counter signature(s), "
            "zero tabular-nums declarations"))

    # OPTICAL-SHADOW — elevation reads as light, and light has a temperature.
    if _ground_is_chromatic(style_blob):
        for path, first_line, css in sheets:
            for offset, line in enumerate(css.splitlines()):
                if PURE_BLACK_SHADOW_RE.search(line):
                    line_no = first_line + offset
                    findings.append(Finding(
                        "OPTICAL-SHADOW", REVIEW,
                        "pure-black shadow over a hued ground — tint every shadow with the "
                        "surface hue at low alpha, or the elevation reads as a sticker "
                        "(optical-craft.md, Spatial optics)",
                        f"{path}:{line_no}", line.strip()[:120]))

    # OPTICAL-SELECTION — the quiet layer's cheapest second-read detail.
    if not SELECTION_RE.search(style_blob):
        findings.append(Finding(
            "OPTICAL-SELECTION", REVIEW,
            "no ::selection rule — the drag-highlight ships the browser default on a page "
            "that authored everything else (optical-craft.md, The quiet layer)",
            "project",
            f"zero ::selection rules across {len(sheets)} stylesheet(s)"))

    return findings


# ── STACK-FACTS-STALE — the skill auditing its own dated facts ──
# stack-facts.md is the single source for every version, package, and support
# number the references cite; each row carries `checked: YYYY-MM`. Past the
# window, the fetch-class rows are assertions again. Scoped to the CLI report
# (main) rather than scan_paths: the freshness of the skill's own facts is not
# a property of the build being scanned, and folding it in would make a clean
# build start reporting a maintenance notice it cannot act on.
STACK_FACTS_RULE_ID = "STACK-FACTS-STALE"
STACK_FACTS_MAX_AGE_DAYS = 180
STACK_FACTS_CHECKED_RE = re.compile(r"checked:\s*(\d{4})-(\d{2})(?:-(\d{2}))?")


def stack_facts_findings(path=None, today=None):
    """One REVIEW line when any dated row is past the window. Silent when the
    file is absent — an installed skill may ship without it, and a guess is
    worse than nothing."""
    path = Path(path) if path else (
        Path(__file__).resolve().parent.parent / "references" / "stack-facts.md")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    today = today or date.today()
    oldest = None
    stale = 0
    for match in STACK_FACTS_CHECKED_RE.finditer(text):
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3) or 1)
        try:
            checked = date(year, month, day)
        except ValueError:
            continue
        if (today - checked).days > STACK_FACTS_MAX_AGE_DAYS:
            stale += 1
            if oldest is None or checked < oldest:
                oldest = checked
    if not stale:
        return []
    return [Finding(
        STACK_FACTS_RULE_ID, REVIEW,
        f"stack-facts.md rows are past {STACK_FACTS_MAX_AGE_DAYS} days — re-verify the "
        "fetch-class rows (Three.js, SplitText, support numbers) before any reference "
        "cites them again",
        str(path),
        f"{stale} stale row(s); oldest checked {oldest.isoformat()}, "
        f"{(today - oldest).days} days ago")]


# Rules that fire only when their precondition is met (an argument passed, a
# built page, the skill's own reference tree), so they are not expected on a
# bare dirty-fixture scan — registered for the checklist lockstep, exempt from
# the "fires on dirty" net.
CONDITIONAL_RULE_IDS = {"STAMP-ARCHETYPE-MISMATCH"}


def known_rule_ids():
    return ({rule[0] for rule in LINE_RULES} | PROJECT_RULE_IDS | CONDITIONAL_RULE_IDS
            | OPTICAL_RULE_IDS | {EASE_RULE_ID, IMG_RULE_ID, STACK_FACTS_RULE_ID})


def scan_paths(paths, archetype=""):
    """Returns (findings, suppressed) — findings is a list of Finding."""
    suppressed = set()
    suppression_notes = []
    archetype_key = archetype.strip().lower()
    for rule_id in sorted(ARCHETYPE_SUPPRESSIONS.get(archetype_key, ())):
        suppressed.add(rule_id)
        suppression_notes.append(f"{rule_id} (archetype {archetype_key})")

    findings = []
    files = list(iter_files(paths))
    # Roots anchor root-relative and directory refs (IMG-NATIVE-RES); a bare
    # file list (test invocations) falls back to the files' own parents.
    dir_roots = [Path(raw) for raw in paths if Path(raw).is_dir()]
    if not dir_roots:
        dir_roots = sorted({path.parent for path in files})
    texts = {}
    for path in files:
        try:
            texts[path] = path.read_text(encoding="utf-8", errors="replace")
        except OSError as err:
            print(f"warning: unreadable, skipped: {path} ({err})", file=sys.stderr)

    project_blob = "\n".join(texts.values())
    has_focus_visible = bool(FOCUS_VISIBLE.search(project_blob))
    form_contracts = _load_form_contracts()

    emdash_count = 0
    emdash_hits = []
    text_words = 0

    for path, text in texts.items():
        ext = path.suffix.lower()
        if _is_vendor(path):
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            if ext in TEXT_EXTS and not HTML_COMMENT_LINE.match(line):
                dashes = EMDASH_RE.findall(line)
                if dashes:
                    emdash_count += len(dashes)
                    emdash_hits.append((f"{path}:{line_no}", line.strip()[:120]))
            for rule_id, severity, description, pattern, exts in LINE_RULES:
                if rule_id in suppressed or ext not in exts:
                    continue
                if pattern.search(line):
                    if rule_id == "OUTLINE-NONE" and has_focus_visible:
                        severity = REVIEW
                    findings.append(Finding(
                        rule_id, severity, description,
                        f"{path}:{line_no}", line.strip()[:120]))
            if EASE_RULE_ID not in suppressed and ext in EASE_EXTS:
                for match in CUBIC_BEZIER_RE.finditer(line):
                    y1, y2 = float(match.group(2)), float(match.group(4))
                    if not (0.0 <= y1 <= 1.0 and 0.0 <= y2 <= 1.0):
                        findings.append(Finding(
                            EASE_RULE_ID, REVIEW, EASE_DESCRIPTION,
                            f"{path}:{line_no}",
                            f"{match.group(0)} — {_bezier_character(y1, y2)}"))
                for match in SPRING_TOKEN_RE.finditer(line):
                    findings.append(Finding(
                        EASE_RULE_ID, REVIEW, EASE_DESCRIPTION,
                        f"{path}:{line_no}",
                        f"`{match.group(0)}` — spring/elastic token"))

        if ext in TEXT_EXTS:
            text_words += len(TAG_RE.sub(" ", text).split())

        # COPY-LANG — visible text only: script/style bodies and comments are
        # stripped so code tokens never count as copy.
        if "COPY-LANG" not in suppressed and ext in TEXT_EXTS:
            visible = TAG_RE.sub(" ", HTML_COMMENT_RE.sub(" ", SCRIPT_STYLE_RE.sub(" ", text)))
            tokens = WORD_RE.findall(visible.lower())
            for language, stopwords in NON_ENGLISH_STOPWORDS.items():
                lang_hits = [t for t in tokens if t in stopwords]
                distinct = len(set(lang_hits))
                if distinct >= COPY_LANG_MIN_DISTINCT and len(lang_hits) >= COPY_LANG_MIN_TOTAL:
                    sample = ", ".join(sorted(set(lang_hits))[:6])
                    findings.append(Finding(
                        "COPY-LANG", FAIL,
                        f"non-English copy ({language}) — copy ships in English unless "
                        "the brief's exact ask names another language "
                        "(copy-recipes.md, the language law)",
                        str(path),
                        f"{len(lang_hits)} hits across {distinct} {language} "
                        f"function words: {sample}"))
            month_hits = sorted({t for t in tokens if t in NON_ENGLISH_MONTHS})
            if len(month_hits) >= COPY_LANG_MIN_MONTHS:
                findings.append(Finding(
                    "COPY-LANG", FAIL,
                    "non-English month names — date chrome holds the page language "
                    "(copy-recipes.md, the language law)",
                    str(path),
                    f"{len(month_hits)} distinct non-English months: "
                    f"{', '.join(month_hits[:6])}"))

        # FORM-SLOT — section-form roots own their layout; a slotless direct
        # child or an uncontracted slot name is freeform smuggled inside.
        if ("FORM-SLOT" not in suppressed and ext in {".html", ".htm"}
                and "data-ad-form" in text):
            parser = _FormSlotParser(form_contracts)
            try:
                parser.feed(text)
            except Exception:
                pass  # a malformed document is other rules' problem
            for line_no, message in parser.violations:
                findings.append(Finding(
                    "FORM-SLOT", FAIL,
                    "section-form slot violation — the form owns the layout; "
                    "direct children carry data-slot from the form's contract "
                    "(components/README.md, section forms)",
                    f"{path}:{line_no}", message))

        # COPY-ECHO — a kicker directly above a heading that repeats one of its
        # content words (the ARDEN "THE 2026 SEASON" / "season" defect).
        if "COPY-ECHO" not in suppressed and ext in {".html", ".htm"}:
            for line_no, message in _copy_echo_findings(text):
                findings.append(Finding(
                    "COPY-ECHO", REVIEW,
                    "kicker/heading word echo — a kicker repeating a heading's "
                    "content word reads as redundant labelling (preflight §6)",
                    f"{path}:{line_no}", message))

        # Per-page structural rules — full HTML documents with real content
        # only (an SPA shell renders its h1/main from JS).
        if (ext in {".html", ".htm"} and BODY_TAG.search(text)
                and len(TAG_RE.sub(" ", text).split()) >= PAGE_MIN_WORDS):
            h1_count = len(H1_TAG.findall(text))
            if "H1-COUNT" not in suppressed and h1_count != 1:
                findings.append(Finding(
                    "H1-COUNT", FAIL,
                    "each page carries exactly one <h1>",
                    str(path), f"{h1_count} <h1> found"))
            if "MAIN-LANDMARK" not in suppressed and not MAIN_TAG.search(text):
                findings.append(Finding(
                    "MAIN-LANDMARK", FAIL,
                    "page has no <main> landmark",
                    str(path), "add <main> around the primary content"))

    if ("EMDASH" not in suppressed and emdash_count >= EMDASH_MIN_COUNT
            and text_words and emdash_count / text_words > EMDASH_DENSITY):
        description = (f"em/en dash density {emdash_count} per {text_words} visible words — "
                       "above ~1/100 reads as AI prose")
        for location, excerpt in emdash_hits:
            findings.append(Finding("EMDASH", FAIL, description, location, excerpt))

    # IMG-NATIVE-RES — dims-vs-layout, measured from headers (REVIEW-only proxy).
    if IMG_RULE_ID not in suppressed:
        findings.extend(_img_native_res_findings(texts, dir_roots))

    # OPTICAL-* — the craft pass read back off the stylesheet (REVIEW-only).
    findings.extend(f for f in _optical_findings(texts) if f.rule_id not in suppressed)

    # Project-level rules.
    motion_signals = len(MOTION_SIGNAL.findall(project_blob))
    if ("REDUCED-MOTION" not in suppressed and motion_signals
            and not MOTION_GUARD.search(project_blob)):
        findings.append(Finding(
            "REDUCED-MOTION", FAIL,
            "motion present with no prefers-reduced-motion branch anywhere",
            "project", f"{motion_signals} motion signal(s), zero guards"))

    text_blob = "\n".join(t for p, t in texts.items() if p.suffix.lower() in TEXT_EXTS)
    sections = len(SECTION_TAG.findall(text_blob))
    eyebrows = len(EYEBROW_SIGNATURE.findall(text_blob))
    if ("EYEBROW-DENSITY" not in suppressed and sections >= 3
            and eyebrows > math.ceil(sections / 3)):
        findings.append(Finding(
            "EYEBROW-DENSITY", REVIEW,
            "eyebrow-signature count exceeds ceil(sections/3) — verify against the rendered page",
            "project", f"{eyebrows} eyebrow signature(s) for {sections} section(s), "
                       f"max {math.ceil(sections / 3)}"))

    families = set()
    for path, text in texts.items():
        if path.suffix.lower() in {".css", ".scss"}:
            for match in FONT_FAMILY_DECL.finditer(text):
                families.add(match.group(1).strip().lower())
    if "FONT-COUNT" not in suppressed and len(families) > FONT_COUNT_MAX:
        findings.append(Finding(
            "FONT-COUNT", REVIEW,
            "distinct font-family count exceeds the page-wide cap — more reads as collage",
            "project", f"{len(families)} distinct font families — cap is 3 plus one mono outlier"))

    css_files = [path for path in texts if path.suffix.lower() == ".css"]
    if ("STAMP" not in suppressed and css_files
            and not any(texts[path].split("\n", 1)[0].startswith(STAMP_PREFIX)
                        for path in css_files)):
        findings.append(Finding(
            "STAMP", REVIEW,
            f"missing rotation stamp — no stylesheet's first line starts with `{STAMP_PREFIX}`",
            "project", f"{len(css_files)} stylesheet(s) scanned, none opens with the stamp"))

    # STAMP-ARCHETYPE-MISMATCH: only when the reviewer supplied an archetype —
    # the stamp's own archetype field must agree, or the build applied the wrong
    # archetype's grammar (or mis-stamped to dodge an archetype-scoped check).
    if "STAMP-ARCHETYPE-MISMATCH" not in suppressed and archetype_key:
        for path in css_files:
            first_line = texts[path].split("\n", 1)[0]
            match = STAMP_ARCHETYPE_RE.match(first_line.strip())
            if not match:
                continue
            stamped = match.group(1)
            if stamped != archetype_key:
                findings.append(Finding(
                    "STAMP-ARCHETYPE-MISMATCH", REVIEW,
                    f"stamp archetype `{stamped}` disagrees with the reviewer archetype "
                    f"`{archetype_key}` — the build applied a different archetype's grammar, "
                    "or mis-stamped to dodge an archetype-scoped check; the reviewer "
                    "archetype governs the audit, never the stamp",
                    f"{path}:1", first_line.strip()[:120]))
            break

    return findings, suppression_notes


def format_report(findings, suppression_notes, files):
    lines = []
    by_rule = {}
    for finding in findings:
        by_rule.setdefault((finding.severity, finding.rule_id), []).append(finding)

    ordered = sorted(by_rule.items(), key=lambda kv: (kv[0][0] != FAIL, kv[0][1]))
    for (severity, rule_id), hits in ordered:
        lines.append(f"{severity} {rule_id} — {hits[0].description} ({len(hits)} hit(s))")
        for finding in hits[:MAX_EXCERPTS_PER_RULE]:
            lines.append(f"  {finding.location}: {finding.excerpt}")
        if len(hits) > MAX_EXCERPTS_PER_RULE:
            lines.append(f"  … and {len(hits) - MAX_EXCERPTS_PER_RULE} more")
        lines.append("")

    fail_hits = [f for f in findings if f.severity == FAIL]
    review_hits = [f for f in findings if f.severity == REVIEW]
    fail_rules = {f.rule_id for f in fail_hits}
    review_rules = {f.rule_id for f in review_hits}
    text_files = sum(1 for path in files if path.suffix.lower() in TEXT_EXTS)
    lines.append(f"{len(files)} files scanned ({text_files} text / {len(files) - text_files} code)")
    lines.append(
        f"Summary: {len(fail_hits)} FAIL hit(s) across {len(fail_rules)} rule(s) · "
        f"{len(review_hits)} REVIEW hit(s) across {len(review_rules)} rule(s)")
    if suppression_notes:
        lines.append("Suppressed: " + ", ".join(suppression_notes))
    lines.append("Every FAIL: fix it or justify it in the pre-flight verdict. "
                 "Every REVIEW: judge it against the catalog. "
                 "A clean scan ticks no box — it catches, it never clears.")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="award-design pre-flight scanner — countable anti-slop tells")
    parser.add_argument("paths", nargs="+", help="build files or directories to scan")
    parser.add_argument("--archetype", default="",
                        help="build archetype; editorial / corporate-luxury suppress EMDASH")
    args = parser.parse_args(argv)

    files = list(iter_files(args.paths))
    # scan_paths gets the raw paths, not the file list — directory roots anchor
    # root-relative image refs (IMG-NATIVE-RES); it re-derives the same files.
    findings, suppression_notes = scan_paths(args.paths, args.archetype)
    findings.extend(stack_facts_findings())
    print(format_report(findings, suppression_notes, files))
    if not files:
        return 2
    return 1 if any(f.severity == FAIL for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
