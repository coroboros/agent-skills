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

Usage:
    python3 preflight_scan.py <path> [<path>...] [--archetype NAME] [--allow RULE-ID]...

`--archetype` applies declared archetype grammar: editorial and
corporate-luxury suppress EMDASH (a deliberate typographic choice there);
brutalist suppresses META-LABEL (ASCII process flags are its register).
`--allow RULE-ID` suppresses a rule for this run — each use requires a
written justification in the pre-flight verdict.

Exit codes: 0 = no FAIL findings, 1 = FAIL findings present, 2 = usage error.
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

# Line rules: (id, severity, description, pattern, extensions).
LINE_RULES = [
    ("AI-PURPLE", FAIL,
     "banned AI-purple hex (#a855f7 / #8b5cf6 / #ec4899 / #6366f1)",
     re.compile(r"#(?:a855f7|8b5cf6|ec4899|6366f1)\b", re.IGNORECASE), CODE_EXTS),
    ("PURE-BW", FAIL,
     "pure #000 / #fff (or bg-black / text-white) — use off-blacks and off-whites",
     re.compile(
         r"(?i)(?:color|background(?:-color)?|fill|stroke|border(?:-[a-z]+)*|outline|"
         r"box-shadow|text-shadow)\s*:\s*[^;{}\n]*#(?:000000|000|fff|ffffff)\b"
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
     "index meta-label (SECTION 01 / STEP 2 / PHASE 03) — name the topic, not the count",
     re.compile(r"\b(?:SECTION|QUESTION|STAGE|STEP|PHASE|PASS)\s?0?\d\b"), TEXT_EXTS),
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
                    "FONT-COUNT"}


def known_rule_ids():
    return {rule[0] for rule in LINE_RULES} | PROJECT_RULE_IDS


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

    return findings, suppression_notes


def format_report(findings, suppression_notes):
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

    findings, suppression_notes = scan_paths(args.paths, args.archetype, args.allow)
    print(format_report(findings, suppression_notes))
    return 1 if any(f.severity == FAIL for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
