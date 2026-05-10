"""Tests for brand_prescan.py — YAML loading, brand-pattern detectors,
whitelist behaviour, and the scan_brand() integration."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "skills" / "humanize-en" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from brand_prescan import (  # noqa: E402
    DEFAULT_ACRONYM_WHITELIST,
    DEFAULT_COMPOUND_IDIOM_WHITELIST,
    detect_all_caps_emphasis,
    detect_emoji,
    detect_first_person_plural,
    detect_first_person_singular,
    detect_forbidden_lexicon,
    detect_negative_parallelism,
    detect_rewrite_rule_rejects,
    detect_rhetorical_questions,
    detect_rule_of_three_heading,
    detect_second_person,
    detect_signposting,
    load_brand_rules,
    merge_lexical_exceptions,
    parse_yaml_minimal,
    scan_brand,
)
from prescan import mask_protected_regions  # noqa: E402

PRESCAN_SCRIPT = SCRIPTS / "prescan.py"


def _voice_doc(yaml_body):
    """Wrap a YAML body in a minimal valid BRAND-VOICE.md scaffold."""
    return f"---\n{yaml_body.strip()}\n---\n\n# Brand Voice — Test\n\n## 1. Core voice attributes\nstub\n"


class TestParseYamlMinimal(unittest.TestCase):
    def test_parses_lists_of_strings(self):
        data = parse_yaml_minimal("foo:\n  - a\n  - b\n")
        self.assertEqual(data, {"foo": ["a", "b"]})

    def test_parses_nested_dict(self):
        data = parse_yaml_minimal("voice:\n  name: \"X\"\n  forbid:\n    - a\n")
        self.assertEqual(data["voice"]["name"], "X")
        self.assertEqual(data["voice"]["forbid"], ["a"])

    def test_parses_list_of_objects(self):
        data = parse_yaml_minimal(
            "rules:\n  - reject: \"a\"\n    accept: \"b\"\n    rule_id: r1\n"
        )
        self.assertEqual(data["rules"], [{"reject": "a", "accept": "b", "rule_id": "r1"}])

    def test_hash_inside_quoted_value_preserved(self):
        """A `#` inside a quoted string is NOT a comment — must survive parsing.
        URLs with anchors and color hex codes routinely contain `#`."""
        data = parse_yaml_minimal('url: "https://example.com/page#section"\n')
        self.assertEqual(data["url"], "https://example.com/page#section")

    def test_hash_at_word_boundary_strips_comment(self):
        """`key: value  # comment` — comment is stripped."""
        data = parse_yaml_minimal("key: value  # this is a comment\n")
        self.assertEqual(data["key"], "value")

    def test_hash_inside_single_quoted_preserved(self):
        data = parse_yaml_minimal("color: '#ff0000'\n")
        self.assertEqual(data["color"], "#ff0000")

    def test_invalid_yaml_raises_value_error(self):
        # Inconsistent indent under a parent — parse_map raises with
        # "unexpected indent (got N, want M)".
        with self.assertRaises(ValueError):
            parse_yaml_minimal("foo:\n  bar: baz\n   wrong: indent\n")

    def test_yaml_parse_error_carries_line_number(self):
        """ValueError must carry a `.line` attribute (1-indexed) so callers can
        surface the offending line. Mirrors brand-voice/utils.py contract."""
        try:
            parse_yaml_minimal("foo:\n  bar: baz\n   wrong: indent\n")
        except ValueError as exc:
            self.assertTrue(hasattr(exc, "line"),
                            "ValueError from parse_yaml_minimal must have .line")
            self.assertEqual(exc.line, 3,
                             "the wrong-indent line is line 3 (1-indexed)")
        else:
            self.fail("parse_yaml_minimal did not raise on bad indent")

    def test_yaml_float_parsed_as_float(self):
        """Float scalars must coerce to float — parity with brand-voice parser."""
        data = parse_yaml_minimal("threshold: 0.95\nratio: -1.5\n")
        self.assertEqual(data["threshold"], 0.95)
        self.assertEqual(data["ratio"], -1.5)
        self.assertIsInstance(data["threshold"], float)
        self.assertIsInstance(data["ratio"], float)


class TestLoadBrandRules(unittest.TestCase):
    def test_returns_dict_for_valid_voice(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(_voice_doc("voice:\n  name: \"Test\"\nforbidden_lexicon:\n  - foo\n"))
            path = f.name
        try:
            rules = load_brand_rules(path)
            self.assertEqual(rules.get("voice", {}).get("name"), "Test")
            self.assertEqual(rules.get("forbidden_lexicon"), ["foo"])
        finally:
            Path(path).unlink()

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            load_brand_rules("/tmp/_does_not_exist_xyz.md")

    def test_load_brand_rules_strips_utf8_bom(self):
        """Editors that save BRAND-VOICE.md with a UTF-8 BOM (U+FEFF prefix)
        must not silently break frontmatter detection. Without BOM stripping,
        the leading `\\ufeff---` would not match `---` and load_brand_rules
        would return an empty dict — a silent failure mode."""
        bom = "﻿"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md",
                                          delete=False, encoding="utf-8") as f:
            f.write(bom + _voice_doc("voice:\n  name: \"BomTest\"\n"
                                      "forbidden_lexicon:\n  - \"foo\"\n"))
            path = f.name
        try:
            rules = load_brand_rules(path)
            self.assertEqual(rules.get("voice", {}).get("name"), "BomTest",
                             "BOM-prefixed YAML must still parse")
            self.assertEqual(rules.get("forbidden_lexicon"), ["foo"])
        finally:
            Path(path).unlink()


class TestLexicalExceptionsMerge(unittest.TestCase):
    def test_default_whitelists_present(self):
        acronyms, idioms = merge_lexical_exceptions({})
        self.assertIn("BPM", acronyms)
        self.assertIn("API", acronyms)
        self.assertIn("MIDI", acronyms)
        self.assertIn("in-your-face", idioms)
        self.assertIn("do-it-yourself", idioms)

    def test_voice_extends_whitelist(self):
        acronyms, _ = merge_lexical_exceptions(
            {"lexical_exceptions": {"acronyms": ["FOO", "BAR"]}}
        )
        self.assertIn("FOO", acronyms)
        self.assertIn("BAR", acronyms)
        # Defaults still present
        self.assertIn("BPM", acronyms)

    def test_compound_idiom_lowercased(self):
        _, idioms = merge_lexical_exceptions(
            {"lexical_exceptions": {"compound_idioms": ["Pay-As-You-Go"]}}
        )
        self.assertIn("pay-as-you-go", idioms)

    def test_skips_non_string_entries(self):
        """Defensive: malformed YAML may inject non-string values (ints, None,
        empty strings). The merger must skip them without crashing."""
        acronyms, idioms = merge_lexical_exceptions({
            "lexical_exceptions": {
                "acronyms": ["FOO", 123, None, ""],
                "compound_idioms": ["a-b", 42, None, ""],
            }
        })
        self.assertIn("FOO", acronyms)
        self.assertNotIn("", acronyms)
        self.assertIn("a-b", idioms)
        self.assertNotIn("", idioms)
        # Non-strings are silently dropped — count matches expected
        self.assertEqual(sum(1 for a in acronyms if not isinstance(a, str)), 0)

    def test_non_dict_lexical_exceptions_falls_back_to_defaults(self):
        """If lexical_exceptions is not a dict (malformed YAML), defaults still apply."""
        acronyms, idioms = merge_lexical_exceptions({"lexical_exceptions": "not a dict"})
        self.assertIn("BPM", acronyms)
        self.assertIn("in-your-face", idioms)


class TestAllCapsEmphasis(unittest.TestCase):
    def test_flags_uppercase_token(self):
        hits = detect_all_caps_emphasis("THIS is THE word.", DEFAULT_ACRONYM_WHITELIST)
        # 'THIS' and 'THE' both ≥ 3 chars uppercase, neither whitelisted
        self.assertGreaterEqual(len(hits), 2)

    def test_skips_whitelisted_acronyms(self):
        hits = detect_all_caps_emphasis(
            "The API returns JSON via HTTP.", DEFAULT_ACRONYM_WHITELIST
        )
        self.assertEqual(hits, [])

    def test_voice_extension_whitelists_brand_acronym(self):
        # "EDM" must not flag for a music brand that whitelists it.
        whitelist = DEFAULT_ACRONYM_WHITELIST  # already includes EDM
        hits = detect_all_caps_emphasis("The EDM track samples deep.", whitelist)
        self.assertEqual(hits, [])

    def test_short_caps_not_flagged(self):
        # 2-char uppercase tokens (e.g., "OK", "NO") are below the ≥3 threshold
        hits = detect_all_caps_emphasis("Say NO loudly.", DEFAULT_ACRONYM_WHITELIST)
        self.assertEqual(hits, [])


class TestForbiddenLexicon(unittest.TestCase):
    def test_flags_each_term_match(self):
        hits = detect_forbidden_lexicon(
            "The game-changing seamless leverage.", ["game-changing", "seamless", "leverage"]
        )
        self.assertEqual(len(hits), 3)
        rule_ids = {h["rule_id"] for h in hits}
        self.assertIn("forbidden_lexicon:game-changing", rule_ids)

    def test_case_insensitive(self):
        hits = detect_forbidden_lexicon("Game-Changing tech.", ["game-changing"])
        self.assertEqual(len(hits), 1)

    def test_word_boundary_respected(self):
        # 'unlocking' should not match the forbidden term 'unlock' alone if the
        # term's boundary intent is whole-word; current contract uses
        # alphanumeric-edge boundary, so 'unlocking' WILL match 'unlock' as
        # substring up to the next non-alphanumeric. Pin this contract:
        hits = detect_forbidden_lexicon("They unlocked the door.", ["unlock"])
        self.assertEqual(hits, [], "unlock should not match 'unlocked' (alphanumeric boundary)")

    def test_no_match_clean_text(self):
        self.assertEqual(detect_forbidden_lexicon("Plain prose.", ["foo"]), [])


class TestRewriteRuleRejects(unittest.TestCase):
    def test_flags_literal_reject_phrase(self):
        rules = [{"reject": "It might be worth considering...", "rule_id": "no-hedging"}]
        hits = detect_rewrite_rule_rejects(
            "It might be worth considering... a different approach.", rules
        )
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["rule_id"], "rewrite_rule:no-hedging")

    def test_skips_rules_without_reject_or_rule_id(self):
        rules = [{"accept": "x"}, {"reject": "y"}]  # both missing rule_id
        self.assertEqual(detect_rewrite_rule_rejects("y in text", rules), [])


class TestPronouns(unittest.TestCase):
    def test_first_person_singular(self):
        hits = detect_first_person_singular("I think this is great.")
        self.assertGreater(len(hits), 0)

    def test_first_person_singular_capitalized_my(self):
        """Sentence-start `My` must flag — not just lowercase `my`."""
        hits = detect_first_person_singular("My priority is the rollout.")
        self.assertGreater(len(hits), 0)

    def test_first_person_singular_capitalized_me_myself(self):
        for token in ("Me too.", "Myself included."):
            with self.subTest(token=token):
                self.assertGreater(len(detect_first_person_singular(token)), 0)

    def test_first_person_singular_curly_apostrophe(self):
        """`I’m` (curly apostrophe) must flag the full contraction, not just `I`."""
        hits = detect_first_person_singular("I’m here.")
        self.assertGreater(len(hits), 0)
        # Snippet should include the contraction, not just bare `I`.
        self.assertTrue(any("I’m" in h["snippet"] for h in hits))

    def test_first_person_singular_straight_apostrophe(self):
        hits = detect_first_person_singular("I'll handle it.")
        self.assertGreater(len(hits), 0)

    def test_first_person_plural_sentence_start(self):
        hits = detect_first_person_plural("We absorbed the framework.")
        self.assertEqual(len(hits), 1)

    def test_first_person_plural_after_period(self):
        hits = detect_first_person_plural("It works. We think so.")
        self.assertGreaterEqual(len(hits), 1)

    def test_first_person_plural_contraction_were(self):
        """Sentence-initial `We're` was previously NOT flagged because the
        regex required whitespace immediately after `We` — apostrophe failed
        the lookahead. Pin every contraction variant so this regression
        cannot return."""
        for sample in ("We're shipping.", "We've shipped.",
                       "We'll ship.", "We'd ship."):
            with self.subTest(sample=sample):
                self.assertEqual(len(detect_first_person_plural(sample)), 1)

    def test_first_person_plural_curly_apostrophe(self):
        """Curly-apostrophe contractions must flag identically to straight ones."""
        for sample in ("We’re shipping.", "We’ve shipped.",
                       "We’ll ship.", "We’d ship."):
            with self.subTest(sample=sample):
                self.assertEqual(len(detect_first_person_plural(sample)), 1)

    def test_first_person_plural_mid_sentence_skipped(self):
        """Pin the contract: mid-sentence `we` is intentionally NOT flagged.
        Sentence-initial `We` is the strongest signal of brand-voice
        violation; mid-sentence `we` is too noisy to flag without false
        positives on quoted material and blockquotes."""
        for sample in ("The issue we faced was small.",
                       "The team we hired delivered."):
            with self.subTest(sample=sample):
                self.assertEqual(detect_first_person_plural(sample), [])

    def test_first_person_plural_does_not_match_word_starting_with_we(self):
        """`Web`, `Wednesday`, `weather` etc. must not flag — sentence-initial
        but the word continues past `We`."""
        for sample in ("Web service is down.", "Wednesday is the deadline.",
                       "Weather permitting, we ship."):
            with self.subTest(sample=sample):
                # Last sample has mid-sentence `we` which is also skipped.
                hits = detect_first_person_plural(sample)
                self.assertEqual(hits, [], f"unexpected hit on '{sample}'")

    def test_second_person_flagged(self):
        hits = detect_second_person("Your priority is the rollout.", DEFAULT_COMPOUND_IDIOM_WHITELIST)
        self.assertGreater(len(hits), 0)

    def test_second_person_compound_idiom_skipped(self):
        """`in-your-face` must not flag despite containing 'your'."""
        hits = detect_second_person(
            "The in-your-face style is intentional.", DEFAULT_COMPOUND_IDIOM_WHITELIST
        )
        self.assertEqual(hits, [])

    def test_second_person_compound_idiom_case_insensitive(self):
        hits = detect_second_person(
            "An IN-YOUR-FACE design.", DEFAULT_COMPOUND_IDIOM_WHITELIST
        )
        self.assertEqual(hits, [])


class TestSignposting(unittest.TestCase):
    def test_lets_dive(self):
        hits = detect_signposting("Let's dive into the code.")
        self.assertGreater(len(hits), 0)

    def test_without_further_ado(self):
        hits = detect_signposting("Without further ado, here it is.")
        self.assertGreater(len(hits), 0)


class TestNegativeParallelism(unittest.TestCase):
    def test_is_not_x_it_is_y(self):
        hits = detect_negative_parallelism("It is not just a refactor; it is a rewrite.")
        self.assertGreater(len(hits), 0)

    def test_contracted_s_not_it_is(self):
        """Contracted `'s not` must flag — common in informal-leaning prose."""
        hits = detect_negative_parallelism("It's not a tool; it's a platform.")
        self.assertGreater(len(hits), 0)

    def test_curly_apostrophe_contraction(self):
        hits = detect_negative_parallelism("It’s not just code; it’s craft.")
        self.assertGreater(len(hits), 0)

    def test_not_just_x_but_y(self):
        hits = detect_negative_parallelism("Not just a tool, but a platform.")
        self.assertGreater(len(hits), 0)

    def test_not_only_but_also(self):
        hits = detect_negative_parallelism("Not only fast but also reliable.")
        self.assertGreater(len(hits), 0)

    def test_not_only_but_no_also(self):
        """`but` without `also` is the common variant — must flag."""
        hits = detect_negative_parallelism("Not only fast but reliable.")
        self.assertGreater(len(hits), 0)


class TestRuleOfThreeHeading(unittest.TestCase):
    def test_flags_three_comma_heading(self):
        hits = detect_rule_of_three_heading("## Performance, scale, and reliability\n")
        self.assertGreater(len(hits), 0)

    def test_two_item_heading_skipped(self):
        hits = detect_rule_of_three_heading("## Speed and security\n")
        self.assertEqual(hits, [])

    def test_four_item_heading_skipped(self):
        """4+ items in a comma-separated heading must NOT match (over-greedy regex bug)."""
        hits = detect_rule_of_three_heading("## A, B, C, D\n")
        self.assertEqual(hits, [], "rule_of_three is strictly three items")

    def test_five_item_heading_skipped(self):
        hits = detect_rule_of_three_heading("## A, B, C, D, E\n")
        self.assertEqual(hits, [])


class TestRhetoricalQuestions(unittest.TestCase):
    def test_flags_question_line(self):
        hits = detect_rhetorical_questions("What could go wrong here?")
        self.assertEqual(len(hits), 1)

    def test_skips_blockquote(self):
        hits = detect_rhetorical_questions("> Is this real?")
        self.assertEqual(hits, [])


class TestEmoji(unittest.TestCase):
    def test_flags_emoji(self):
        hits = detect_emoji("This is great! \U0001F680")
        self.assertGreater(len(hits), 0)

    def test_no_emoji_clean(self):
        self.assertEqual(detect_emoji("Plain ASCII prose."), [])

    def test_regional_indicator_flag(self):
        """Flag emojis are regional-indicator pairs (U+1F1E6..U+1F1FF) — must flag."""
        hits = detect_emoji("Shipped from \U0001F1FA\U0001F1F8 today.")
        self.assertEqual(len(hits), 1, "the US flag is one regional-indicator pair")

    def test_variation_selector_consumed(self):
        """❤️ is U+2764 + U+FE0F. The match must consume both so the snippet
        is visually intact, not truncated to ❤."""
        hits = detect_emoji("Heart ❤️ here")
        self.assertEqual(len(hits), 1)
        self.assertIn("❤️", hits[0]["snippet"])


class TestForbiddenLexiconEdgeCases(unittest.TestCase):
    """Document edge cases for the forbidden-lexicon detector — pinned so a
    future regex tweak surfaces the contract change."""

    def test_possessive_apostrophe_still_matches(self):
        """The possessive 's after a forbidden term still flags. Defensible:
        the forbidden term IS present. Snippet shows the trailing 's."""
        hits = detect_forbidden_lexicon("game-changing's value", ["game-changing"])
        self.assertEqual(len(hits), 1)


class TestNegativeParallelismDocumentedGaps(unittest.TestCase):
    """Pin the contract for variants that are intentionally NOT matched —
    a future regex change must update the test alongside."""

    def test_is_not_x_but_y_NOT_matched(self):
        """`It is not X, but Y` (no second `it is`) — intentionally NOT a
        negative-parallelism hit. The brand catalog reserves the family for
        the paired-clause shape `is not X[;,] it is Y`. The bare
        `is not X, but Y` shape is a contrast clause, not parallelism, and
        flagging it would generate false positives."""
        hits = detect_negative_parallelism("It is not a tool, but a platform.")
        self.assertEqual(hits, [], "single-clause contrast is not negative parallelism")


class TestFallbackVoiceExtendsNotResolved(unittest.TestCase):
    """The fallback YAML loader (`brand_prescan.load_brand_rules`) reads only
    the child file's frontmatter and does NOT walk `voice.extends`. The full
    chain is resolved by `brand-voice/scripts/extract_rules.py` upstream of
    `prescan --brand`. This test pins the fallback contract so a future
    refactor can't silently start resolving chains in the wrong layer."""

    def test_fallback_does_not_walk_chain(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as parent:
            parent.write(_voice_doc(
                "voice:\n  name: \"Parent\"\n"
                "forbidden_lexicon:\n  - \"parent-only-term\"\n"
                "rewrite_rules:\n  - reject: \"foo\"\n    accept: \"bar\"\n    rule_id: r\n"
                "sentence_norms:\n  word_count_min: 8\n  word_count_max: 18\n  sentence_max_hard: 25\n"
            ))
            parent_path = parent.name
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as child:
            child.write(_voice_doc(
                f"voice:\n  name: \"Child\"\n  extends: \"{parent_path}\"\n"
                "forbidden_lexicon:\n  - \"child-only-term\"\n"
            ))
            child_path = child.name
        try:
            rules = load_brand_rules(child_path)
            forbidden = rules.get("forbidden_lexicon") or []
            self.assertIn("child-only-term", forbidden)
            self.assertNotIn("parent-only-term", forbidden,
                             "fallback must NOT resolve voice.extends — parent terms absent")
        finally:
            Path(parent_path).unlink()
            Path(child_path).unlink()


class TestScanBrand(unittest.TestCase):
    """Integration: scan_brand() applies every detector enabled by the rules."""

    def test_only_runs_detectors_for_declared_patterns(self):
        rules = {
            "forbidden_patterns": ["all_caps_emphasis"],
            "forbidden_lexicon": ["foo"],
            "rewrite_rules": [],
        }
        text = "## SECTION\n\nThe foo is bad. Let's dive in.\n"
        hits = scan_brand(text, rules)
        # all_caps_emphasis fires on SECTION (not whitelisted);
        # forbidden_lexicon fires on 'foo';
        # signposting NOT enabled — 'Let's dive' must not flag here
        self.assertTrue(any(h["rule_id"] == "all_caps_emphasis" for h in hits))
        self.assertTrue(any("forbidden_lexicon:foo" == h["rule_id"] for h in hits))
        self.assertFalse(any(h["rule_id"] == "signposting" for h in hits))

    def test_pseudo_block_content_scanned(self):
        rules = {"forbidden_patterns": ["all_caps_emphasis"]}
        text = "Outside.\n```text\nINSTRUMENTS column\n```\nOutside.\n"
        hits = scan_brand(text, rules)
        # 'INSTRUMENTS' inside pseudo-block must flag
        self.assertTrue(any(h["rule_id"] == "all_caps_emphasis" for h in hits))

    def test_real_code_block_skipped(self):
        rules = {"forbidden_patterns": ["all_caps_emphasis"]}
        text = "Outside.\n```python\nALL_CAPS_CONST = 1\n```\nOutside.\n"
        hits = scan_brand(text, rules)
        self.assertFalse(any(h["snippet"].startswith("ALL_CAPS_CONST") for h in hits))

    def test_strict_code_only_blanks_pseudo_blocks(self):
        rules = {"forbidden_patterns": ["all_caps_emphasis"]}
        text = "```\nLOUD inside\n```\n"
        hits = scan_brand(text, rules, strict_code_only=True)
        self.assertEqual(hits, [])

    def test_empty_rules_returns_no_hits(self):
        self.assertEqual(scan_brand("any text", {}), [])

    def test_non_dict_rules_returns_no_hits(self):
        self.assertEqual(scan_brand("any text", None), [])
        self.assertEqual(scan_brand("any text", "not a dict"), [])

    def test_pronoun_forbid_set_case_insensitive(self):
        """A voice doc may write `pronouns.forbid: ["First-person singular"]`
        with capital F. The detector enable check must match case-insensitively
        — otherwise a stylistic capitalisation choice silently disables the
        whole detector."""
        rules = {
            "pronouns": {"default": "third-person", "forbid": ["First-person singular"]},
        }
        text = "I think this is great.\n"
        hits = scan_brand(text, rules)
        self.assertTrue(any(h.get("rule_id") == "pronouns:first-person singular"
                            for h in hits),
                        "First-person singular detector must enable on capitalised forbid entry")

    def test_pronoun_forbid_lowercase_still_enables(self):
        """Backward-compat: lowercase entry still enables."""
        rules = {"pronouns": {"forbid": ["first-person singular"]}}
        hits = scan_brand("I think this.\n", rules)
        self.assertTrue(any(h.get("rule_id") == "pronouns:first-person singular"
                            for h in hits))

    def test_pronoun_unrelated_forbid_does_not_enable(self):
        """Sanity: unrelated entries do not enable any pronoun detector."""
        rules = {"pronouns": {"forbid": ["royal we (archaic)"]}}
        hits = scan_brand("I am here. We are there. You are nowhere.\n", rules)
        # No pronoun detector enables — confirm no pronouns:* rule fires.
        self.assertFalse(any(h.get("rule_id", "").startswith("pronouns:") for h in hits))


class TestPrescanCLIBrandFlag(unittest.TestCase):
    """End-to-end: prescan.py --brand <doc> emits hits for both sources."""

    def _run(self, *args, stdin=None):
        return subprocess.run(
            [sys.executable, str(PRESCAN_SCRIPT), *args],
            input=stdin, capture_output=True, text=True, timeout=30,
        )

    def test_brand_flag_loads_and_scans(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as voice:
            voice.write(_voice_doc(
                "voice:\n  name: \"T\"\n"
                "forbidden_lexicon:\n  - \"verboten\"\n"
                "rewrite_rules:\n  - reject: \"foo\"\n    accept: \"bar\"\n    rule_id: r\n"
                "sentence_norms:\n  word_count_min: 8\n  word_count_max: 18\n  sentence_max_hard: 25\n"
            ))
            voice_path = voice.name
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as prose:
            prose.write("# Doc\n\nThe verboten term should flag.\n")
            prose_path = prose.name
        try:
            r = self._run("--brand", voice_path, prose_path)
            self.assertEqual(r.returncode, 0, r.stderr)
            hits = json.loads(r.stdout)
            brand_hits = [h for h in hits if h.get("source") == "brand"]
            self.assertGreater(len(brand_hits), 0, "expected at least one brand hit")
            self.assertTrue(any(
                h.get("rule_id") == "forbidden_lexicon:verboten" for h in brand_hits
            ))
        finally:
            Path(voice_path).unlink()
            Path(prose_path).unlink()

    def test_brand_flag_missing_file_returns_1(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as prose:
            prose.write("# Doc\n")
            prose_path = prose.name
        try:
            r = self._run("--brand", "/tmp/_nonexistent_voice.md", prose_path)
            self.assertEqual(r.returncode, 1)
        finally:
            Path(prose_path).unlink()

    def test_universal_only_no_source_field(self):
        """Without --brand, hits don't carry a source field (backward compat)."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Doc\n\nMoreover, this is interesting.\n")
            path = f.name
        try:
            r = self._run(path)
            self.assertEqual(r.returncode, 0)
            hits = json.loads(r.stdout)
            self.assertGreater(len(hits), 0)
            for h in hits:
                self.assertNotIn("source", h)
        finally:
            Path(path).unlink()


class TestMaskingMirrors(unittest.TestCase):
    """utils.mask_protected_regions delegates to prescan.mask_protected_regions
    so eval scripts and prescan stay byte-identical on masking."""

    def test_pseudo_block_handling_consistent(self):
        from prescan import mask_protected_regions as p_mask
        text = "```text\nfoo\n```\n```python\nbar\n```"
        self.assertEqual(mask_protected_regions(text), p_mask(text))


if __name__ == "__main__":
    unittest.main()
