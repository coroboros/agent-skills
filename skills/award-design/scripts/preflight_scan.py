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
cheapest bleed vector and a closed vocabulary.

Usage:
    python3 preflight_scan.py <path> [<path>...] [--archetype NAME] [--allow RULE-ID]...

`--archetype` applies declared archetype grammar: editorial and
corporate-luxury suppress EMDASH (a deliberate typographic choice there);
brutalist suppresses META-LABEL (ASCII process flags are its register).
`--allow RULE-ID` suppresses a rule for this run — each use requires a
written justification in the pre-flight verdict.

Exit codes: 0 = no FAIL findings, 1 = FAIL findings present, 2 = usage error
or zero files scanned (a wrong path must never read as a clean build).
"""

import argparse
import json
import math
import re
import struct
import sys
from html.parser import HTMLParser
from pathlib import Path

FAIL = "FAIL"
REVIEW = "REVIEW"

# Text-bearing sources (visible copy + markup) vs all scannable sources.
TEXT_EXTS = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro", ".mdx", ".md"}
CODE_EXTS = TEXT_EXTS | {".js", ".ts", ".css", ".scss"}
EXCLUDED_DIRS = {"node_modules", ".git", ".next", ".astro", "coverage", "vendor", "__pycache__",
                 "dist", "build", ".output", ".nuxt", ".svelte-kit", ".vercel"}

# ── Closed-world provenance (CW rules) ──────────────────────────────────────
# The boundary is provenance first, content second: the library's own files
# legitimately carry every machinery pattern, so the machinery rules apply
# only to what the builder wrote. Partition: a file whose basename matches a
# library file is byte-compared (verbatim → exempt; edited → CW-LIB-EDIT — a
# library defect is a defect order, never an edit); a delimiter-chunked bundle
# is checked chunk-by-chunk; declared vendor engines are out of scope; the
# rest is build-authored and the CW rules apply. Excluded dirs are never a
# blind spot for library copies: a library basename is checked wherever it
# ships (an edited nav component once hid under js/vendor/components/).
CW_LIBRARY_DIR = Path(__file__).resolve().parent.parent / "assets" / "components"
CW_BUNDLE_CHUNK_RE = re.compile(r"/\*\s*====\s*([\w-]+)\s*====\s*\*/")
CW_VENDOR_NAME_RE = re.compile(r"^(?:three|lenis|gsap)[.\-]", re.IGNORECASE)
CW_JS_EXTS = {".js", ".mjs", ".html", ".htm"}
CW_CSS_EXTS = {".css", ".scss"}

CW_RULES = [
    ("CW-ENGINE",
     "build-authored engine use (THREE/WebGL/Lenis/GSAP) — worlds and drives come from the "
     "library's covering piece; a missing world is a BLOCKED row, never a from-scratch scene",
     re.compile(r"\bnew\s+THREE\.|import\s+\*\s+as\s+THREE|from\s+['\"]three"
                r"|WebGLRenderer|ShaderMaterial|RawShaderMaterial|BufferGeometry"
                r"|PMREMGenerator|onBeforeCompile"
                r"|getContext\(\s*['\"](?:webgl2?|webgpu)"
                r"|new\s+Lenis\s*\(|gsap\.(?:to|from|fromTo|timeline|set)\s*\("
                r"|ScrollTrigger\.create"), CW_JS_EXTS),
    ("CW-SHADER",
     "build-authored shader code (GLSL) — shader work is library-level only",
     re.compile(r"gl_FragColor|gl_Position|/\*\s*glsl\s*\*/"
                r"|precision\s+(?:high|medium|low)p"
                r"|^\s*uniform\s+(?:float|vec[234]|mat[234]|sampler\w*)"), CW_JS_EXTS),
    ("CW-RAF-LOOP",
     "build-authored requestAnimationFrame loop — drive loops live in library components",
     re.compile(r"requestAnimationFrame\s*\("), CW_JS_EXTS),
    ("CW-CANVAS-DRAW",
     "build-authored canvas drawing — frame engines are library components (scrub-film et al.)",
     re.compile(r"getContext\(\s*['\"]2d|\.drawImage\(|putImageData"
                r"|createElement\(\s*['\"]canvas"), CW_JS_EXTS),
    ("CW-INPUT-DRIVE",
     "build-authored input-drive listener — pointer/scroll/wheel coupling comes from the library",
     re.compile(r"addEventListener\(\s*['\"](?:pointermove|mousemove|touchmove|wheel|scroll"
                r"|pointerenter|pointerleave|mouseenter|mouseleave|pointerdown|touchstart)['\"]"),
     CW_JS_EXTS),
    ("CW-OBSERVER",
     "build-authored observer state machine — IO/RO/MO machinery is a library component",
     re.compile(r"new\s+(?:IntersectionObserver|ResizeObserver|MutationObserver)\b"), CW_JS_EXTS),
    ("CW-STYLE-DRIVE",
     "build-authored per-frame style write — style driving belongs to library components",
     re.compile(r"\.style\.(?:setProperty|transform|left|top|width|height|opacity|display"
                r"|backgroundPosition)\s*[=(]|\.style\["), CW_JS_EXTS),
    ("CW-CSS-BEHAVIOR",
     "build-authored CSS behavior (@keyframes / animation / scroll-timeline) — ambient and "
     "scroll-driven motion ships as library components, never hand CSS",
     re.compile(r"@keyframes|\banimation(?:-name)?\s*:|animation-timeline\s*:|scroll-timeline"),
     CW_CSS_EXTS),
]
CW_RULE_IDS = {rule[0] for rule in CW_RULES} | {"CW-LIB-EDIT"}

CLASS_LIB_VERBATIM = "LIB-VERBATIM"
CLASS_LIB_EDIT = "LIB-EDIT"
CLASS_VENDOR = "VENDOR"
CLASS_BUILD = "BUILD-AUTHORED"


def _load_library_index():
    """basename → list of source texts for every library component/form file."""
    index = {}
    if not CW_LIBRARY_DIR.is_dir():
        return index
    for path in sorted(CW_LIBRARY_DIR.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".js", ".css"}:
            try:
                index.setdefault(path.name, []).append(
                    path.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                continue
    return index


def _classify_provenance(path, text, lib_index):
    """Returns (class, mismatched_chunk_ids). Order matters: a library
    basename wins over a vendor path (the hidden-copy lesson)."""
    if path.name in lib_index:
        if any(text == src for src in lib_index[path.name]):
            return CLASS_LIB_VERBATIM, []
        return CLASS_LIB_EDIT, []
    parts = CW_BUNDLE_CHUNK_RE.split(text)
    if len(parts) >= 3:
        bad = []
        for i in range(1, len(parts) - 1, 2):
            chunk_id, body = parts[i], parts[i + 1]
            sources = (lib_index.get(chunk_id + ".js", [])
                       + lib_index.get(chunk_id + ".css", []))
            if not any(body.strip() == src.strip() for src in sources):
                bad.append(chunk_id)
        return (CLASS_LIB_EDIT, bad) if bad else (CLASS_LIB_VERBATIM, [])
    if (any(part.lower() == "vendor" for part in path.parts)
            or CW_VENDOR_NAME_RE.match(path.name)):
        return CLASS_VENDOR, []
    return CLASS_BUILD, []

# ── Tooling gates — static proxies (REVIEW-only: a proxy never FAILs on a guess) ──
# EASE-OVERSHOOT: the page runs ONE declared motion register (decelerating-
# mechanical, playful-elastic, or cinematic — the effect-grammar verdict). The
# scanner cannot read the DESIGN.md (excluded), so it names every overshoot/
# elastic curve in build-authored code for the reviewer to judge against the
# declared register. Provenance-gated like the CW rules: the library's own
# easing tokens never re-litigate the library.
EASE_RULE_ID = "EASE-OVERSHOOT"
EASE_EXTS = CW_JS_EXTS | CW_CSS_EXTS
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


def _img_native_res_findings(texts, classes, roots):
    findings = []
    groups = {}     # (file, stem) → {floor, signal, loc, paths}
    seq_seen = set()      # resolved dirs already walked
    seq_emitted = set()   # (parent, prefix) groups already reported
    for path, text in sorted(texts.items()):
        if classes.get(path) != CLASS_BUILD:
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
    # Library components inject their CSS from JS strings and form stylesheets ship
    # zero decoration, so any .css file that SELECTS a component role class is build
    # CSS re-styling a role the library already owns — the class-role drift that put
    # two hover verbs on one primary label (CALDERA close vs arrival).
    ("ROLE-RESTYLE", FAIL,
     "build CSS styles a library component role (.ad-* / .is-primary) — the role's "
     "treatment comes from its library instance, page-wide; a section or form never "
     "redefines it, in class, attribute-substring, or selector-list form "
     "(class-role uniformity)",
     # Three branches: role class with the brace on the line; role class on a
     # selector-list line (trailing comma — CALDERA's `.is-primary:hover,`);
     # attribute-substring selection of a role class ([class*="ad-"]). `\\?`
     # tolerates the CSS-escaped hyphen dodge (.ad\-cta); the lookbehind keeps
     # [class*="grad-"] and [class*="-ad-"] silent.
     re.compile(r"\.(?:ad\\?-[a-z][\w\\-]*|is\\?-primary)\b[^{}]*(?:\{|,\s*$)"
                r"|\[\s*class\s*[~^$*|]?=\s*['\"]?(?<![\w-])(?:ad-|is-primary)"),
     {".css", ".scss"}),
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
# Markup-side signature only: a stylesheet's `text-transform: uppercase`
# defines a treatment once, so counting it can never register a removed
# eyebrow. Vanilla-CSS eyebrows escape this count (false-negative bias) —
# the pre-flight box still judges the rendered page.
EYEBROW_SIGNATURE = re.compile(
    r"uppercase[^\"'`]*tracking-|tracking-\[[^\]]*\][^\"'`]*uppercase")
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


_LIB_INDEX_CACHE = None


def _library_index():
    global _LIB_INDEX_CACHE
    if _LIB_INDEX_CACHE is None:
        _LIB_INDEX_CACHE = _load_library_index()
    return _LIB_INDEX_CACHE


def iter_files(paths):
    lib_names = _library_index().keys()
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
            # A library basename is provenance-checked wherever it ships —
            # excluded dirs never hide an edited copy (the js/vendor lesson).
            if (any(part in EXCLUDED_DIRS for part in path.relative_to(root).parts[:-1])
                    and path.name not in lib_names):
                continue
            # DESIGN.md is the spec, not the build — its Don'ts legitimately
            # quote banned phrases as prohibitions and would never scan clean.
            if path.name == "DESIGN.md":
                continue
            if path.is_file() and path.suffix.lower() in CODE_EXTS:
                yield path


PROJECT_RULE_IDS = {"EMDASH", "H1-COUNT", "MAIN-LANDMARK", "REDUCED-MOTION", "EYEBROW-DENSITY",
                    "FONT-COUNT", "STAMP", "COPY-LANG", "FORM-SLOT"}


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
# Rules that fire only when their precondition is met (an argument passed), so
# they are not expected on a bare dirty-fixture scan — registered for the
# checklist lockstep, exempt from the "fires on dirty" net.
CONDITIONAL_RULE_IDS = {"STAMP-ARCHETYPE-MISMATCH"}


def known_rule_ids():
    return ({rule[0] for rule in LINE_RULES} | PROJECT_RULE_IDS | CONDITIONAL_RULE_IDS
            | CW_RULE_IDS | {EASE_RULE_ID, IMG_RULE_ID})


def scan_paths(paths, archetype="", allow=()):
    """Returns (findings, suppressed) — findings is a list of Finding."""
    suppressed = {rule_id.upper() for rule_id in allow}
    for rule_id in sorted(suppressed - known_rule_ids()):
        print(f"warning: --allow {rule_id} matches no rule (typo?)", file=sys.stderr)
    suppression_notes = [f"{rid} (--allow)" for rid in sorted(suppressed)]
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

    # Closed-world provenance partition — classification precedes content rules.
    lib_index = _library_index()
    classes = {}
    for path, text in texts.items():
        cls, bad_chunks = _classify_provenance(path, text, lib_index)
        classes[path] = cls
        if cls == CLASS_LIB_EDIT and "CW-LIB-EDIT" not in suppressed:
            edit_description = ("edited library copy — ship the library file verbatim; a library "
                               "defect is a defect order + a justified --allow note, never an edit "
                               "(closed-world)")
            if bad_chunks:
                for chunk_id in bad_chunks:
                    findings.append(Finding(
                        "CW-LIB-EDIT", FAIL, edit_description, str(path),
                        f"bundle chunk `{chunk_id}` differs from the library source"))
            else:
                findings.append(Finding(
                    "CW-LIB-EDIT", FAIL, edit_description, str(path),
                    f"content differs from the library's {path.name}"))

    emdash_count = 0
    emdash_hits = []
    text_words = 0

    for path, text in texts.items():
        ext = path.suffix.lower()
        cls = classes.get(path, CLASS_BUILD)
        if cls in (CLASS_VENDOR, CLASS_LIB_VERBATIM):
            # Vendor engines are out of scope; verbatim library copies are
            # gated at library level — scanning them re-litigates the library
            # (the SCROLL-LISTENER / injected-CSS false-positive class). They
            # stay in the project blob, so guard detection still sees them.
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
            if cls == CLASS_BUILD:
                for rule_id, description, pattern, exts in CW_RULES:
                    if rule_id in suppressed or ext not in exts:
                        continue
                    if pattern.search(line):
                        findings.append(Finding(
                            rule_id, FAIL, description,
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
        findings.extend(_img_native_res_findings(texts, classes, dir_roots))

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
    parser.add_argument("--allow", action="append", default=[], metavar="RULE-ID",
                        help="suppress a rule for this run (repeatable; justify in the verdict)")
    args = parser.parse_args(argv)

    files = list(iter_files(args.paths))
    # scan_paths gets the raw paths, not the file list — directory roots anchor
    # root-relative image refs (IMG-NATIVE-RES); it re-derives the same files.
    findings, suppression_notes = scan_paths(args.paths, args.archetype, args.allow)
    print(format_report(findings, suppression_notes, files))
    if not files:
        return 2
    return 1 if any(f.severity == FAIL for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
