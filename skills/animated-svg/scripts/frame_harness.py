#!/usr/bin/env python3
"""Generate frozen-frame HTML harness pages for an animated SVG.

Each page inlines the SVG and freezes every animation at one timestamp —
SMIL via `pauseAnimations()` + `setCurrentTime()`, CSS/WAAPI via
`document.getAnimations()`. Screenshot each page with any browser tool to
turn "the animation looks right" into reviewable stills. The harness uses
JS to freeze time; the SVG under test stays JS-free.

Output: one `RESULT: frame=<abs path> t=<seconds>` line per page.

Exit 0 = pages written. Exit 2 = unreadable input or invalid times.
"""

import argparse
import sys
from pathlib import Path

PAGE = """<!doctype html>
<meta charset="utf-8">
<title>frame @ {t}s — {name}</title>
<style>
  html, body {{ margin: 0; }}
  body {{ background: {bg}; display: grid; place-items: center; min-height: 100vh; }}
  #stage svg {{ width: {size}px; height: auto; display: block; }}
</style>
<div id="stage">{svg}</div>
<script>
  const T = {t};
  const svg = document.querySelector("#stage svg");
  if (svg && svg.pauseAnimations) {{ svg.pauseAnimations(); svg.setCurrentTime(T); }}
  if (document.getAnimations) {{
    for (const a of document.getAnimations()) {{
      a.pause();
      try {{ a.currentTime = T * 1000; }} catch (_) {{}}
    }}
  }}
</script>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path)
    parser.add_argument("-t", "--times", required=True,
                        help="comma-separated seconds, e.g. 0,0.8,1.6,2.4")
    parser.add_argument("-o", "--out", type=Path, required=True,
                        help="output directory for the harness pages")
    parser.add_argument("--size", type=int, default=800, help="stage width in px")
    parser.add_argument("--bg", default="#ffffff",
                        help="page background (e.g. #0d1117 for a dark pass)")
    args = parser.parse_args()

    if not args.svg.is_file():
        print(f"RESULT: error=not a file: {args.svg}")
        return 2
    try:
        times = [float(t) for t in args.times.split(",") if t.strip()]
    except ValueError:
        print(f"RESULT: error=invalid --times: {args.times}")
        return 2
    if not times or any(t < 0 for t in times):
        print(f"RESULT: error=--times must be non-negative seconds: {args.times}")
        return 2
    times = list(dict.fromkeys(times))

    try:
        svg_markup = args.svg.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        print(f"RESULT: error=not readable as UTF-8 SVG: {exc}")
        return 2
    try:
        args.out.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"RESULT: error=cannot create output dir: {exc}")
        return 2
    for t in times:
        page = args.out / f"frame-t{t:g}.html"
        try:
            page.write_text(
                PAGE.format(t=t, name=args.svg.name, bg=args.bg, size=args.size,
                            svg=svg_markup),
                encoding="utf-8",
            )
        except OSError as exc:
            print(f"RESULT: error=cannot write page: {exc}")
            return 2
        print(f"RESULT: frame={page.resolve()} t={t:g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
