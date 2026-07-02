#!/usr/bin/env python3
"""Validate an animated SVG for self-contained, no-JS delivery.

Profiles:
  readme (default) — <img>/camo context (GitHub READMEs, registry pages):
    scripts never execute, external resources never load, pointer events
    never fire. Violations of self-containment FAIL.
  web — inline-on-page use: same checks, but external references and
    interactivity downgrade to WARN.

Output: one `RESULT: check=<id> status=<pass|warn|fail> detail=<text>` line
per check, then `RESULT: verdict=<pass|fail> fails=<n> warns=<n>`.

Exit 0 = no FAIL. Exit 1 = at least one FAIL. Exit 2 = unreadable input
(the run stops at the failing parse line, no verdict line).
"""

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_HREF = "{http://www.w3.org/1999/xlink}href"
SMIL_ANIMATE_TAGS = {"animate", "animateTransform", "animateMotion"}
SMIL_TAGS = SMIL_ANIMATE_TAGS | {"set"}
URL_ATTRS = {"href", XLINK_HREF, "src"}
# Anything that is not an internal #id or an inline data: URI needs a fetch —
# relative paths and file:/http(s) alike never resolve in <img> context.
INTERNAL_REF = re.compile(r"^\s*(#|data:)", re.IGNORECASE)
CSS_URL = re.compile(r"url\(\s*['\"]?([^'\")]+)", re.IGNORECASE)
README_SIZE_WARN_KB = 200
WEB_SIZE_WARN_KB = 500


def localname(tag):
    return tag.rsplit("}", 1)[-1]


def walk(root):
    yield root
    for child in root:
        yield from walk(child)


def collect_css(root):
    """All CSS the document carries: <style> bodies + style="" attributes."""
    chunks = []
    for el in walk(root):
        if localname(el.tag) == "style" and el.text:
            chunks.append(el.text)
        inline = el.get("style")
        if inline:
            chunks.append(inline)
    return "\n".join(chunks)


def check_viewbox(root, css, profile):
    if root.get("viewBox"):
        return "pass", f"viewBox=\"{root.get('viewBox')}\""
    return "fail", "no viewBox — the SVG cannot scale predictably when embedded"


def check_animation_present(root, css, profile):
    smil = sorted({localname(el.tag) for el in walk(root) if localname(el.tag) in SMIL_ANIMATE_TAGS})
    has_set = any(localname(el.tag) == "set" for el in walk(root))
    has_css_anim = "@keyframes" in css
    if smil and has_css_anim:
        return "pass", f"SMIL ({', '.join(smil)}) + CSS @keyframes"
    if smil:
        return "pass", f"SMIL ({', '.join(smil)})"
    if has_css_anim:
        return "pass", "CSS @keyframes"
    if has_set:
        return "fail", "only <set> found — a discrete value flip, not an animation"
    return "fail", "no SMIL element and no @keyframes — this SVG does not animate"


def check_no_script(root, css, profile):
    offenders = []
    for el in walk(root):
        if localname(el.tag) == "script":
            offenders.append("<script>")
        for attr, value in el.attrib.items():
            if localname(attr).lower().startswith("on"):
                offenders.append(f"{localname(attr)}=")
            if attr in URL_ATTRS and value.strip().lower().startswith("javascript:"):
                offenders.append("javascript: href")
    if offenders:
        return "fail", f"JS never runs in <img> context: {', '.join(sorted(set(offenders)))}"
    return "pass", "no <script>, no event handlers"


def check_self_contained(root, css, profile):
    offenders = []
    for el in walk(root):
        for attr, value in el.attrib.items():
            if attr in URL_ATTRS:
                if value and not INTERNAL_REF.match(value):
                    offenders.append(f"<{localname(el.tag)} {localname(attr)}=\"{value[:40]}\">")
            elif attr != "style":  # style attrs are already in the collected CSS
                # url() is legal in presentation attributes too (fill, filter,
                # mask, clip-path, marker-*) — same fetch, same failure in <img>
                for match in CSS_URL.finditer(value):
                    if not INTERNAL_REF.match(match.group(1)):
                        offenders.append(f"<{localname(el.tag)} {localname(attr)}=url({match.group(1)[:40]})>")
    for match in CSS_URL.finditer(css):
        if not INTERNAL_REF.match(match.group(1)):
            offenders.append(f"css url({match.group(1)[:40]})")
    if "@import" in css:
        offenders.append("css @import")
    if not offenders:
        return "pass", "all references are internal (#id) or data: URIs"
    detail = f"fetched references never resolve in <img> context: {', '.join(sorted(set(offenders)))}"
    return ("fail" if profile == "readme" else "warn"), detail


def check_fonts(root, css, profile):
    has_text = any(localname(el.tag) in ("text", "tspan") for el in walk(root))
    if not has_text:
        return "pass", "no <text> — glyphs are paths"
    if profile == "web":
        return "warn", ("<text> present — ensure the embedding page provides the font, "
                        "or convert text to paths")
    return "warn", ("<text> present — custom fonts do not load in <img> context; "
                    "convert text to paths or accept system-font variance")


def check_reduced_motion(root, css, profile):
    if "@keyframes" not in css:
        has_smil = any(localname(el.tag) in SMIL_ANIMATE_TAGS for el in walk(root))
        if has_smil:
            return "pass", "SMIL-only — not media-gateable; keep amplitude modest"
        return "pass", "no animation to gate"
    if "prefers-reduced-motion" in css:
        return "pass", "prefers-reduced-motion gate present"
    return "warn", "CSS animations without a prefers-reduced-motion gate"


def check_interactivity(root, css, profile):
    triggers = []
    if re.search(r":(hover|active|focus)", css):
        triggers.append("css :hover/:active/:focus")
    for el in walk(root):
        begin = el.get("begin", "")
        if any(ev in begin for ev in ("click", "activate", "mouseover", "mouseout",
                                      "mousedown", "mouseup", "mousemove", "focus")):
            triggers.append(f"begin=\"{begin}\"")
    if not triggers:
        return "pass", "animation is autonomous"
    if profile == "web":
        return "pass", (f"interactive triggers valid for inline embedding: "
                        f"{', '.join(sorted(set(triggers)))}")
    detail = f"pointer events never fire in <img> context: {', '.join(sorted(set(triggers)))}"
    return "warn", detail


def check_size(path, profile):
    kb = path.stat().st_size / 1024
    budget = README_SIZE_WARN_KB if profile == "readme" else WEB_SIZE_WARN_KB
    status = "pass" if kb <= budget else "warn"
    return status, f"{kb:.1f} KB (soft budget {budget} KB)"


def check_a11y(root, css, profile):
    first_children = [localname(el.tag) for el in list(root)]
    if "title" in first_children:
        return "pass", "<title> present"
    return "warn", "no <title> child on the root — screen readers announce nothing"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path)
    parser.add_argument("-p", "--profile", choices=("readme", "web"), default="readme")
    args = parser.parse_args()

    if not args.svg.is_file():
        print(f"RESULT: check=parse status=fail detail=not a file: {args.svg}")
        return 2
    try:
        root = ET.fromstring(args.svg.read_text(encoding="utf-8"))
    except (ET.ParseError, UnicodeDecodeError) as exc:
        print(f"RESULT: check=parse status=fail detail=not well-formed XML: {exc}")
        return 2
    if localname(root.tag) != "svg" or SVG_NS not in root.tag:
        print(f"RESULT: check=parse status=fail detail=root is <{localname(root.tag)}>, "
              f"expected <svg xmlns=\"{SVG_NS}\">")
        return 2
    print("RESULT: check=parse status=pass detail=well-formed SVG with xmlns")

    css = collect_css(root)
    checks = (
        ("viewbox", check_viewbox),
        ("animation-present", check_animation_present),
        ("no-script", check_no_script),
        ("self-contained", check_self_contained),
        ("fonts", check_fonts),
        ("reduced-motion", check_reduced_motion),
        ("interactivity", check_interactivity),
        ("a11y-title", check_a11y),
    )
    fails = warns = 0
    for check_id, fn in checks:
        status, detail = fn(root, css, args.profile)
        fails += status == "fail"
        warns += status == "warn"
        print(f"RESULT: check={check_id} status={status} detail={detail}")

    status, detail = check_size(args.svg, args.profile)
    warns += status == "warn"
    print(f"RESULT: check=size status={status} detail={detail}")

    verdict = "fail" if fails else "pass"
    print(f"RESULT: verdict={verdict} fails={fails} warns={warns}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
