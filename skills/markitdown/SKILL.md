---
name: markitdown
description: Convert any document to Markdown with Microsoft's `markitdown` CLI — PDF, Word, Excel, PowerPoint, HTML, CSV, JSON, XML, ZIP, EPub, images (OCR/EXIF), audio (transcription), and YouTube URLs. Use whenever the user wants to extract text from a binary document, transcribe audio, OCR an image, scrape a YouTube transcript, or pre-process a file for an LLM context window — even when they just say "convert this pdf", "what's in this docx", "transcribe this mp3", or "get the text out of this".
when_to_use: When the user has a non-Markdown file (PDF, DOCX, PPTX, XLSX, HTML, CSV, JSON, XML, EPub, ZIP, image, audio) or a YouTube URL and wants the contents as Markdown — for reading, summarising, feeding to an LLM, or saving as a clean text file. Keywords — convert to markdown, extract text, ocr, transcribe, read pdf, parse document, youtube transcript, markitdown, doc to md. Skip when the file is already Markdown, when the user wants visual rendering instead of text extraction, or when only a tiny snippet is needed and the Read tool is faster.
argument-hint: "[-s] [-S] [-d] [-p] [-k] [-l] <file-or-url>"
model: sonnet
allowed-tools: Bash(bash *) Bash(markitdown *) Bash(command *) Read
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
metadata:
  author: coroboros
  sources:
    - github.com/microsoft/markitdown
---

# MarkItDown

Convert a document, image, audio file, or YouTube URL to Markdown using Microsoft's [`markitdown`](https://github.com/microsoft/markitdown) CLI. The skill validates the input, composes the right flags, optionally saves the result under `.claude/output/markitdown/<slug>/`, and reports a one-line summary.

The deterministic work — install check, validation, slug derivation, save path, command composition — happens in `scripts/markitdown.sh`. The skill parses `$ARGUMENTS`, hands them to the script, and turns the script's `RESULT:` lines into a human report.

## Install

```bash
pip install 'markitdown[all]'
```

For a smaller install, pick only what you need:

| Group | Adds |
|-------|------|
| `[pdf]` | PDF parsing |
| `[docx]` | Word documents |
| `[pptx]` | PowerPoint |
| `[xlsx]` `[xls]` | Excel |
| `[outlook]` | Outlook `.msg` |
| `[audio-transcription]` | MP3/WAV via local Whisper |
| `[youtube-transcription]` | YouTube transcripts |
| `[az-doc-intel]` | Azure Document Intelligence backend |

For Azure Document Intelligence, also export `MARKITDOWN_DOCINTEL_ENDPOINT=https://<resource>.cognitiveservices.azure.com/` before invoking with `-d`.

## Parameters

| Flag | Default | Effect |
|------|---------|--------|
| `-s` | off | Save Markdown to `.claude/output/markitdown/<slug>/<stem>.md` |
| `-S` | — | Force no-save (override an ambient save mode) |
| `-d` | off | Use Azure Document Intelligence (needs `MARKITDOWN_DOCINTEL_ENDPOINT`) |
| `-p` | off | Enable installed third-party `markitdown` plugins |
| `-k` | off | Keep data URIs (base64 images) inline in the output |
| `-l` | — | List installed plugins and exit |

`<slug>` is the kebab-cased input basename, max 5 words. Pipeline-friendly — typical downstream: `/spec -s -f <path>` decomposes the extracted content into workstreams; `/apex -f <path>` implements from it; any skill accepting `-f` can consume.

## Workflow

1. **Empty `$ARGUMENTS`** → ask for a file path or URL and stop. Do not guess.
2. Run the helper:

   ```bash
   bash ${CLAUDE_SKILL_DIR}/scripts/markitdown.sh $ARGUMENTS
   ```

3. The script emits `RESULT: key=value` lines — keys: `bytes`, `slug`, `saved`, plus `path` when saving (order is not guaranteed; parse by key) — followed either by the converted Markdown (no-save mode, after a `---` separator) or nothing (save mode — the file is on disk).
4. Parse the `RESULT:` lines and produce the report below.
5. If the script exits with `ERR: markitdown not installed` (exit 127) → print the install command from `## Install` and stop. Never auto-install on the user's behalf.
6. If the script exits with another `ERR:` (file not found, missing endpoint, unknown flag) → relay the message verbatim and stop.

## Output

```
markitdown: <input> → <bytes> bytes of Markdown
saved: <path>      # only when -s
```

When saving, just report. When not saving, also stream the converted Markdown back to the user; if it exceeds ~80 lines, show the first 80 and tell the user to re-run with `-s` to capture the full output.

## Examples

```bash
/markitdown ~/Downloads/report.pdf            # convert, print to terminal
/markitdown -s ~/Downloads/report.pdf         # convert + save under .claude/output/markitdown/report/
/markitdown -s -p deck.pptx                   # use third-party plugins (e.g. markitdown-ocr)
/markitdown -d invoice.pdf                    # Azure Document Intelligence
/markitdown -k brand.html                     # keep base64 images inline
/markitdown https://youtu.be/dQw4w9WgXcQ      # YouTube transcript
/markitdown -l                                # list installed plugins, then exit
```

## Notes

- **YouTube URLs** are detected by the `https?://` prefix and passed straight to `markitdown`. The slug is derived from the URL's last path segment, so saved paths look like `.claude/output/markitdown/dqw4w9wgxcq/dQw4w9WgXcQ.md`.
- **Audio transcription** uses local Whisper via the `[audio-transcription]` extra. It's CPU-bound — warn the user before kicking off a long podcast.
- **Image OCR** without the `markitdown-ocr` plugin only reads embedded EXIF text. For pixel-level OCR, `pip install markitdown-ocr` and pass `-p`.
- **No silent overwrites** — `markitdown` itself overwrites with `-o`, but the slug-namespaced save path makes collisions predictable, not surprising.

## Why the wrapper

`markitdown` is already a great CLI; this skill exists to (a) follow the repo's `-s/-S/-f` convention so other skills can chain on the output, (b) translate "extract this pdf" into the right invocation without forcing the user to remember `-x`, `-m`, `-d`, `-e`, and (c) emit a uniform one-line report so terminals don't render multi-MB Markdown by accident.
