# Postmortem — `/write-clear-readme` on `claude-config/README.md`

**Date.** 2026-05-13
**Target.** `coroboros/claude-config` README — a long, multi-audience file (install + reference + meta-instructions).
**Outcome.** Restructure shipped as PR #11 across four commits. The final form — h2-only scan-line with every sub-section in a labeled `<details>`, no `Expand —` prefix, no h3 above the disclosure — matched the user's stated preference for a long human-facing doc: instant mental orientation, single-click expand, no page load. The failure was the trajectory, not the destination: the skill should have proposed extreme in-page collapse from the start rather than reaching it after four corrections.

## What happened

The skill ran in audit mode on the README. The structural audit script returned zero findings — anchors resolved, no nested `<details>`, no missing `<br>`, no bloat tokens. The prose scan (AI tells, marketing voice, hedging) returned zero hits.

A human read surfaced three real issues the script could not detect:

- TOC missing three entries (Secret scanning, Multi-Account Credentials, License).
- Duplicate `#maintenance` anchor — the top-level TOC link landed inside a buried h4, not on the intended h2.
- A substantial section nested under a parent heading that diluted its standing.

Asked for a more aggressive restructure, the skill applied Pattern A grouped collapse — `<details>` blocks wrapped heavy reference content, applied selectively. The TOC was simplified to h2-only. Multi-Account Credentials was promoted to a peer h2. The colliding inner `#### Maintenance` was renamed to `### Token rotation`. The audit re-ran clean. The PR opened.

The result was longer than the original, with heavy tables hidden behind expanders and short sections left visible — a mix that varied section by section based on local judgment about content density. Several summary lines also surfaced specific counts ("25 symlinks", "14 declared periodic tasks") that were either already wrong or would rot the moment a file was added.

The user opened the rendered file and said it still was not readable, clear, or beautiful, and called out the inconsistent collapse as a minefield: no rule to infer about which sections expand and which do not.

## Why the audit missed the real problems

### 1. The audit measures mechanics, not meaning

The audit script checks four things: unresolved anchors, nested `<details>`, missing `<br>` after `<summary>`, presence of bloat tokens. All four are syntactic. None are perceptual.

The script cannot answer the questions that determine whether a README is good:

- Can a new reader install in under five minutes without backtracking?
- Does the reader know which sections are for them and which to skip?
- Does the first screen earn a second screen?
- Does the page have visual rhythm — density variation, breathing room, callouts, imagery?

The skill shipped a clean report on a file with real readability problems, then moved on.

### 2. `<details>` hides volume but does not reduce it

The restructure made the file longer, not shorter. The content a reader has to read is unchanged. The promise of `<details>` is "skim past sections you do not need." The reality is "scroll, click, scroll inside the expand, scroll back out." For a document already organized by tables and headings, the interaction tax can be larger than the scroll it replaces.

The skill's *Universal rules* warn against collapsing first-time-setup content. They do not warn against collapsing deep reference tables that a reader might want to scan visually alongside the rest of the page.

### 3. The collapse rule was not self-evident

This was the most visible failure to the reader. Pattern A was applied selectively — heavy sections collapsed, short sections left visible, based on per-section judgment about "frequency of use" and "content density." Each individual decision was locally defensible. The aggregate was inconsistent.

The reader, faced with a dozen subsection headings, sees some content visible and some collapsed with no inferable rule. The collapse becomes a guessing game: is this hidden because it is optional, or because it is long, or because it is lookup-only? Every section turns into a decision point — *should I click here?* — and the page reads as a minefield.

A maintainable Pattern A application requires a self-evident rule. The valid modes:

- **Top-level collapse.** Every h2 wraps in `<details>`. The reader sees the h2 list as a scan-map; clicks reveal full sections.
- **Per-section collapse.** Within each h2, every sub-section wraps. The reader sees the h2s and a labeled `<summary>` list; clicks reveal content. *(This is the form PR #11 ultimately shipped — and the one the user confirmed reads well.)*
- **No collapse.** Everything visible.
- **Mixed, with a self-evident rule.** A short intro paragraph visible under each h2, then every sub-section collapsed (exactly the pattern Multi-Account Credentials and Tasks Manager use in PR #11). Acceptable when the rule is obvious from the structure without explanation.

What does *not* work is the original failure mode: ad-hoc selective collapse driven by per-section judgment about "content density" or "frequency of use." When no rule connects the choices, the page reads as a minefield. Pick one of the four valid modes and apply it uniformly.

### 4. Summary text used meta-instruction, not heading

Every `<summary>` started with `Expand —` followed by a descriptor. The prefix tells the reader the affordance, but the affordance is implicit in the `<details>` element itself — the disclosure triangle is the universal signal. The prefix adds a word of noise on every collapsed block and signals that the author distrusts the reader.

A clean summary uses the heading text directly, or a short descriptor with no meta-instruction:

- Cluttered: `<summary><em>Expand — symlinks created by install.sh</em></summary>`
- Clean: `<summary><em>Files installed</em></summary>` — or simply reuse the h3 heading inside.

### 5. Stale counts in the summary text

Several summaries embedded specific counts (e.g. "25 symlinks created by install.sh", "14 declared periodic tasks"). Counts of internal content rot the moment a row is added. One was already wrong at audit time. Summaries — and all maintainable doc prose — should describe content qualitatively ("symlinks created by install.sh") rather than enumerating it.

### 6. The skill never touched content shape

Pattern A wraps existing content in markup. It does not:

- Split a long table into category sub-tables.
- Trim redundant columns (the README's `Source` column repeats the obvious path for every row).
- Merge thin sections into their parents.
- Promote sections that deserve their own files.
- Cut content that no longer earns its place.

The audit mode reports "consider Pattern A if 5+ peer items cluster into groups." It does not report "consider splitting into INSTALL.md + REFERENCE.md + CONTRIBUTING.md."

### 7. The file served three audiences in one place

The target documented three jobs:

- **First-time install** — for a new user setting up `~/.claude/` from scratch.
- **Daily reference** — Top Commands, Tasks Manager flags, Maintenance matrix.
- **Meta-instructions** — "Rules for Claude when working in this repo," for the agent itself.

Each audience reads in a different order, wants a different density. The skill's instinct (recorded in the earlier draft of this postmortem) was to propose a multi-file split — `MULTI-ACCOUNT-CREDENTIALS.md`, `TASKS.md`, `CLAUDE-DESKTOP-PREFS.md`, each with a one-line pointer in the README. The user rejected that path: multi-file split forces click + page load, which is more friction than click + in-page expand. Extreme in-page collapse — every sub-section in a labeled `<details>` — lets one README serve all three audiences without forcing navigation between files. The skill should have proposed that pattern directly rather than reaching for file extraction.

### 8. "Beauty" was not in the skill's vocabulary

The skill checks anchor resolution and bloat tokens. It does not check:

- Section-shape variance (a page where every section is `## H2 → paragraph → table` is visually monotone, regardless of content quality).
- Use of GitHub-supported callouts (`> [!NOTE]`, `> [!WARNING]`, `> [!TIP]`).
- Hero imagery, GIFs, or screenshots for first-screen impact.
- Code-fence language-tag consistency.
- Table column-width ratios.
- Paragraph-length variance.

The request was "lisible, clair et beau" — readable, clear, beautiful. The skill solved for none of the three.

### 9. The first-3-lines test passed by surface match

The skill's *README-specific style* prescribes a first-3-lines check: title + tagline + scope paragraph should deliver what + who + what it does. The target file passes on the surface — the title is `claude-config`, the tagline is "Personal Claude Code configuration," the paragraph lists what is in the box. A new reader still cannot picture what the project is, what installing it does, or whether they want it.

The check needs a stronger criterion: a reader given only the first three lines should be able to (a) decide whether the file is for them, and (b) predict the next section.

### 10. No rendering loop

The skill ran entirely in markdown source. It never asked the agent to view the rendered output, the GitHub preview, or a screenshot. Visual problems — monotony, density, lack of imagery, inconsistent collapse — cannot be detected without seeing the rendering. The skill prescribed a structure that is auditable in source but unverifiable in form.

### 11. Section heading + `<summary>` repeated the same label

Even after the consistency rule was applied and `Expand —` was stripped, the rendered output kept each h3 heading visible above its `<details>` — "Prerequisites" the h3, then "▸ Prerequisites" the italic disclosure summary right under it. Every section displayed two visual labels for one piece of content. The user called it out as redundant noise on every collapsed block.

The fix is to drop the h3 entirely. The `<details>` element provides the affordance (the disclosure triangle) and the `<summary>` provides the label. A separate h3 above adds nothing the reader cannot already see, and on a page with many sections the duplication compounds.

The trade-off — the h3 anchor disappears (`#token-scopes`, `#files-installed`, etc.) — is acceptable for an internal-facing README whose TOC is h2-only. In-prose links to former h3 anchors become positional references ("see Token scopes below"). For docs where deep anchors matter, the alternative is to keep the h3 inside the `<details>` — GitHub auto-expands on hash navigation and the anchor still resolves.

## What "readable, clear, beautiful" actually needed

A more honest restructure would have:

1. **Pushed every sub-section into a labeled `<details>` from the start.** The earlier draft of this postmortem prescribed multi-file split (extracting MAC, Tasks Manager, Personal Preferences to their own files). The user rejected that path as an anti-pattern: cross-file `.md` links rarely get clicked by human readers, and the page-load + lost-context cost dwarfs the in-page click-to-expand cost. Keep the doc in one file and let the disclosure pattern handle audience separation. File split is opt-in only — never a default move.
2. **Picked one collapse rule and stuck to it.** Either collapse every h2 (top-level scan-line), or collapse every sub-section within each h2 (per-section detail), or collapse nothing. Avoid the local-optimization trap — saving the reader a click on a "short" section while making them click on a "long" adjacent section is worse than either consistent extreme.
3. **Stripped `Expand —` from summaries.** Let the disclosure triangle do its job. The summary should read as the heading.
4. **Described content qualitatively, not by count.** "Symlinks created by install.sh" is evergreen. "25 symlinks" rots.
5. **Trimmed the heaviest table.** Files installed is wide and deep. Grouping by category (Rules / Hooks / Scripts / Sounds / Assets) and dropping the redundant `Source` column produces small micro-tables that render at full width.
6. **Opened with a screenshot or GIF.** `install.sh` running in a terminal, or the resulting `~/.claude/` tree. First-screen impact, zero scroll required.
7. **Added a "you'll want this if…" line.** One sentence above the badge row that filters readers in or out before they invest scroll time.
8. **Targeted a slim index README.** Detail lives in linked files. The index does navigation, not reference.
9. **Used callouts for asides.** "Why direnv over global state" is a sidebar in essay form; it reads as body text and competes with the setup steps for attention. A `> [!NOTE]` block would set it apart visually.
10. **Replaced one or two tables with bullet flows.** The Hook overrides table is small enough to read as bullets (`allow-leak <cmd>` — bypasses `pre-publish-scrub.sh`), which would also break the visual monotony.
11. **Dropped the h3 above every `<details>` block.** When the `<summary>` already carries the section label, an h3 above it is duplicate signal. Drop the heading, accept the loss of the deep anchor, rewrite any in-prose link to a positional reference.

The skill suggested none of this. The output was a structurally compliant restructure of a document that needed editorial, consistency, and maintainability work.

## Skill improvements

### 1. Default priority order for long human-facing docs

The skill should propose, in order:

1. **Extreme in-page collapse.** Every sub-section in a labeled `<details>`, h2 as scan-line, no h3 above the disclosure, no `Expand —` prefix in `<summary>`. First default.
2. **In-between, with a self-evident rule.** Short intro paragraph visible under each h2, then every sub-section collapsed (the MAC / Tasks Manager pattern in PR #11). Use when the intro carries enough signal to decide whether to click.
3. **No collapse.** For short docs (under a few screen heights), or for sections where every line matters.
4. *(Anti-pattern — reject.)* **Multi-file split.** Cross-file `.md` links rarely get clicked by human readers. The page-load + lost-context cost dwarfs the in-page click-to-expand cost. The pattern survives only by convention. For this user's reading model — and likely most internal config / personal docs — file split is to be rejected outright, not ranked behind the others.

The earlier version of this skill (and the earlier draft of this postmortem) ranked file-split as the *first* move, which the user explicitly rejected as an anti-pattern. Flipping the order is not enough — file split needs to be marked as opt-in-only, never default.

### 2. Reframe `<details>` as last resort

The current skill leads with Pattern A. Move it to the bottom of the audit's recommendations, after content-shape changes. The decision tree should be:

- Can content be cut?
- Can content be moved to a separate file?
- Can a section be reshaped (long table → category tables, paragraph → bullets, six bullets → one sentence)?
- Only then: should it be collapsed under `<details>`?

`<details>` is a structural last resort, not a first move.

### 3. Make Pattern A all-or-nothing at a given level

When applying Pattern A, pick one mode: collapse every peer at the chosen level, or collapse none of them. Reject the heuristic "collapse if section length > N lines" — it produces selective collapse that creates a minefield for the reader. The skill should refuse to ship a partial Pattern A unless the rule is self-evident from the structure: every h2, OR every h3-within-h2, OR every h4-within-h3, OR nothing.

### 4. Strip `Expand —` from `<summary>` text

The current example pattern uses `<summary><em>Expand — descriptor</em></summary>`. Drop the `Expand —` prefix. The `<details>` element provides the affordance — the disclosure triangle is the universal signal. Use the summary for the heading text or a short qualitative descriptor only.

### 5. Ban stale counts in doc prose

Lint the diff for numeric content-counts adjacent to nouns ("25 rows", "8 imports", "14 tasks", "557 lines"). Each is a maintenance liability. The skill should flag these in audit mode and rewrite them in author/polish modes to qualitative descriptors.

### 6. Add a visual rhythm check

Beauty heuristics the audit can detect from source alone:

- Section-shape repetition (consecutive `## H2 → paragraph → table` sections flag as monotone).
- Callout density (zero `> [!NOTE|TIP|WARNING|IMPORTANT|CAUTION]` blocks in a long user-facing file flags as flat).
- Paragraph-length variance (low variance flags as bullet-like).
- Image presence (zero images in a long user-facing README flags as text-heavy).
- Code-fence language-tag consistency (mixed tagged/untagged within the same file).

None of these is conclusive on its own. Together they signal "the page reads flat" and prompt the agent to surface the finding.

### 7. Add an audience-mapping check

For each major section, identify the implicit audience (first-time installer, daily user, maintainer, agent reading CLAUDE.md context). When the same file serves more than two audiences, flag as a candidate for `split` mode.

### 8. Mandate a rendering check

Before declaring done, the agent should view the rendered output — open the file in a browser, request a screenshot from the user, or at minimum render to a static HTML preview and read the result. Source-only audits cannot catch visual monotony or inconsistent collapse patterns.

### 9. Strengthen the first-3-lines test

Replace "title + tagline + scope paragraph" with: "a reader given only the first three lines should be able to (a) decide whether the file is for them, and (b) predict the next section." The current check is satisfied by a generic tagline; the proposed check would have flagged the target file's opening as a list-of-contents rather than a positioning line.

### 10. Surface the silent assumption

The skill's *Universal rules* implicitly assume the file's content is the right content. The audit should state this assumption out loud: "This audit evaluates structure, anchor integrity, and prose for AI tells. It does not evaluate whether the right content is in this file. For that, consider `split`, `polish`, or asking the user whether sections should be moved or cut."

Naming the assumption gives the user a chance to flag it before the skill spends a turn polishing the wrong target.

### 11. Bias toward `<summary>` as the section heading

When applying Pattern A and a `<details>` block has a labeled `<summary>`, drop the surrounding h3 by default. The default trade-off — lose the h3 anchor, gain visual cleanliness — wins for most internal-facing READMEs. The skill should surface the trade-off when deep anchors are referenced from elsewhere (cross-doc links, external bookmarks); otherwise default to no-h3 and let the disclosure triangle carry the affordance.

## Status of the affected file

PR #11 shipped the destination across four commits. The user confirmed the final form matches their preference for a long human-facing doc — instant scan, click to dive, no friction. The structural work and the consistency rules are done:

- Pick one collapse mode and stick to it ✓
- Strip `Expand —` from every `<summary>` ✓
- Drop the h3 above every `<details>` block ✓
- Replace every embedded content-count in prose with a qualitative descriptor ✓

What the earlier draft of this postmortem got wrong: it prescribed multi-file split (`MULTI-ACCOUNT-CREDENTIALS.md`, `TASKS.md`, `CLAUDE-DESKTOP-PREFS.md`). The user rejected the entire pattern as an anti-pattern — cross-file `.md` links rarely get clicked, the page-load tax breaks reading flow, and the reader stays in the file they were already in. Extreme in-page collapse is the right answer for this class of doc; file split is opt-in only, never a default. The split prescription has been retracted everywhere it appeared.

Optional polish items the skill could have surfaced, none of them blocking and none required by the user:

- Group the Files installed table by category (Rules / Hooks / Scripts / Sounds / Assets); drop the redundant `Source` column.
- Add a "you'll want this if…" line above the badges.
- Add a screenshot or GIF of `install.sh` to the Install section.
- Use GitHub callouts (`> [!NOTE]`) for the "Why direnv" / "Why NOT 1Password" asides under Multi-Account Credentials, instead of bold-tagged inline paragraphs.

A single-file README with disciplined `<details>` discipline can serve install + reference + meta-instructions for one human user without breaking. The four-iteration journey to confirm this — selective collapse → consistent collapse → strip `Expand —` → drop h3s — is the real failure mode the skill should fix.

## Why this postmortem lives here

The skill is the unit that needs revision. A postmortem in its own `references/` folder keeps the failure case in view for the next agent that runs an audit or the next maintainer who edits the skill. The lessons sit where the change has to happen.
