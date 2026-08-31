"""skeletons.md — the executable half of the technique layer.

The seven wirings exist because a build reproduces them wrong from memory, so
these tests pin the properties that make a skeleton *executable* rather than
illustrative: it is present under its own heading, it carries both closing
lines (the flat Critical-points sentence and the named Common failure), and
the value that actually decides whether it works is in the code.

The Lenis skeleton gets its own class. The bug it closes — `autoRaf: true`
alongside a `gsap.ticker` driver, two rAF clocks advancing one instance twice
a frame — shipped in the research article and in foundations.md for a year.
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
REFS = SKILL_DIR / "references"
SKELETONS = REFS / "skeletons.md"

# (heading letter, the phrase the heading must carry)
SEVEN = (
    ("A", "Lenis"),
    ("B", "pin"),
    ("C", "Horizontal pan"),
    ("D", "SplitText"),
    ("E", "Three.js"),
    ("F", "View Transitions"),
    ("G", "IO reveal"),
)


def _body():
    return SKELETONS.read_text(encoding="utf-8")


def _sections(text):
    """{letter: section body} for every `## <letter>. …` skeleton heading."""
    out = {}
    matches = list(re.finditer(r"^##\s+([A-G])\.\s+(.+)$", text, re.MULTILINE))
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out[match.group(1)] = (match.group(2), text[match.end():end])
    return out


def _code(section):
    return "\n".join(re.findall(r"```[a-z]*\n(.*?)```", section, re.DOTALL))


class TestSevenSkeletonsPresent(unittest.TestCase):
    """Seven headings, seven code blocks. A skeleton that loses its code is a
    pointer, and the file already has a pointer file (stack-facts.md)."""

    @classmethod
    def setUpClass(cls):
        cls.text = _body()
        cls.sections = _sections(cls.text)

    def test_all_seven_headings(self):
        self.assertEqual(sorted(self.sections), [letter for letter, _ in SEVEN])

    def test_each_heading_names_its_mechanic(self):
        for letter, phrase in SEVEN:
            with self.subTest(skeleton=letter):
                title, _ = self.sections[letter]
                self.assertIn(phrase.lower(), title.lower(),
                              f"skeleton {letter} heading must name {phrase}")

    def test_each_skeleton_ships_code(self):
        for letter, _ in SEVEN:
            with self.subTest(skeleton=letter):
                code = _code(self.sections[letter][1])
                self.assertGreater(len(code.splitlines()), 5,
                                   f"skeleton {letter} carries no runnable block")


class TestEachSkeletonIsSelfContained(unittest.TestCase):
    """The file's header promises "the whole file, not a fragment". A skeleton
    that names `gsap` or `ScrollTrigger` without importing it throws a
    ReferenceError at module evaluation the moment it is pasted — the exact
    copy-paste trap the file exists to close."""

    @classmethod
    def setUpClass(cls):
        cls.sections = {letter: _code(body) for letter, (_, body) in _sections(_body()).items()}

    def test_every_bare_global_is_imported_or_runtime_resolved(self):
        for letter, code in sorted(self.sections.items()):
            js = "\n".join(block for block in code.split("\n")
                           if not block.strip().startswith("//"))
            for name in ("gsap", "ScrollTrigger", "SplitText", "Lenis"):
                if not re.search(rf"(?<![\w.]){re.escape(name)}\b", js):
                    continue
                with self.subTest(skeleton=letter, symbol=name):
                    imported = re.search(rf"^import .*\b{re.escape(name)}\b.*from", js, re.MULTILINE)
                    resolved = re.search(rf"(?:const|let|var)\s+{re.escape(name)}\s*=", js)
                    self.assertTrue(imported or resolved,
                                    f"skeleton {letter} uses `{name}` with no import and no "
                                    "runtime resolution — it throws on paste")

    def test_scrolltrigger_users_register_the_plugin(self):
        """A ScrollTrigger config on a tween is inert without registerPlugin."""
        for letter in ("B", "C", "D"):
            with self.subTest(skeleton=letter):
                self.assertIn("gsap.registerPlugin(", self.sections[letter])


class TestClosingContract(unittest.TestCase):
    """taste-skill §5's form: one flat Critical-points sentence, then one
    Common-failure sentence that names the wrong value and its fix. A skeleton
    without the failure line teaches the shape but not the trap, which is the
    only reason the file exists."""

    @classmethod
    def setUpClass(cls):
        cls.sections = _sections(_body())

    def test_every_skeleton_has_critical_points(self):
        for letter, _ in SEVEN:
            with self.subTest(skeleton=letter):
                self.assertRegex(self.sections[letter][1], r"(?m)^Critical points: ",
                                 msg=f"skeleton {letter} missing the Critical points line")

    def test_every_skeleton_has_a_common_failure(self):
        for letter, _ in SEVEN:
            with self.subTest(skeleton=letter):
                body = self.sections[letter][1]
                match = re.search(r"^Common failure: (.+)$", body, re.MULTILINE)
                self.assertIsNotNone(match, f"skeleton {letter} missing the Common failure line")
                self.assertIn("the fix is", match.group(1),
                              f"skeleton {letter}'s failure line must name the fix, not just the bug")

    def test_critical_points_is_one_line(self):
        """Flat, per the form — a bulleted Critical-points block is a second
        skeleton wearing a summary's clothes."""
        for letter, _ in SEVEN:
            with self.subTest(skeleton=letter):
                block = re.search(r"^Critical points: .+$", self.sections[letter][1], re.MULTILINE)
                self.assertIsNotNone(block)
                self.assertNotIn("\n-", block.group(0))


class TestLenisWiringIsTheFixedForm(unittest.TestCase):
    """The one skeleton whose wrong form shipped for a year."""

    @classmethod
    def setUpClass(cls):
        cls.section = _sections(_body())["A"][1]
        cls.code = _code(cls.section)

    def test_constructs_lenis(self):
        self.assertIn("new Lenis(", self.code)

    def test_autoraf_is_never_declared_as_an_option(self):
        """`autoRaf: true` alongside the ticker is the double-drive bug. The
        option is not merely set to false here — it is never declared, so a
        reader cannot re-introduce it by flipping a visible value. Naming it in
        a comment is the point; declaring it is the bug."""
        self.assertIsNone(re.search(r"autoRaf\s*:", self.code),
                          "the fixed wiring omits the autoRaf option entirely (it defaults off)")
        self.assertIn("autoRaf", self.code,
                      "the code should still name the omission, so the reader knows it is deliberate")

    def test_gsap_ticker_is_the_sole_driver(self):
        self.assertIn("gsap.ticker.add(", self.code)
        self.assertIn("lagSmoothing(0)", self.code)
        self.assertRegex(self.code, r"lenis\.raf\(\s*time\s*\*\s*1000\s*\)",
                         "gsap.ticker passes seconds; lenis.raf takes milliseconds")

    def test_scrolltrigger_is_notified_not_listening(self):
        self.assertIn("lenis.on('scroll', ScrollTrigger.update)", self.code)

    def test_gsap_absent_fallback_branch(self):
        """No GSAP on the page still needs exactly one clock — the fallback is
        an own rAF, never a second driver stacked on the ticker."""
        self.assertIn("requestAnimationFrame(loop)", self.code)
        self.assertIn("cancelAnimationFrame", self.code)

    def test_reduced_motion_returns_a_null_instance(self):
        self.assertIn("prefers-reduced-motion: reduce", self.code)
        self.assertIn("lenis: null", self.code,
                      "native scroll is the reduced-motion contract — a null instance, not a fake one")

    def test_destroy_removes_the_ticker_function_and_the_instance(self):
        destroy = self.section[self.section.find("destroy()"):]
        for teardown in ("gsap.ticker.remove(", "lenis.destroy()"):
            with self.subTest(teardown=teardown):
                self.assertIn(teardown, destroy)

    def test_common_failure_names_autoraf_and_the_double_drive(self):
        failure = re.search(r"^Common failure: (.+)$", self.section, re.MULTILINE).group(1)
        self.assertIn("autoRaf: true", failure, "the failure line must name the wrong value")
        self.assertIn("two rAF clocks", failure, "the failure line must name the mechanism")
        self.assertIn("scrub", failure, "the failure line must name what breaks")


class TestSkeletonSpecifics(unittest.TestCase):
    """One load-bearing value per remaining skeleton — the value that decides
    whether the wiring works, which is the reason each one is here."""

    @classmethod
    def setUpClass(cls):
        cls.sections = {letter: _code(body) for letter, (_, body) in _sections(_body()).items()}

    def test_pin_scrub_pins_at_the_viewport_top_and_refreshes_on_fonts(self):
        code = self.sections["B"]
        self.assertIn("start: 'top top'", code)
        self.assertIn("document.fonts.ready", code,
                      "a late font swap moves every trigger — refresh after it lands")
        self.assertIn("pinSpacing", code, "the sticky-stack variant is one line of this skeleton")
        self.assertNotIn("invalidateOnRefresh", code,
                         "the flag flushes a tween's recorded start values; with no function-valued "
                         "tween value here it does nothing, and a no-op with a comment is noise")

    def test_horizontal_pan_pins_the_wrapper_and_computes_travel(self):
        code = self.sections["C"]
        self.assertIn("ease: 'none'", code, "a scrubbed pan is 1:1 with the scrollbar")
        self.assertRegex(code, r"end:\s*\(\)\s*=>", "end must be function-valued, not a literal")
        self.assertRegex(code, r"x:\s*\(\)\s*=>", "x must be function-valued so the travel re-measures")
        self.assertIn("invalidateOnRefresh: true", code,
                      "the function-valued x only re-runs when the recorded start is flushed")
        self.assertIn("scrollWidth - window.innerWidth", code)

    def test_matchmedia_is_the_only_teardown_for_the_pinned_rigs(self):
        """gsap.matchMedia already reverts everything created inside its callback,
        so a nested gsap.context duplicates a teardown the file says there is one
        of. Two cleanup paths is the bug the 'one cleanup path per rig' rule bans."""
        for letter in ("B", "C"):
            with self.subTest(skeleton=letter):
                self.assertIn("mm.revert()", self.sections[letter])
                self.assertNotIn("gsap.context(", self.sections[letter])

    def test_splittext_uses_the_current_factory_and_returns_the_tween(self):
        code = self.sections["D"]
        self.assertIn("SplitText.create(", code, "the current documented factory")
        self.assertNotIn("new SplitText(", code, "the constructor form is the stale shape")
        self.assertIn("autoSplit: true", code)
        self.assertIn("mask: 'lines'", code)
        self.assertRegex(code, r"onSplit\(self\)\s*\{\s*return gsap\.",
                         "onSplit must RETURN the tween so autoSplit can revert it")

    def test_three_scene_awaits_init_on_the_webgpu_path(self):
        code = self.sections["E"]
        self.assertIn("three/webgpu", code)
        self.assertIn("await renderer.init()", code,
                      "WebGPU adapter acquisition is async — the first render must wait for it")
        self.assertNotIn("renderAsync", code,
                         "renderAsync is deprecated once init() is awaited — render() is the form")
        self.assertIn("prefers-reduced-motion: reduce", code)
        self.assertIn("IntersectionObserver", code)
        self.assertIn("visibilitychange", code)
        self.assertIn("renderer.dispose()", code)

    def test_three_scene_ands_its_two_visibility_gates(self):
        """One shared flag lets a tab-return restart the loop on an off-screen
        canvas: the observer will not fire again until intersection changes, so
        the off-screen gate is silently defeated for the rest of the visit."""
        code = self.sections["E"]
        self.assertIn("onScreen && visible", code,
                      "the intersection and visibility flags must be ANDed, not share one boolean")

    def test_view_transitions_guard_both_scopes_independently(self):
        code = self.sections["F"]
        self.assertIn("@view-transition", code, "the cross-document opt-in")
        self.assertIn("document.startViewTransition", code, "the same-document feature detect")
        self.assertRegex(code, r"if \(!document\.startViewTransition\) return",
                         "the guard IS the fallback — update() must still run")
        self.assertIn("prefers-reduced-motion: reduce", code)

    def test_view_transitions_catch_the_ready_rejection(self):
        """`ready` rejects whenever the transition is skipped — including the
        duplicate-name case this skeleton's own failure line describes. Left
        uncaught it surfaces as an unhandled rejection instead of silence."""
        self.assertIn("transition.ready.catch(", self.sections["F"])

    def test_io_reveal_keeps_the_base_state_visible(self):
        code = self.sections["G"]
        self.assertIn("io.unobserve(", code, "fire-once means the reveal persists")
        self.assertIn("html.js", code,
                      "the hidden state may only exist under the JS-added class")
        self.assertIn("prefers-reduced-motion: no-preference", code)
        self.assertNotIn("addEventListener('scroll'", code)

    def test_io_reveal_sets_the_js_class_before_first_paint(self):
        """A deferred module lets the browser paint the visible base, then blank
        the in-view reveals when the class lands — a flash on exactly the slow
        connections the visible-base rule exists for."""
        code = self.sections["G"]
        self.assertRegex(code, r"<script>document\.documentElement\.classList\.add\('js'\);</script>",
                         "the class must be set by a render-blocking inline script in <head>")

    def test_io_reveal_returns_a_teardown_like_every_other_skeleton(self):
        self.assertIn("io.disconnect()", self.sections["G"])


class TestNoVersionClaimsLiveHere(unittest.TestCase):
    """stack-facts.md is the single source for versions and support figures.
    A number restated in a skeleton is a second place to update, which is how
    the two conflicting scroll-driven support figures happened."""

    def test_no_bare_version_or_support_numbers(self):
        text = _body()
        for pattern in (r"\br1\d{2}\+?\b", r"\bChrome \d{3}\b", r"\bSafari \d{2}\b",
                        r"\bGSAP 3\.\d+", r"\d{2}% (?:global|support)"):
            with self.subTest(pattern=pattern):
                self.assertIsNone(re.search(pattern, text),
                                  f"skeletons.md must not restate a stack fact: {pattern}")

    def test_points_at_stack_facts(self):
        self.assertIn("stack-facts.md", _body())


if __name__ == "__main__":
    unittest.main()
