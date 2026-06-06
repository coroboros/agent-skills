#!/usr/bin/env python3
"""Measure stylometric stats from a prose corpus to ground `sentence_norms`.

Reads a corpus (file or stdin); ``--as-sentence-norms`` emits a ``sentence_norms``
dict, or ``null`` below the threshold so the caller keeps its LLM/interview default.
Stdlib only, deterministic (sorted keys, no RNG).

Segmentation is a heuristic, not a parser — the p10/p90 bounds are used precisely
because percentiles absorb the occasional mis-split.

Detector asymmetry: em_dash/oxford are omitted when the corpus shows no signal
(absence is not prohibition); contractions/exclamation carry only allow|forbid, so a
corpus past the threshold that never uses them reads as forbidding — overridable.
"""
import argparse
import json
import math
import re
import statistics
import sys

DEFAULT_THRESHOLD = 30  # sentences below this → not enough signal to measure

_FENCED_CODE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE = re.compile(r"`[^`]*`")
_URL = re.compile(r"https?://\S+")
_HEADING_LINE = re.compile(r"^[ \t]*#{1,6}[ \t].*$", re.MULTILINE)
# trailing space keeps "1. item" (marker) distinct from "1.5 million" (decimal)
_LEADING_MARKER = re.compile(r"^[ \t]*(?:[>*+\-|]+|\d+\.)[ \t]+", re.MULTILINE)
_ABBREV = ("e.g.", "i.e.", "etc.", "vs.", "Mr.", "Mrs.", "Ms.", "Dr.", "St.",
           "Inc.", "Ltd.", "No.")
# Can end a sentence: keep the split when a capital follows ("etc. Then"). The
# connectives/titles above are mid-sentence, so their period is always protected.
_FINAL_PRONE = ("etc.", "Inc.", "Ltd.", "No.")
_CAP_FOLLOWS = r"(?!\s+[A-Z])"
_ELLIPSIS = re.compile(r"\.{2,}")
_WORD = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?")
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
# 's is excluded: possessive ("reader's") is indistinguishable from the "it's"
# contraction without POS tagging, and possessives are far more common — counting
# them would make "forbid" almost never fire. The other suffixes are unambiguous.
_CONTRACTION = re.compile(r"\b[A-Za-z]+'(?:t|re|ve|ll|d|m)\b", re.IGNORECASE)
_LIST_CONJ = re.compile(r"\b(?:and|or|nor)\b", re.IGNORECASE)
_EM_DASH = "—"
_PROTECT = "\x01"  # control-char sentinel for periods that must not end a sentence


def _strip_noise(text):
    """Drop code, URLs, and markdown structure so only prose is measured."""
    text = _FENCED_CODE.sub(" ", text)
    text = _INLINE_CODE.sub(" ", text)
    text = _URL.sub(" ", text)
    text = _HEADING_LINE.sub(" ", text)
    text = _LEADING_MARKER.sub(" ", text)
    return text


def _sentences(text):
    # Drop any pre-existing sentinel so the restore step can't corrupt real input.
    protected = text.replace(_PROTECT, "")
    # Protect ellipses ("Wait... what" is one sentence, not two).
    protected = _ELLIPSIS.sub(lambda m: _PROTECT * len(m.group()), protected)
    # Protect abbreviation periods (see _FINAL_PRONE for the capital-follows split).
    for ab in _ABBREV:
        repl = ab.replace(".", _PROTECT)
        if ab in _FINAL_PRONE:
            protected = re.sub(re.escape(ab) + _CAP_FOLLOWS, repl, protected)
        else:
            protected = protected.replace(ab, repl)
    # Protect decimals (3.14) from splitting.
    protected = re.sub(r"(\d)\.(\d)", r"\1" + _PROTECT + r"\2", protected)
    out = []
    for part in _SENT_SPLIT.split(protected):
        part = part.replace(_PROTECT, ".").strip()
        if part and _WORD.search(part):
            out.append(part)
    return out


def _percentile(sorted_vals, pct):
    """Linear-interpolation percentile, rounded to int. Deterministic."""
    if not sorted_vals:
        return 0
    if len(sorted_vals) == 1:
        return int(sorted_vals[0])
    k = (len(sorted_vals) - 1) * pct / 100.0
    f, c = math.floor(k), math.ceil(k)
    if f == c:
        return int(sorted_vals[int(k)])
    return int(round(sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f)))


def _em_dash_spacing(text):
    spaced = tight = 0
    for m in re.finditer(_EM_DASH, text):
        i = m.start()
        left = text[i - 1] if i > 0 else ""
        right = text[i + 1] if i + 1 < len(text) else ""
        if left == " " and right == " ":
            spaced += 1
        else:
            tight += 1
    if spaced + tight == 0:
        return None
    return "spaced" if spaced >= tight else "tight"


def _oxford_comma(sents):
    """True when the corpus prefers a serial comma, None when no list signal.

    A serial ("Oxford") comma sits immediately before the conjunction closing a
    list of three or more items: ``A, B, and C`` (≥ 2 commas in the run). The
    counter-signal is the same list without it: ``A, B and C``. A lone comma before
    a conjunction joining two clauses (``home, and we slept``) is not a list — one
    comma, conjunction comma-attached — and is ignored.
    """
    oxford = plain = 0
    for sent in sents:
        for m in _LIST_CONJ.finditer(sent):
            commas_before = sent[:m.start()].count(",")
            if sent[:m.start()].rstrip().endswith(","):
                if commas_before >= 2:        # "A, B, and …" — serial comma, 3+ items
                    oxford += 1
            elif commas_before >= 1:          # "A, B and …" — list without the serial comma
                plain += 1
    if oxford + plain == 0:
        return None
    return oxford >= plain


def measure(text):
    clean = _strip_noise(text)
    sents = _sentences(clean)
    counts = sorted(c for c in (len(_WORD.findall(s)) for s in sents) if c > 0)
    word_counts = {
        "min": counts[0] if counts else 0,
        "p10": _percentile(counts, 10),
        "median": int(statistics.median(counts)) if counts else 0,
        "p90": _percentile(counts, 90),
        "max": counts[-1] if counts else 0,
    }
    return {
        "sentence_count": len(sents),
        "word_counts": word_counts,
        "conventions": {
            "em_dash_spacing": _em_dash_spacing(clean),
            "oxford_comma": _oxford_comma(sents),
            "contractions": "allow" if _CONTRACTION.search(clean) else "forbid",
            "exclamation_marks": "allow" if "!" in clean else "forbid",
        },
    }


def to_sentence_norms(stats, threshold=DEFAULT_THRESHOLD):
    """Map measured stats to a sentence_norms dict, or None when too thin.

    None tells the caller to keep LLM/interview defaults — never fabricate
    bounds from an under-threshold corpus. The clamp guarantees
    ``word_count_min >= 1`` and ``word_count_min <= word_count_max <= sentence_max_hard``,
    the ordering voice_lint requires (it accepts ``min == max``, so the clamp need
    only preserve the ``<=`` chain, not strict inequality).
    """
    if stats["sentence_count"] < threshold:
        return None
    wc = stats["word_counts"]
    wmin = max(1, wc["p10"])
    wmax = max(wmin, wc["p90"])
    whard = max(wmax, wc["max"])
    norms = {
        "word_count_min": wmin,
        "word_count_max": wmax,
        "sentence_max_hard": whard,
        "contractions": stats["conventions"]["contractions"],
        "exclamation_marks": stats["conventions"]["exclamation_marks"],
    }
    em = stats["conventions"]["em_dash_spacing"]
    if em is not None:
        norms["em_dash_spacing"] = em
    ox = stats["conventions"]["oxford_comma"]
    if ox is not None:
        norms["oxford_comma"] = ox
    return norms


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Measure stylometric stats from a prose corpus.")
    ap.add_argument("path", nargs="?",
                    help="corpus file; reads stdin when omitted")
    ap.add_argument("--as-sentence-norms", action="store_true",
                    help="emit a sentence_norms dict (or null below threshold)")
    ap.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD,
                    help=f"min sentences to measure (default {DEFAULT_THRESHOLD})")
    args = ap.parse_args(argv)

    try:
        if args.path:
            with open(args.path, encoding="utf-8") as fh:
                text = fh.read()
        else:
            text = sys.stdin.read()
    except OSError as exc:
        print(f"measure_corpus: cannot read input: {exc}", file=sys.stderr)
        return 2

    if not text.strip():
        print("measure_corpus: empty input", file=sys.stderr)
        return 2

    stats = measure(text)
    result = to_sentence_norms(stats, args.threshold) if args.as_sentence_norms else stats
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
