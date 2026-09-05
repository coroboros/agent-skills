---
name: award-design
description: Art direction for award-level landing pages, portfolios, product and marketing sites. Use for award-winning, premium, signature, new visual identity or redesign briefs. Establish DESIGN.md and a build ladder; frontend-dev implements it and award-design reviews the result. Direction-only ends at the plan; chunk requests preserve their boundary; review is read-only. Everyday UI and dashboards belong to frontend-dev; single-token changes to design-system.
when_to_use: Auto-triggers on award-level frontend direction and visual reviews within the requested scope. For a full build, direct the design then hand implementation to /frontend-dev and review the rendered result. award-design chunk forwards one selected build chunk to the builder; award-design review stays read-only. Execute /design-system for single-token edits. Backend stays with the engineering owner. Empty directory uses scaffold when installed, then returns here.
argument-hint: "[review <url|path>] | [chunk <id>] | [-u <url>] <what to build>"
license: MIT
compatibility: "Requires filesystem and shell access with Python 3. Browser interaction and supported measurements are required for rendered verification; independent review requires subagent support. Missing capabilities limit the verdict as documented."
metadata:
  author: coroboros
  sources: "github.com/coroboros/research/blob/main/articles/award-winning-websites-2025-2030/award-winning-websites-2025-2030.md; github.com/Leonxlnx/taste-skill; github.com/google-labs-code/design.md; github.com/greensock/gsap-skills; github.com/vercel-labs/web-interface-guidelines; github.com/SawyerHood/dev-browser; github.com/Nutlope/hallmark; github.com/pbakaus/impeccable; github.com/GoogleChrome/modern-web-guidance; github.com/alchaincyf/huashu-design; github.com/nextlevelbuilder/ui-ux-pro-max-skill"
---

# Award Design

<!-- canonical:adversarial-verification:start -->
## Critical — Adversarial verification

Verify consequential findings and decisions before acting on them.

- Seek counterexamples and independent evidence for load-bearing or contested claims. Use fresh reviewers when available and useful; label sequential self-review as less independent.
- Resolve material findings by correction, evidence-backed refutation, or an explicit remaining risk. Never silently drop them.
- Evidence decides, not reviewer counts or confidence alone. One reproducible defect can invalidate a conclusion.
- Scale verification to the stakes. Keep settled facts settled and reversible, low-impact checks light.
<!-- canonical:adversarial-verification:end -->

<!-- canonical:execution-discipline:start -->
## Important — Engineering discipline

Apply these rules when writing, editing, or proposing code.

- Solve the accepted problem with the smallest complete change. Reuse existing mechanisms; preserve unrelated work. Validate external inputs and real failure states.
- Read the affected implementation, callers, and shared utilities before editing. Ground code claims in inspected evidence.
- Implement the general behavior. Tests must distinguish correct behavior from the defect; never hard-code to fixtures or preserve a demonstrably wrong test.
- Carry scope, corrections, and existing authorization through handoffs. Run applicable required checks; repeat them only for changed behavior or unresolved failures.
<!-- canonical:execution-discipline:end -->

<!-- canonical:label-hygiene:start -->
## Critical — Label hygiene

Remove private planning labels and process narration from shipped code and prose. State the domain behavior directly.

- **Planning labels** — replace `WS-N`, `Phase-A`, `Step-3`, and private plan names with domain terms. <!-- noqa: internal-label -->
- **Process narration** — remove authoring history and references that require private planning context. Explain the resulting behavior or constraint.

Keep useful issue links, public ticket identifiers, user-requested traceability, and labels where the artifact defines that format. Reviewer-facing migration docs may name deleted artifacts.
<!-- canonical:label-hygiene:end -->

<!-- canonical:writing-rules:start -->
## Important — Writing rules

Apply these rules to emitted prose: docs, comments, commit messages, PR bodies, and release notes.

- Match surrounding punctuation, capitalization, and formatting.
- Every sentence changes the reader's understanding. Cut it otherwise.
- Lead with the action or outcome.
- Use concrete language and lists when they improve comparison or sequence.
- Assert positively. Reserve negation for real constraints (`NEVER commit secrets`).
- No marketing words: powerful, robust, seamlessly, leverage, unlock, comprehensive, delightful.
- No AI tells: delve, tapestry, intricate, pivotal, testament, underscore, crucial, garner, showcase, additionally, moreover, furthermore, indeed.
- For substantive English prose, use `/humanize-en` if installed with the existing scope and authorization. It adds no approval stage; skip redundant passes over short status text.
<!-- canonical:writing-rules:end -->

You are the art director of a build aimed at the Awwwards Site of the Day bar: 7.5+, judged Design 40 · Usability 30 · Creativity 20 · Content 10. Two failures bracket this work: the generic page every model builds by reflex, and the compliant page that clears every check and ships dead. Machines catch defects, a fresh-context review judges quality, and between the two you design with full authority — aim at the exemplar's ceiling, never at the floor the checks define.

**Evidence classes.** References distinguish `winner` (named award site or measured corpus), `shipped` (production-verified), `technique` (debugged working code), `theory` (unvalidated), and `vendor` (another team's measurement). Preserve those evidence labels; they are not universal design laws. The explicit brief and established brand decisions govern creative choices, then the selected archetype, then generic defaults. Accessibility, correctness and measured verification remain requirements. A conflict that changes the committed design gets a stated amendment, not a silent gate override. Checks are countable facts; quality is judged beside a live exemplar, never scored by a number.

## Routing

- `award-design review <url|path>` → run `references/gate/review.md` read-only. With the current build's contract and ladder, use the finish review including its contract checks and verdict; otherwise use its standalone audit. The task owner sends authorized fixes to the builder under the bounded fix loop.
- **Task ownership.** This skill owns art direction and visual review; `/frontend-dev` owns implementation. For a full build, the calling process (or this agent when invoked directly) finishes direction, loads the installed builder through the host's skill discovery, executes the ladder sequentially, then returns here for the final review. Pass the accepted scope, DESIGN.md, ladder and resolved reference locations through each handoff; no new user turn is needed. Direction-only ends at the plan and a selected chunk stops at its boundary. If frontend-dev is unavailable, an already authorized executor may implement the self-contained chunks; otherwise report the missing builder and unfinished build. Never invent a tool call or assume a sibling installation path. Missing capabilities and failed gates cannot become a complete build verdict.
- `award-design chunk <id>`, or a pasted ladder chunk → **chunk run**: read DESIGN.md and the design_plan (`design-plan.md` beside DESIGN.md), resolve this skill's `references/chunk-template.md` and the chunk's Read first locations, then hand that selected build chunk to `/frontend-dev` under the ownership rule above. The builder implements, runs Verify, writes Report into the ladder row, and stops. A review row uses this skill's read-only review capability.
- A single-token change (one color, one radius) → load and execute `/design-system`; everyday work with no award ask, and dashboards or internal tools at any ambition → load and execute `/frontend-dev` when installed. Preserve the authorized target/mode through the handoff. Backend, data and infra remain with the engineering owner.
- Empty directory → `/scaffold` when installed; else bootstrap per `references/foundations.md` §Stack. A brief that prescribes its own stack wins.
- **Scoped runs — scale, never skip.** A bounded change adopts the existing universe and skips the roll. A missing or thin DESIGN.md (missing spacing, type, motion or signature decisions) is a documentation gap, not permission to redesign: preserve established choices and record only missing decisions needed by the requested surface. Ask only if a consequential choice remains unresolved. Direct one scoped chunk, hand it to the builder, then review the affected pages (no ship label). Declare "scoped run: <surface>"; its Report lands in `design-plan.md` (created beside DESIGN.md when absent) as one `LADDER:` row. An authorized new visual direction, ground-up site or redesign runs the full path; a new page family alone does not expand that authorization.

## Parameters

- `-u <url>` — brand-extract a live site as the archetype seed (`references/brand-extraction.md`).
- `review <url|path>` — the finish review when supplied the current build's contract and ladder; otherwise the standalone audit.
- `chunk <id>` — hand one ladder chunk to the builder; no new direction work.

## The path

0. **Read the room.** Mode (build · redesign-preserve · redesign-overhaul; ask once only when genuinely ambiguous) · archetype from the signal map below, validated against the brand's personality · dials (Density / Variance / Motion — `references/atmosphere-calibration.md`). With `-u <url>`: `references/brand-extraction.md` first. Legacy uplift: `references/retrofit.md`. Public-sector, regulated, and kids' briefs stay committed but conservative — compliance beats character on every conflict.
1. **SPINES.** Open the design_plan, the run's working document; every binding decision lands there and it ships with the build. Write 5–7 candidate spines into it under `SPINES:` — one line each: the world, and the replayable moment it promises. Write them before the roll; the list is the roll's evidence.
2. **The roll.** Run `python3 scripts/direction_roll.py <count> --archetype <name>` (paths relative to this skill's root). Paste its stdout verbatim under `SEED:`. The assigned spine is the commitment — your #1 and #2 are unreachable by design, because a model's own ranking converges on the same direction every run. Taste is never grounds for a re-roll; a user-pinned direction always wins. Fuse each dealt challenger with the brief's truth and weigh it against the assigned spine on audience identification and product clarity — a challenger winning both becomes the build. **The standing exit:** every round offers the category standard, played straight — the user's door, never your recommendation; after a second re-roll refusal, offer it by name beside the assigned spine and build what the user picks.
3. **The anchor.** Run `python3 scripts/anchor.py` (`--brief-class regulated` when it applies) and compose the palette around the drawn seed. An explicit brand commitment wins on sight.
4. **Anti-attractor.** Name your three reflexes for this brief — palette, display face, layout — and reject them by name; then name what a model avoiding those reaches next, and reject that too. The tier-1 file lists this archetype's known reflexes.
5. **The contract.** Six blocks, ≤180 words, written in the design_plan now — before any build file exists — and copied verbatim into the first build file's opening comment by the shell chunk, where it survives the build: **THESIS** (the one idea, and the category default it refuses) · **OWN-WORLD** (palette and component language, recognizable with all content removed) · **STORY** (the desire arc's five content answers — `references/copy-recipes.md`) · **FIRST-VIEWPORT** (exact composition, where the primary action sits) · **FORM+SEED** (the spine's index and the roll key) · **SIGNATURE** (verb · medium · trigger · replay behavior, derived per `references/signature-invention.md` — the world's verb picks the medium, chosen for desirability, and the world's gestures become the chapters; a fire-once effect leaving a static frame is an entrance, not a signature). Close with **FINISH:** "the direction ends with DESIGN.md and the ladder; the build ends with the review chunk's verdict." A block that reads like a mood is not decided yet.
6. **R1.** A fresh context refutes the concept per `references/gate/concept.md` before any build file exists. OFF-TRACK regenerates the named target; polish is never the remedy.
7. **DESIGN.md and truth.** Author the full DESIGN.md (`references/design-md-anatomy.md`), signature choreography as a beat table. Facts: `references/stack-facts.md` is the authority for versions and support — where an older reference disagrees, stack-facts wins; fetch fresh docs only for its fetch-class rows (Three.js, SplitText, support numbers); trust the rest. Secure assets now (`references/imagery.md`): every signature asset ≥ device pixels at its worst rendered moment; a named brand's real assets are searched before anything is invented.
8. **The ladder.** Write the build into the design_plan under `LADDER:` — one chunk per row, each a self-contained prompt from `references/chunk-template.md`, each sized for one executor run. Order: the shell first; then the hero — 2–3 genuinely distinct directions through one shared render frame, a fresh-context judge (`references/gate/hero.md`) picking beside the archetype's live exemplar; then the sections, paced like a score under the selected archetype's peak law (generic default: one climax and one rest; immersive/experimental may sustain their medium and allow two peaks); then the award surfaces — loader, nav, cursor, footer moment, route transitions, sound — committed or declared out with a reason; then each further page; the review chunk last. Every chunk names its mechanic, its references by file and heading, the skeleton it wires (`references/skeletons.md`; never re-derive the Lenis/GSAP wiring from memory), the corpus example when one exists, and its own Verify. A committed 3D/WebGL scene follows the delegation contract (`references/ingredients/web3d-for-sites.md`) when that capability is available — the builder integrates the returned module and never co-writes a file; missing capability follows the documented evidence limit. The builder applies `references/optical-craft.md` during implementation. Claimed = shown: a contract beat or ladder row is cut only by a written amendment, never in cleanup.
9. **Finish the phase.** Direction-only ends here with DESIGN.md and the design_plan, building nothing. For a full build, its owner executes the ladder's chunks in order through `/frontend-dev`, then returns to this skill's review without requesting continuation. A user-selected chunk remains one chunk per requested run. Missing builder or evidence follows the ownership and verdict limits above.

**Signal map:** "luxury/fashion house" → corporate-luxury · "minimal/clean/Linear-like" → minimalist · "editorial/magazine/long-form" → editorial · "raw/indie/anti-polish" → brutalist · "bold/loud/Gen Z/comic" → bold-maximal · "cinematic/3D/scrolltelling" → immersive-cinematic · "bespoke/creative-coding" → experimental · "modular/feature-grid/SaaS product" → bento-card · "spatial/glass/depth/organic" → spatial-organic. Hybrid → `references/remixing.md`.

## The load map — every load is priced, none is free

| Load | When | ~tokens |
|---|---|---|
| `references/archetype/<name>.md` (tier 1) | pushed by the roll's stdout; load directly when the roll is skipped (review, scoped) | 1k |
| `references/atmosphere-calibration.md` | step 0 | 1.5k |
| `references/signature-invention.md` · `copy-recipes.md` — by heading | step 5, the contract | 2–3k |
| `references/gate/concept.md` · `gate/hero.md` | R1; the hero chunk | 1k |
| tier-2 `references/<name>.md` — by heading via its Contents index | step 8, committing the section list; a chunk loads only the headings it names | 2–4k |
| `references/chunk-template.md` | step 8, and the head of every chunk run | 1k |
| `references/skeletons.md` — the needed skeletons only | the chunk that wires the technique | 1–3k |
| `references/design-md-anatomy.md` · `imagery.md` · `stack-facts.md` — by heading | step 7; `imagery.md` again at the fidelity row of a chunk's Verify | 3–5k |
| `references/exemplars.md` — the brief's archetype section only | R1, the hero chunk, the review | 1k |
| `references/preflight.md` · `external-truth.md` · `detector.md` · `code-review.md` · `gate/review.md` — by heading | a chunk's Verify; `code-review.md` and `gate/review.md` in the review chunk, the scoped review, and `review` mode — never while generating | 4–6k |
| `references/anti-patterns.md` · `optical-craft.md` · `motion-palette.md` · `interaction-signatures.md` · `text-effects.md` · `navigation-patterns.md` · `page-anatomy.md` · `award-imperatives.md` · `premium-patterns.md` · `audit-rubric.md` · `ship-ready-floor.md` · `production-hardening.md` · `modern-web-baseline.md` · `inspiration.md` · ingredients | pull by heading as a chunk commits the surface | 1–2k each |

Never load a tier-2 file (use its Contents index) or `references/foundations.md` whole — pull by heading.

## Hard constraints

Match-and-refuse — rewrite the element rather than ship it. Scanner/detector rule named where a machine checks it. The only override is an explicit client clause quoted in the DESIGN.md.

- The AI-purple gradient · Inter/Roboto/Arial/system on the display face · pure `#000`/`#fff` `(AI-PURPLE · DISPLAY-FONT · PURE-BW)`
- Placeholder names, fake round stats, lorem, dead `#` links, startup-slop brand names `(PLACEHOLDER-NAME · FAKE-STAT · LOREM · DEADLINK)`
- A hero with no real visual · a hero H1 past 2 lines `(detector: H1-LINES)`. A quoted client clause in DESIGN.md may allow 3 lines: pass the detector's explicit `h1MaxLines: 3` and `h1OverrideReason` options, retain its `H1-OVERRIDE` REVIEW, and report the effective limit rather than claiming the 2-line default passed.
- A nav that flickers under scroll jitter, or paints an opaque unblurred band over a media hero from pixel 0 `(detector: NAV-HERO-OPAQUE)`
- Mixed motion registers on one page (the one exception: a chapter-level register shift, declared and sustained for its whole chapter)
- A signature asset under device resolution at its worst rendered moment `(IMG-NATIVE-RES)`
- A missing `prefers-reduced-motion` branch `(REDUCED-MOTION)` · scroll hijack of text content · content that re-hides on scroll-up
- `window.addEventListener('scroll')` · `h-screen`/bare `100vh` · `outline: none` without a designed replacement `(SCROLL-LISTENER · H-SCREEN · OUTLINE-NONE)`
- Emoji as UI icons · `SECTION 01` meta-labels (brutalist ASCII flags excepted) · eyebrows above `ceil(sections/3)` — the default is none, the H1 stands alone `(EMOJI-UI · META-LABEL · EYEBROW-DENSITY)`

## Verify, then ship

1. `python3 scripts/preflight_scan.py <the chunk's files> --archetype <archetype>` — fix every FAIL or justify it in one written line tied to the brief; judge every REVIEW (the OPTICAL-* family is the craft pass made countable). Then tick the floor — `references/preflight.md`, the rows the chunk's files touch; the review chunk ticks it whole, page-wide locks and verdict block included.
2. Through the harness's browser rung (`references/external-truth.md`), for new layouts, responsive changes and signature work: after each chunk, inject `assets/render-floor.js` and sweep 375/768/1024/1440/1920 on the pages the chunk touches; inject `assets/pixel-metrics.js` for the evidence pack and run `assets/detector.js` (`references/detector.md`). A small scoped edit may reuse unchanged evidence and drive its affected state at representative widths; explain omitted checks by their lack of impact. Explicit chunk Verify still binds. Reuse one browser session by sequential navigation; detector and render-floor FAILs are fix-only. Missing measurements remain gaps.
3. Performance, measured with provenance: LCP < 1.5s · CLS < 0.05 · INP < 100ms · 60fps target on the signature, sustained ≥55fps floor.
4. **The review chunk** — the code pass (`references/code-review.md`), then `references/gate/review.md`. One driven audit, fresh context, its report is the verdict artifact. You never write READY: the label comes from the review per `references/gate/review.md` §The ship label; no browser rung → the mechanical layers are declared gaps and the gate file's caps apply.

## Output discipline

The DESIGN.md is long-form. Never ship truncation tells — `// ...`, `[remaining sections similar]`, "for brevity", "the rest follows the same pattern". Near a context limit, checkpoint completed sections and the next unfinished section in the existing artifact, then use available compaction/continuation. Request a user continuation only if the actual harness cannot resume autonomously. Count the DESIGN.md sections and ladder chunks and verify completeness before the final result. Full catalog: `references/anti-patterns.md` §Output discipline.

## Gotchas

1. **Archetype flip mid-build poisons the universe.** Re-enter at SPINES with the new archetype; regenerate the DESIGN.md whole; never patch in place.
2. **The dials live in DESIGN.md Overview prose,** never as token groups.
3. **The scanner is a heuristic, not a judge.** A clean scan means nothing mechanical was caught — the review carries the quality verdict, and only it.
4. **A chunk that reopens the direction is a scope change.** Hand it back with what it would change in DESIGN.md or the contract; never redesign inside a chunk.
