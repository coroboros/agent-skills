---
voice:
  name: "Chanel"
  source_urls:
    - https://www.chanel.com/us/fashion/collection/savoir-faire-metiers-art/
    - https://www.chanel.com/us/about-chanel/the-house-of-chanel/
    - https://www.chanel.com/us/about-chanel/gabrielle-chanel/
    - https://www.metmuseum.org/toah/hd/chnl/hd_chnl.htm
    - https://en.wikipedia.org/wiki/Chanel
  last_updated: "2026-04-27"
  source: "extract"

core_attributes:
  - attribute_id: institutional
    name: "Institutional"
    failure_mode: "first-person voice, conversational tone, casual register"
  - attribute_id: warm-restrained
    name: "Warm-restrained"
    failure_mode: "hype superlatives ('amazing', 'world-class'), exclamation marks, trend-speak"
  - attribute_id: heritage-anchored
    name: "Heritage-anchored"
    failure_mode: "novelty-as-virtue framing, season-bound urgency, claims without dates"
  - attribute_id: french-rooted
    name: "French-rooted"
    failure_mode: "translating house terms (maison, atelier, savoir-faire, Métiers d'art)"
  - attribute_id: craft-poetic
    name: "Craft-poetic"
    failure_mode: "abstract claims about craft without naming the atelier, the technique, or the duration"

forbidden_lexicon:
  - "game-changing"
  - "revolutionary"
  - "cutting-edge"
  - "next-gen"
  - "world-class"
  - "best-in-class"
  - "must-have"
  - "limited time"
  - "trendy"
  - "trending"
  - "viral"
  - "hottest"
  - "amazing"
  - "incredible"
  - "stunning"
  - "breathtaking"
  - "empower"
  - "unlock"
  - "leverage"
  - "premium"
  - "high-end"
  - "you'll love"
  - "we believe"
  - "we feel"
  - "passion for"
  - "obsessed with"
  - "journey"

required_lexicon:
  - "maison"
  - "atelier"
  - "ateliers"
  - "savoir-faire"
  - "haute couture"
  - "prêt-à-porter"
  - "Métiers d'art"
  - "Maisons d'art"
  - "Gabrielle Chanel"
  - "the House"
  - "House of Chanel"
  - "exceptional"
  - "le19M"

rewrite_rules:
  - reject: "exclusive limited edition"
    accept: "<replace with concrete: 'the atelier produced N pieces' or atelier name>"
    rule_id: no-explicit-exclusivity
  - reject: "trendy new bag"
    accept: "<name the model: 'the new <model name>'>"
    rule_id: no-trend-speak
  - reject: "you'll love this piece"
    accept: "<delete reader-address; describe the piece>"
    rule_id: no-reader-address
  - reject: "amazing craftsmanship"
    accept: "<name the atelier and the technique: 'embroidered by the artisans of Atelier Montex'>"
    rule_id: specific-over-amazing
  - reject: "passion for fashion"
    accept: "<replace with specific: 'the maison's commitment to <named craft>'>"
    rule_id: no-passion-cliche
  - reject: "the hottest piece this season"
    accept: "<delete heat metaphor: 'the spring collection introduces…'>"
    rule_id: no-heat-metaphor
  - reject: "We believe simplicity is elegance."
    accept: "Simplicity is the keynote of all true elegance."
    rule_id: no-hedging-attribution
  - reject: "Don't miss out!"
    accept: "<delete urgency closer entirely>"
    rule_id: no-urgency-closer
  - reject: "Chanel revolutionized fashion."
    accept: "Chanel introduced jersey to haute couture in 1916; the practice persists."
    rule_id: specific-over-revolutionary
  - reject: "premium materials"
    accept: "<name the material and atelier: 'tweed woven by Lesage'>"
    rule_id: specific-over-premium
  - reject: "I love the new bag."
    accept: "The new bag follows the 2.55 quilt."
    rule_id: no-first-person-singular
  - reject: "Discover the new collection."
    accept: "The new collection releases on <date> in <city>."
    rule_id: no-discover-signpost

sentence_norms:
  word_count_min: 8
  word_count_max: 35
  sentence_max_hard: 60
  contractions: "forbid"
  oxford_comma: true
  em_dash_spacing: "spaced"
  exclamation_marks: "forbid"

forbidden_patterns:
  - rule_of_three
  - rhetorical_questions
  - emoji
  - all_caps_emphasis
  - marketing_analogies
  - negative_parallelism
  - signposting
  - second_person_address

contexts:
  corporate:
    register: "institutional academic"
    third_person_only: true
    example_opener: "The House of Chanel originated in 1909, when Gabrielle Chanel opened a millinery shop at 160 Boulevard Malesherbes."
  metiers_d_art:
    register: "warm institutional, poetic when describing craft"
    primary_source_quote: "celebrate the exceptional French savoir-faire at the heart of the House's creations"
    example_opener: "The Métiers d'art collections celebrate the exceptional French savoir-faire at the heart of the House's creations."
  press_release:
    chronological: true
    dates_required: true
    example_opener: "Paris, March 2026 — the Métiers d'art collection is presented at le19M in Aubervilliers."
  product:
    technical_specifics: true
    avoid_emotion: true
    example_opener: "The 2.55 handbag, introduced February 1955, retains its quilted lambskin and chain shoulder strap."
  digital:
    shorter_form: true
    formality_preserved: true
    example_opener: "The maison archives film. The bag predates it."

pronouns:
  default: "third-person institutional ('CHANEL' or 'the House' as subject)"
  forbid:
    - "first-person singular"
    - "first-person plural in marketing"
    - "second-person 'you' in marketing"
---

# Brand Voice — Chanel

The voice of an institution older than living memory. Restraint over decoration, French heritage left untranslated, third-person observation rather than first-person enthusiasm. Warm when describing craft; austere when describing itself.

## 1. Core voice attributes

Five principles. Non-negotiable. Every piece of branded prose passes through this filter.

| Attribute | Description | Failure mode to avoid |
|---|---|---|
| **Institutional** | Speaks about itself in the third person — `CHANEL`, `the House`, `Gabrielle Chanel`. Maintains documentary distance from marketing vernacular. | First-person voice, conversational tone, casual register. |
| **Warm-restrained** | Refuses hype superlatives (`amazing`, `world-class`). Tolerates institutional qualifiers (`exceptional`, `extraordinary`) when they describe specific craft. No exclamation marks. | Trend-speak, fast-fashion vocabulary, urgency closers, generic adjectives without referent. |
| **Heritage-anchored** | Anchors every claim to a date, a place, an atelier, or a person. The maison documents continuity rather than announces reinvention. | Novelty-as-virtue framing, season-bound urgency, claims without dates. |
| **French-rooted** | Keeps `maison`, `atelier`, `savoir-faire`, `haute couture`, `prêt-à-porter`, `Métiers d'art`, `Maisons d'art` untranslated. The French signals insider competence without explanation. | Anglicising house vocabulary, italicising house terms (they are not foreign — they are the brand). |
| **Craft-poetic** | Permits warmth and poetry when describing the artisans' work — *"the artisans who embody the beauty of the craft"*. Specific atelier names anchor the poetry. | Abstract claims about craft without naming the atelier, the technique, or the duration. |

## 2. Rewrite rules — do/don't

### No reader-address

| Reject | Accept |
|---|---|
| "You'll love this piece." | (delete) |
| "Imagine wearing it." | (delete) |
| "Don't miss out." | (delete entire urgency closer) |
| "Discover the new collection." | "The new collection releases on <date> in <city>." |

### Specific over abstract

| Reject | Accept |
|---|---|
| "amazing craftsmanship" | "embroidered by the artisans of Atelier Montex" |
| "premium tweed" | "tweed woven by the Lesage atelier in Paris" |
| "the hottest piece" | "the most ordered piece, by retail volume" |
| "Chanel revolutionized fashion." | "Chanel introduced jersey to haute couture in 1916; the practice persists." |
| "Discover Chanel's new fragrance." | "The new fragrance, blended in Grasse, follows the floral aldehyde structure of N°5 (1921)." |

The rule of thumb is the maison's own: *"every creation is the result of precise movements, patiently practiced and passed down from generation to generation"* (chanel.com). Replace each abstract claim with the precise movement, the duration, or the atelier.

### No hype lexicon, but qualifiers are allowed

Drop entirely: `game-changing`, `revolutionary`, `cutting-edge`, `world-class`, `must-have`, `trendy`, `viral`, `hottest`, `amazing`, `incredible`, `stunning`, `breathtaking`. Keep, when describing craft attached to a named atelier: `exceptional`, `extraordinary`, `precise`. The maison's own copy uses *"exceptional savoir-faire"* and *"extraordinary skills of the maisons d'art"*. Qualifiers earn their place when the named subject (the atelier, the technique, the duration) earns the qualifier.

### No salesperson openers

Never begin with "We're excited to", "Discover the", "Don't miss". Begin with a date, a place, a name, a process: *"In 1909..."*, *"The atelier..."*, *"Maison Michel, established in..."*.

## 3. Forbidden lexicon and patterns

### Lexicon

`game-changing`, `revolutionary`, `cutting-edge`, `world-class`, `premium`, `high-end` — luxury marketing taxonomy with no specific referent. Replace with the concrete craft, atelier, or material.

`must-have`, `limited time`, `trendy`, `trending`, `viral`, `hottest`, `season's must` — the maison demonstrates rarity through facts (production counts, atelier names, distribution maps), never through these words.

`amazing`, `incredible`, `stunning`, `breathtaking` — emotional adjectives without information. Replace with the technique, dimension, or duration that earns the reaction.

`empower`, `unlock`, `leverage`, `journey`, `passion for`, `obsessed with` — generic SaaS-luxury crossover lexicon. The maison does not "empower" a wearer.

`we believe`, `we feel`, `we think`, `you'll love` — first-person hedge or second-person address. The voice is third-person institutional. State the fact directly.

### Patterns

- `rule_of_three` — three-item lists with rhythm signal AI authorship. The maison favours pairs, singletons, or runs of four.
- `rhetorical_questions` — *"But what about the silhouette?"* The reader did not ask.
- `emoji` — disallowed in branded prose. The maison's typographic restraint is part of the voice.
- `all_caps_emphasis` — caps reserved for the wordmark `CHANEL` and the interlocking `CC`. Bold or italic carries emphasis otherwise.
- `marketing_analogies` — *"Think of it as the Tesla of handbags."* The handbag is the bag. Describe its construction.
- `second_person_address` — *"your wardrobe"*, *"your style"*. The maison addresses the world, not the reader.
- `negative_parallelism` — *"It's not just a bag, it's a statement."* Drop the construction; state the fact.
- `signposting` — *"Discover…"*, *"Let us tell you about…"*, *"Without further ado…"*. Begin with the fact instead.

## 4. Sentence-level norms

Most sentences run 8–35 words. The voice tolerates long sentences when they carry chronology, dates, atelier names, or craft details. The maison's own copy regularly produces 35–40-word sentences with multiple subordinate clauses (e.g. *"CHANEL celebrates the Maisons d'art and the artisans who embody the beauty of the craft and contribute to bring to life the creative vision of the CHANEL Creation Studio through their exceptional savoir-faire"* — 33 words, single sentence). The hard ceiling is 60 words; over that, split.

No contractions in branded prose. `do not` rather than `don't`, `the maison is` rather than `the maison's`. Contractions belong to the conversational register.

Active voice when the agent is the maison or its founders (*"Chanel introduced jersey in 1916"*). Passive when the agent is anonymous craft (*"The bag was introduced in February 1955"*). Both are formal.

No hedging language. Reject `might`, `seems`, `arguably`, `relatively`, `generally`. State the fact.

No apology language. The maison never uses `sorry`, `apologies`, `unfortunately`. Delays, errata, and substitutions are stated as facts, not as regrets.

### Counter-examples

- *"This amazing new bag is a must-have for the season!"* → fails on three counts: lexicon (`amazing`, `must-have`), exclamation, season-urgency. Rewrite: *"The bag, introduced February 2026, follows the 2.55 quilt and the chain shoulder strap."*
- *"You'll love how seamlessly this piece fits your wardrobe."* → fails reader-address (`you'll`, `your`), lexicon (`seamlessly`), generic claim. Rewrite: *"The jacket, cut from Lesage tweed, follows the 1954 silhouette without modification."*

## 5. Tone by context

| Context | Adjustment | Example opener (anchored to primary source) |
|---|---|---|
| **Corporate / About** | Institutional academic. Third-person only. Dates and lineage anchor the prose. | *"The House of Chanel originated in 1909, when Gabrielle Chanel opened a millinery shop at 160 Boulevard Malesherbes."* |
| **Métiers d'art / craft editorial** | Warm institutional, poetic when describing artisans. Specific atelier names anchor the poetry. | *"The Métiers d'art collections celebrate the exceptional French savoir-faire at the heart of the House's creations."* (chanel.com) |
| **Press release** | Chronological narrative. Dates required. Reads as documentation, not promotion. | *"Paris, March 2026 — the Métiers d'art collection is presented at le19M in Aubervilliers."* |
| **Product description** | Technical specifics. Material, atelier, dimension, year. Avoid emotion unless attached to an atelier. | *"The 2.55 handbag, introduced February 1955, retains its quilted lambskin and chain shoulder strap."* |
| **Digital / Social** | Shorter form. Formality preserved. No hashtags, no exclamation, no emoji. | *"The maison archives film. The bag predates it."* |

## 6. Pronouns and self-reference

The maison writes about itself in the third person.

- **Default** — third-person institutional. `CHANEL`, `the House`, `the maison`, `Gabrielle Chanel introduced`.
- **Acceptable** — impersonal passive when the agent is anonymous craft. *"The bag was introduced in 1955."*
- **Reject** — first-person plural ("we") in marketing copy. Reserved for internal communications and signed editorial pieces.
- **Forbidden** — first-person singular ("I"). The author is the maison, not a person.

Never address the reader as "you" in branded prose. The maison speaks about the world; the reader observes.

## 7. Format conventions

### Code in prose

Inline `code spans` for technical identifiers (model numbers, year codes). Reserved use; the maison rarely needs technical typography.

### Numbers and units

- Dates: prefer the long form (`February 1955`, `Spring 2026`). Avoid numeric-only formats.
- Years: bare four digits (`1909`, `1916`, `2026`).
- Production counts: `the atelier produced 240 pieces` (numerals always).
- Dimensions: `25.5 cm × 17 cm` with the multiplication sign U+00D7.
- Money: never in branded prose. Discussed only in financial filings.

### Punctuation

- Oxford commas: yes (`tweed, jersey, and lace`).
- Em dashes — like this — with spaces. The British/French convention here, not the tight US convention.
- Quotation marks: curly `“`, `”` in branded English prose; straight `"` in code spans.
- Ellipses: `…` Unicode (U+2026), not three dots.

### Foreign vocabulary

- French house terms (`maison`, `atelier`, `savoir-faire`, `haute couture`, `prêt-à-porter`, `Métiers d'art`, `Maisons d'art`) appear untranslated and unitalicised. They are not foreign; they are the brand vocabulary.
- The accent on `Métiers` and `prêt-à-porter` is preserved everywhere.
- Italicise other foreign terms on first use.

### Lists

Avoid where prose works. When used, parallel grammatical structure throughout. End with no terminal punctuation if fragments, with periods if full sentences.

## 8. Visual pairing

The voice presupposes the visual environment of the maison.

- Editorial typography. Serif display, sans-serif body set tightly.
- Black on white, or white on black. No coloured backgrounds in branded layouts.
- Photography: black-and-white preferred for archival material; colour photography in restrained palette (cream, ivory, black, gold).
- No gradients. No drop shadows. No skeuomorphism. The page is a printed page even when it is a screen.

Writing that follows this guide and is then rendered in a casual sans-serif on a coloured background reads wrong. The voice and the visuals are the same artefact.

## 9. Quick diagnostic

Before publishing any prose under the maison name, three checks:

1. Read the first paragraph aloud. If it sounds like a department store catalogue, rewrite it.
2. Search the document for `we believe`, `you'll`, `must-have`, `revolutionary`, `amazing`, `passion`, `journey`, `unlock`, `empower`, `seamless`, `Discover the`. Each match is a rewrite.
3. Remove the longest paragraph. If the document is still complete, it was filler. Repeat until removing a paragraph genuinely subtracts meaning.

## 10. Counter-examples

Real bad rewrites — what the rules prevent.

- *"We're so excited to announce our amazing new collection that empowers women to seamlessly express their unique style!"* — fails salesperson opener (`We're so excited`), lexicon (`amazing`, `empowers`, `seamlessly`, `unique`), reader-address-by-implication, exclamation. Rewrite: *"The spring collection releases March 2026. Twenty pieces. Each cut from Lesage tweed."*
- *"This must-have bag is the season's hottest piece — limited edition, exclusive to insiders!"* — fails lexicon (`must-have`, `hottest`, `limited edition`, `exclusive`), urgency framing, em-dash misuse, exclamation. Rewrite: *"The new bag, introduced March 2026, is produced in 240 pieces by the Verneuil atelier."*
- *"Discover Chanel's revolutionary new fragrance — it'll change how you see luxury!"* — fails signposting (`Discover`), lexicon (`revolutionary`), reader-address (`how you see`), contraction (`it'll`), exclamation. Rewrite: *"The new fragrance, blended in Grasse, follows the floral aldehyde structure of N°5 (1921)."*
- *"You'll love how this incredible piece elevates any outfit!"* — fails reader-address (`You'll`, `any outfit`), lexicon (`incredible`, `elevates`), generic claim, exclamation. Rewrite: *"The jacket, cut from black wool tweed, takes the 1954 silhouette without modification."*

## 11. Reference texts

The canonical Chanel voice is exemplified in the maison's own copy. Primary sources:

- *Savoir-faire and Métiers d'art* — `chanel.com/us/fashion/collection/savoir-faire-metiers-art/` — the definitive primary-source page on the artisans, the Maisons d'art, le19M, and the institutional warmth-around-craft register. Quotable: *"celebrate the exceptional French savoir-faire at the heart of the House's creations"*; *"the artisans who embody the beauty of the craft and contribute to bring to life the creative vision of the CHANEL Creation Studio through their exceptional savoir-faire"*; *"every creation is the result of precise movements, patiently practiced and passed down from generation to generation"*.
- *The History of the House of CHANEL* — `chanel.com/us/about-chanel/the-house-of-chanel/` — the corporate-academic register, dated and chronological.
- *Gabrielle Chanel, the founder of CHANEL* — `chanel.com/us/about-chanel/gabrielle-chanel/` — the founder voice, biographical and dated.
- *Gabrielle "Coco" Chanel and the House of Chanel* — `metmuseum.org/toah/hd/chnl/hd_chnl.htm` — The Met Museum's academic essay; useful for the editorial-academic register and as cross-reference.

Secondary references (cross-checks, not primary):

- `en.wikipedia.org/wiki/Chanel` — encyclopaedic overview, useful for dated facts and chronology.
- `en.wikipedia.org/wiki/Coco_Chanel` — founder chronology.

When in doubt, re-read the primary sources. The voice has been consistent for over a century. Match it.
