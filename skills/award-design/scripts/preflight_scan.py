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
import math
import re
import sys
from pathlib import Path

FAIL = "FAIL"
REVIEW = "REVIEW"

# Text-bearing sources (visible copy + markup) vs all scannable sources.
TEXT_EXTS = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro", ".mdx", ".md"}
CODE_EXTS = TEXT_EXTS | {".js", ".ts", ".css", ".scss"}
EXCLUDED_DIRS = {"node_modules", ".git", ".next", ".astro", "coverage", "vendor", "__pycache__",
                 "dist", "build", ".output", ".nuxt", ".svelte-kit", ".vercel"}

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
                    "FONT-COUNT", "STAMP", "COPY-LANG"}
# Rules that fire only when their precondition is met (an argument passed), so
# they are not expected on a bare dirty-fixture scan — registered for the
# checklist lockstep, exempt from the "fires on dirty" net.
CONDITIONAL_RULE_IDS = {"STAMP-ARCHETYPE-MISMATCH"}


def known_rule_ids():
    return {rule[0] for rule in LINE_RULES} | PROJECT_RULE_IDS | CONDITIONAL_RULE_IDS


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
    texts = {}
    for path in files:
        try:
            texts[path] = path.read_text(encoding="utf-8", errors="replace")
        except OSError as err:
            print(f"warning: unreadable, skipped: {path} ({err})", file=sys.stderr)

    project_blob = "\n".join(texts.values())
    has_focus_visible = bool(FOCUS_VISIBLE.search(project_blob))

    emdash_count = 0
    emdash_hits = []
    text_words = 0

    for path, text in texts.items():
        ext = path.suffix.lower()
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
    findings, suppression_notes = scan_paths(files, args.archetype, args.allow)
    print(format_report(findings, suppression_notes, files))
    if not files:
        return 2
    return 1 if any(f.severity == FAIL for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
