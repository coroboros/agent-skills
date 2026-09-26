"""Browser injection, targeted browser pipelines, and detector/checklist compatibility."""

import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[2] / "skills" / "award-design"
ASSETS = SKILL_DIR / "assets"
PROBES = Path(__file__).parent / "fixtures/browser-probes.cjs"


@unittest.skipUnless(shutil.which("node"), "node not on PATH")
class TestBrowserAssetContracts(unittest.TestCase):
    def run_script(self, script):
        result = subprocess.run(
            ["node", "-e", script, str(ASSETS)],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_focus_ring_cannot_rescue_missing_or_weak_hover_feedback(self):
        self.run_script(f"require({json.dumps(str(PROBES))})('hover', process.argv[1]);")

    def test_clipped_glyphs_require_live_scroll_offsets_for_axis_exemptions(self):
        self.run_script(f"require({json.dumps(str(PROBES))})('clipping', process.argv[1]);")

    def test_payloads_inject_as_classic_scripts(self):
        self.run_script("""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
for (const [file, name, methods] of [
  ['detector.js', 'awardDetector', ['run', 'measure', 'measurePeak', 'measureContact']],
  ['render-floor.js', 'awardRenderFloor', ['run', 'arm']],
  ['pixel-metrics.js', 'awardPixelMetrics', ['run']],
]) {
  const window = {};
  vm.runInNewContext(fs.readFileSync(path.join(process.argv[1], file), 'utf8'), {window});
  for (const method of methods) assert.equal(typeof window[name][method], 'function', file + ':' + method);
}
""")

    def test_reinjection_keeps_error_capture_without_duplicate_listeners(self):
        self.run_script("""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const listeners = [];
const window = {innerWidth: 375, addEventListener: (type, handler) => listeners.push({type, handler})};
const context = vm.createContext({window});
const source = fs.readFileSync(path.join(process.argv[1], 'render-floor.js'), 'utf8');
vm.runInContext(source, context);
window.awardRenderFloor.arm();
listeners.find(entry => entry.type === 'error').handler({message: 'first error'});
vm.runInContext(source, context);
const report = window.awardRenderFloor.arm();
assert.equal(report.captured, 1);
assert.deepEqual(listeners.map(entry => entry.type).sort(), ['error', 'unhandledrejection']);
listeners.find(entry => entry.type === 'unhandledrejection').handler({reason: Error('rejection')});
assert.deepEqual(Array.from(window.awardRenderFloor.state.errors, entry => entry.message),
  ['first error', 'rejection']);
""")

    def test_checklist_tags_and_reference_resolve_to_detector_rules(self):
        rules = json.loads(self.run_script("""
const path = require('node:path');
console.log(JSON.stringify(require(path.join(process.argv[1], 'detector.js')).RULES));
"""))
        ids = {rule["id"] for rule in rules}
        self.assertEqual(len(ids), len(rules), "detector rule IDs must be unique")
        preflight = (SKILL_DIR / "references/preflight.md").read_text(encoding="utf-8")
        tags = set(re.findall(r"\(detector: ([A-Z0-9-]+)\)", preflight))
        self.assertTrue(tags, "no detector tags extracted from the checklist")
        self.assertLessEqual(tags, ids)
        reference = (SKILL_DIR / "references/detector.md").read_text(encoding="utf-8")
        for rule in rules:
            with self.subTest(rule=rule["id"]):
                self.assertIn(rule["id"], reference)
                self.assertIn(rule["severity"], {"FAIL", "REVIEW"})
                self.assertRegex(rule["box"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


if __name__ == "__main__":
    unittest.main()
