# Voice calibration — optional

Loaded only when the user explicitly asks for a voice-matching pass on an opinion piece, personal essay, or any format where personality is part of the brief. For docs, specs, and READMEs, **do not** load this file — neutral-precise is the default register.

## When this applies

- The user asks *"match my voice"*, *"humanize in my style"*, *"use this as a reference"*, *"sound like me"*.
- The user provides a writing sample inline or as a file path.
- The target piece is a blog post, op-ed, changelog commentary, or similar editorial format.

**Do not apply** to READMEs, API docs, release notes, commit messages, or formal technical writing even when the user provides a sample — clean up the AI patterns, keep the register neutral.

## Sample-first workflow

1. **Read the sample before rewriting.** Note:
   - Sentence length — short and punchy, long and flowing, or mixed?
   - Word choice level — casual, academic, or in between?
   - How the writer opens paragraphs — jump in, or set context?
   - Punctuation habits — dashes, parentheticals, semicolons?
   - Recurring phrases or verbal tics.
   - Transition style — explicit connectors, or straight into the next point?

2. **Rewrite using the sample's patterns.** Don't just remove AI tells; replace them with moves the sample actually makes. If the sample favours short sentences, the rewrite uses short sentences. If the sample uses "stuff" and "things", don't upgrade to "elements" and "components".

3. **Still apply all 32 patterns** from `patterns.md`. Voice calibration augments pattern removal; it does not replace it.

## What not to do

- Don't invent a voice the sample doesn't have. If the sample is plain and functional, the rewrite stays plain and functional — adding personality on top would contradict the sample.
- Don't override the user's register. If they write formally, stay formal. If they write with contractions, use contractions.
- Don't let voice calibration become an excuse for sycophancy, sloganeering, or editorial drift. The core goal is still honest, direct prose.

## How to ask for a sample

```
# inline
"Humanize this draft. Here's a sample of my previous writing to match the voice: [sample]"

# file
"Humanize this draft. Match the voice in ~/writing/sample.md."
```

When no sample is given and this file is not loaded, fall back to the default neutral-precise register from `SKILL.md`.
