# AI Writing Patterns — full catalogue

32 patterns grouped into six families. For each: what to watch for, why it reads as AI, a concrete before/after.

Use only facts supplied in the input. A specificity or attribution gap remains a gap; a rewrite cannot invent a source, number, date or explanation. Parenthesized editorial actions below describe deletion or a needed source check, not replacement factual prose. Structural patterns are diagnostics unless the requested scope also authorizes restructuring.

## Contents

- **Content patterns** — 1 Significance inflation · 2 Notability name-dropping · 3 Superficial -ing · 4 Promotional language · 5 Vague attributions · 6 Formulaic "Challenges" sections
- **Language patterns** — 7 AI vocabulary · 8 Copula avoidance · 9 Negative parallelisms · 10 Rule of three · 11 Synonym cycling · 12 False ranges · 13 Passive / subjectless fragments
- **Style patterns** — 14 Em-dash overuse · 15 Boldface overuse · 16 Inline-header lists · 17 Title case headings · 18 Emojis · 19 Curly quotes
- **Communication patterns** — 20 Chatbot artifacts · 21 Knowledge-cutoff disclaimers · 22 Sycophantic tone
- **Filler and hedging** — 23 Filler phrases · 24 Excessive hedging · 25 Generic positive conclusions · 26 Hyphenated-pair overuse · 27 Persuasive authority tropes · 28 Signposting · 29 Fragmented headers
- **Structure patterns** — 30 Unusual small tables · 31 Heading-level skipping · 32 Thematic-break overuse

---

## Content patterns

### 1. Significance inflation

**Watch for:** *stands as, serves as, is a testament/reminder, a vital/significant/crucial/pivotal/key role/moment, underscores/highlights the importance, reflects broader, symbolizing ongoing/enduring/lasting, marking/shaping the, represents a shift, key turning point, evolving landscape, focal point, indelible mark, deeply rooted.*

**Why AI:** LLMs inflate arbitrary facts by claiming they represent a broader trend or historic moment.

**Before:**
> The Statistical Institute was officially established in 1989, marking a pivotal moment in the evolution of regional statistics.

**After:**
> The Statistical Institute was officially established in 1989.

### 2. Notability name-dropping

**Watch for:** *cited in NYT, BBC, FT; independent coverage; active social media presence; written by a leading expert.*

**Why AI:** LLMs hit readers with claims of notability, listing outlets without context.

**Before:**
> Her views have been cited in The New York Times, BBC, Financial Times, and The Hindu.

**After:**
> The New York Times, BBC, Financial Times, and The Hindu have cited her views.

If the outlet list adds no useful context, propose removing it. Do not invent an interview, date or subject to justify the mention.

### 3. Superficial -ing analyses

**Watch for:** *highlighting…, underscoring…, emphasizing…, ensuring…, reflecting…, symbolizing…, contributing to…, cultivating…, fostering…, encompassing…, showcasing…* — usually as a trailing participial clause at the end of a sentence.

**Why AI:** LLMs tack on present-participle codas to fake depth.

**Before:**
> The temple's colours resonate with natural beauty, symbolising bluebonnets, reflecting the community's deep connection to the land.

**After:**
> The temple's colours symbolise bluebonnets and the community's connection to the land.

### 4. Promotional language

**Watch for:** *boasts a, vibrant, rich (figurative), profound, enhancing its, showcasing, exemplifies, commitment to, natural beauty, nestled, in the heart of, groundbreaking (figurative), renowned, breathtaking, must-visit, stunning.*

**Why AI:** LLMs default to a tourism-brochure register for cultural or geographic topics.

**Before:**
> Nestled within the breathtaking region, Alamata stands as a vibrant town with rich cultural heritage and stunning natural beauty.

**After:**
> Alamata is a town in the region with cultural heritage and natural surroundings.

### 5. Vague attributions

**Watch for:** *Industry reports, Observers have cited, Experts argue, Some critics argue, several sources/publications.*

**Why AI:** Attributes opinions to unnamed authorities without specific sources.

**Before:**
> Experts believe it plays a crucial role in the regional ecosystem.

**After:**
> Experts believe it matters to the regional ecosystem.

The experts remain unnamed in the input. Flag that source gap instead of supplying an invented survey or converting the attributed belief into an established fact.

### 6. Formulaic "Challenges and Future Prospects" sections

**Watch for:** *Despite its… faces several challenges…, Despite these challenges, Challenges and Legacy, Future Outlook.*

**Why AI:** LLMs reach for a canned "Challenges" section when the topic does not call for one.

**Before:**
> Despite challenges typical of urban areas, the city continues to thrive as an integral part of growth.

**After:**
> The city continues to grow despite urban challenges.

---

## Language patterns

### 7. AI vocabulary

**High-frequency words:** *actually, additionally, align with, crucial, delve, emphasising, enduring, enhance, fostering, garner, highlight (verb), interplay, intricate/intricacies, key (adjective), landscape (abstract), pivotal, showcase, tapestry (abstract), testament, underscore (verb), valuable, vibrant, moreover, furthermore, indeed, notably.*

**Why AI:** These words appear far more often in post-2023 text and cluster together.

**Before:**
> Additionally, a distinctive feature showcases how these dishes have integrated into the traditional culinary landscape.

**After:**
> These dishes are part of the traditional cuisine.

### 8. Copula avoidance

**Watch for:** *serves as, stands as, marks, represents [a], boasts, features, offers.*

**Why AI:** LLMs substitute elaborate verbs for simple `is`/`are`/`has`.

**Before:**
> Gallery 825 serves as the exhibition space. The gallery features four rooms and boasts over 3,000 square feet.

**After:**
> Gallery 825 is the exhibition space. The gallery has four rooms and over 3,000 square feet.

### 9. Negative parallelisms and tailing negations

**Watch for:** *"Not only… but…", "It's not just about X, it's Y", "…, no guessing", "…, no wasted motion".*

**Why AI:** Over-engineered rhetorical contrast. Also: clipped tailing-negation fragments tacked onto otherwise complete sentences.

**Before:**
> It's not just about the beat; it's part of the aggression.

**After:**
> The beat adds to the aggression.

**Before (tailing negation):**
> The options come from the selected item, no guessing.

**After:**
> The options come from the selected item without forcing the user to guess.

### 10. Rule of three overuse

**Why AI:** LLMs force three-item lists to appear comprehensive, even when two or four would be honest.

**Before:**
> The event features keynote sessions, panel discussions, and networking opportunities. Attendees can expect innovation, inspiration, and industry insights.

**After:**
> The event includes keynote sessions, panel discussions, and networking opportunities.

Three actual programme items remain three. Cut the promotional promise; do not alter the programme or invent when networking happens to change the count.

### 11. Synonym cycling (elegant variation)

**Why AI:** Repetition-penalty code substitutes synonyms where a human would reuse the same word.

**Before:**
> The protagonist faces challenges. The main character must overcome obstacles. The central figure triumphs. The hero returns home.

**After:**
> The protagonist faces challenges and returns home triumphant.

### 12. False ranges

**Watch for:** *"from X to Y"* where X and Y are not on a meaningful scale.

**Before:**
> The journey has taken us from the singularity of the Big Bang to the cosmic web, from the birth of stars to the dance of dark matter.

**After:**
> We explored the Big Bang, the cosmic web, star formation, and dark matter.

### 13. Passive voice and subjectless fragments

**Why AI:** LLMs hide the actor or drop the subject entirely — *"No configuration file needed"*, *"The results are preserved automatically"*.

**Before:**
> No configuration file needed. The results are preserved automatically.

**After:**
> You do not need a configuration file. Results are preserved automatically.

Keep the passive construction when the source does not identify the actor.

---

## Style patterns

### 14. Em-dash overuse

**Why AI:** Em-dashes appear roughly 3× more often in LLM text than in pre-2023 human writing. Most can be commas or periods.

**Before:**
> The term is promoted by institutions — not the people themselves — yet this continues — even in official documents.

**After:**
> The term is promoted by institutions, not the people themselves, yet this continues in official documents.

Keep an em-dash when it marks a genuine break in thought. Drop it when a comma or period reads as well.

### 15. Boldface overuse

**Why AI:** LLMs bold phrases mechanically, diluting emphasis.

**Before:**
> It blends **OKRs**, **KPIs**, and tools such as the **Business Model Canvas** and **Balanced Scorecard**.

**After:**
> It blends OKRs, KPIs, and tools such as the Business Model Canvas and Balanced Scorecard.

### 16. Inline-header vertical lists

**Why AI:** `**Header:** restatement of the header.` — every bullet repeats the label.

**Before:**

> - **Performance:** Performance has been enhanced through optimised algorithms.
> - **Security:** Security has been strengthened with encryption.

**After:**

> - Optimised algorithms improve performance.
> - Encryption strengthens security.

### 17. Title case headings

**Why AI:** LLMs capitalise every main word in headings by default.

**Before:**
> ## Strategic Negotiations And Global Partnerships

**After:**
> ## Strategic negotiations and global partnerships

Match the surrounding repo or site convention — don't force sentence case if the house style is title case.

### 18. Emojis in professional writing

**Before:**
> 🚀 **Launch Phase:** The product launches in Q3
> 💡 **Key Insight:** Users prefer simplicity

**After:**
> The product launches in Q3. Users prefer simplicity.

Preserve emojis when the source register uses them intentionally (changelog conventions, social posts, casual notes).

### 19. Curly quotation marks

**Why AI:** ChatGPT output typically uses curly quotes (`"…"`) where a programmer-authored source would use straight quotes (`"…"`).

**Before:**
> He said “the project is on track” but others disagreed.

**After:**
> He said "the project is on track" but others disagreed.

The Before uses curly `“…”` (U+201C / U+201D); the After uses straight `"…"` (U+0022). Exception: prose intended for typeset publication may legitimately use curly quotes — check the surrounding register.

---

## Communication patterns

### 20. Chatbot artifacts

**Watch for:** *I hope this helps, Of course!, Certainly!, You're absolutely right!, Would you like…, let me know, here is a…*

**Before:**
> Here is an overview of the French Revolution. I hope this helps! Let me know if you'd like me to expand on any section.

**After:**
> (Delete the chatbot wrapper; retain the supplied overview of the French Revolution.)

### 21. Knowledge-cutoff disclaimers

**Watch for:** *as of [date], Up to my last training update, While specific details are limited/scarce…, based on available information…*

**Before:**
> While specific details about the company's founding are not extensively documented in readily available sources, it appears to have been established sometime in the 1990s.

**After:**
> The company appears to have been established in the 1990s; the available sources provide little detail.

Retain meaningful uncertainty and the supplied date range. Stylistic confidence is not evidence.

### 22. Sycophantic tone

**Why AI:** RLHF rewards agreement; leaks into written output.

**Before:**
> Great question! You're absolutely right that this is a complex topic. That's an excellent point!

**After:**
> This is a complex topic.

---

## Filler and hedging

### 23. Filler phrases

| Before | After |
|--------|-------|
| In order to achieve this | To achieve this |
| Due to the fact that | Because |
| At this point in time | Now |
| It is important to note that | (delete) |
| has the ability to | can |
| in the event that | if |
| for the purpose of | to |
| a large number of | many |
| in spite of the fact that | although |

### 24. Excessive hedging

**Before:**
> It could potentially possibly be argued that the policy might have some effect on outcomes.

**After:**
> The policy may affect outcomes.

### 25. Generic positive conclusions

**Before:**
> The future looks bright for the company. Exciting times lie ahead as they continue their journey toward excellence.

**After:**
> (Delete the unsupported positive conclusion. Add no plans absent from the source.)

### 26. Hyphenated word-pair overuse

**Watch for:** *third-party, cross-functional, client-facing, data-driven, decision-making, well-known, high-quality, real-time, long-term, end-to-end* — applied with perfect consistency.

**Why AI:** Humans hyphenate these inconsistently; LLMs hyphenate every instance. Less common technical compounds (e.g., *server-side rendering*) are fine.

**Before:**
> The cross-functional team delivered a high-quality, data-driven report on our client-facing tools.

**After:**
> The team spans several functions and delivered a report of high quality, informed by data, on our tools for clients.

Reformulate rather than merely strip hyphens — *cross functional* and *high quality* (unhyphenated) are not standard English and replace one tell with another. This pattern is soft: apply only when the hyphenation is uniformly consistent across the document and feels mechanical.

### 27. Persuasive authority tropes

**Watch for:** *The real question is, at its core, in reality, what really matters, fundamentally, the deeper issue, the heart of the matter.*

**Why AI:** LLMs pretend to cut through noise to a deeper truth, then restate an ordinary point with extra ceremony.

**Before:**
> The real question is whether teams can adapt. At its core, what really matters is organisational readiness.

**After:**
> The question is whether teams can adapt and whether the organisation is ready.

### 28. Signposting and announcements

**Watch for:** *Let's dive in, let's explore, let's break this down, here's what you need to know, now let's look at, without further ado.*

**Why AI:** Tutorial-script meta-commentary that announces the content instead of delivering it.

**Before:**
> Let's dive into how caching works in Next.js. Here's what you need to know.

**After:**
> (Remove the announcements and start with the supplied explanation of caching in Next.js.)

### 29. Fragmented headers

**Why AI:** A one-line paragraph after a heading restating the heading as a rhetorical warm-up.

**Before:**
> ## Performance
>
> Speed matters.
>
> When users hit a slow page, they leave.

**After:**
> ## Performance
>
> When users hit a slow page, they leave.

---

## Structure patterns

### 30. Unusual small tables

**Watch for:** two- or three-row tables presenting a single fact or a short list that prose would handle better.

**Why AI:** LLMs default to tabular output when asked to "present" or "summarise", even when the content is not tabular.

**Before:**
> | Founded | 1994 |
> | Headquarters | Paris |
> | Employees | ~120 |

**After:**
> Founded in 1994, the company is headquartered in Paris and employs around 120 people.

Keep tables when the content is genuinely comparative — columns with peer values across rows. Replace with prose when the "table" is really a two-column key/value dump.

### 31. Heading-level skipping

**Watch for:** jumping from `##` to `####` with no `###` in between, or any gap of more than one level.

**Why AI:** LLMs treat heading levels as visual sizing rather than document hierarchy. Real hierarchy descends one level at a time.

**Before:**
> ## Overview
>
> #### Background
>
> The service launched in 2021.

**After:**
> ## Overview
>
> ### Background
>
> The service launched in 2021.

This also breaks screen-reader navigation and table-of-contents generation — it is not purely aesthetic.

### 32. Thematic-break overuse

**Watch for:** `---` (horizontal rule) inserted before or after every `##` as a default section separator.

**Why AI:** LLMs use `---` mechanically between every section. Humans use thematic breaks sparingly, when a topic shift is strong enough to warrant a visual pause.

**Before:**
> ## Pricing
>
> …
>
> ---
>
> ## FAQ
>
> …
>
> ---
>
> ## Contact

**After:**
> ## Pricing
>
> …
>
> ## FAQ
>
> …
>
> ## Contact

Keep `---` at genuinely major pivots (end of a long narrative introduction, boundary between tutorial sections and API reference, etc.). Drop it when the heading alone already signals the break.

---

## Full worked example

**Input (AI-heavy):**
> Great question! Here is an essay on this topic. I hope this helps!
>
> AI-assisted coding serves as an enduring testament to the transformative potential of large language models, marking a pivotal moment in the evolution of software development. In today's rapidly evolving technological landscape, these groundbreaking tools — nestled at the intersection of research and practice — are reshaping how engineers ideate, iterate, and deliver, underscoring their vital role in modern workflows.
>
> Additionally, industry observers have noted that adoption has accelerated from hobbyist experiments to enterprise-wide rollouts, from solo developers to cross-functional teams.

**After one pass:**
> AI-assisted coding is changing how engineers plan, revise, and deliver software.
>
> Unnamed industry observers report accelerated adoption beyond hobbyist experiments, including enterprise rollouts and use by solo developers and teams.

**Remaining source gap:** the input does not identify those observers. Keep that attribution qualified and flag the gap; this rewrite supplies no productivity measurements or new research claims.

**Patterns removed:**
- #20 Chatbot artifacts — "Great question!", "I hope this helps!"
- #1 Significance inflation — "testament", "pivotal moment", "evolving landscape", "vital role"
- #4 Promotional language — "groundbreaking", "nestled"
- #8 Copula avoidance — "serves as"
- #3 Superficial -ing — "underscoring", "marking", "reshaping"
- #12 False ranges — "from hobbyist experiments to enterprise-wide rollouts, from solo developers to cross-functional teams"
- #7 AI vocabulary — "additionally", "enduring", "transformative"
