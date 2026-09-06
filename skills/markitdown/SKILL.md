---
name: markitdown
description: Extract document text as Markdown with Microsoft's MarkItDown CLI. Use for file conversion or YouTube transcripts; image OCR and audio transcription require verified optional backends and their data-transfer permissions.
when_to_use: When the user has a non-Markdown file (PDF, DOCX, PPTX, XLSX, HTML, CSV, JSON, XML, EPub, ZIP, image, audio) or a YouTube URL and wants the contents as Markdown — for reading, summarising, feeding to an LLM, or saving as a clean text file. Keywords — convert to markdown, extract text, ocr, transcribe, read pdf, parse document, youtube transcript, markitdown, doc to md. Skip when the file is already Markdown, when the user wants visual rendering instead of text extraction, or when only a tiny snippet is needed and the Read tool is faster.
argument-hint: "[-s] [-S] [-d] [-p] [-k] [-l] <file-or-url>"
allowed-tools: Bash(bash *) Bash(markitdown *) Bash(command *) Read
license: MIT
compatibility: "Requires bash and an installed MarkItDown CLI with the converter extras needed by the input. Audio/OCR/plugin backends can use external services; verify configuration and authorized data transfer before processing."
metadata:
  author: coroboros
  sources: "github.com/microsoft/markitdown"
---

# MarkItDown

Convert a document, image, audio file, or YouTube URL to Markdown using Microsoft's [`markitdown`](https://github.com/microsoft/markitdown) CLI. The skill validates the input, composes the right flags, optionally saves the result under `~/.agents/output/<project>/markitdown/<slug>/`, and reports a one-line summary with the fully-expanded absolute path (no tilde, no magic).

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
| `[audio-transcription]` | MP3/WAV transcription; the current converter sends audio to Google recognition |
| `[youtube-transcription]` | YouTube transcripts |
| `[az-doc-intel]` | Azure Document Intelligence backend |

For Azure Document Intelligence, also export `MARKITDOWN_DOCINTEL_ENDPOINT=https://<resource>.cognitiveservices.azure.com/` before invoking with `-d`.

## Parameters

| Flag | Default | Effect |
|------|---------|--------|
| `-s` | off | Save Markdown to `~/.agents/output/<project>/markitdown/<slug>/<stem>.md` |
| `-S` | off | Force no-save (override an ambient save mode) |
| `-d` | off | Use Azure Document Intelligence (needs `MARKITDOWN_DOCINTEL_ENDPOINT`) |
| `-p` | off | Enable installed third-party `markitdown` plugins |
| `-k` | off | Keep data URIs (base64 images) inline in the output |
| `-l` | — | List installed plugins and exit |

Output saved under `~/.agents/output/{project}/markitdown/{slug}/`, where `{project}` is the kebab-cased basename of the git toplevel (else cwd) and `{slug}` is a kebab of the input basename (≤5 words). Pipeline-friendly — typical downstream: `/forge -s -f <path>` decomposes the extracted content into workstreams; `/apex -f <path>` implements from it; any skill accepting `-f` can consume.

## Workflow

1. Resolve the target from arguments or unambiguous session context. Ask only when the target is missing or ambiguous. Before audio, OCR, Azure or plugin conversion, verify the installed backend and required data-transfer authorization; an optional dependency group does not imply local processing.
2. Run the helper:

   `$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing this SKILL.md elsewhere.

   ```bash
   bash "$SKILL_DIR"/scripts/markitdown.sh -s '/absolute/path/report.pdf'
   ```

   Parse arguments as data and pass each flag/value separately with shell quoting. Never splice raw `$ARGUMENTS` into shell code or use `eval`.

3. The script emits `RESULT: key=value` lines — keys: `bytes`, `slug`, `saved`, plus `path` when saving (order is not guaranteed; parse by key) — followed either by the converted Markdown (no-save mode, after a `---` separator) or nothing (save mode — the file is on disk).
4. Parse the `RESULT:` lines and produce the report below.
5. If the script exits with `ERR: markitdown not installed` (exit 127) → print the install command from `## Install` and stop. Never auto-install on the user's behalf.
6. If the script exits with another `ERR:` (file not found, missing endpoint, unknown flag) → relay the message verbatim and stop.

## Output

```
markitdown: <input> → <bytes> bytes of Markdown
saved: <path>      # only when -s
```

When saving, report the actual file path. For long output, choose save mode when consistent with the request or capture stdout once in an authorized temporary file, then provide a bounded preview and the retained result. Do not repeat a costly conversion merely to truncate its display.

## Examples

```bash
/markitdown ~/Downloads/report.pdf            # convert, print to terminal
/markitdown -s ~/Downloads/report.pdf         # convert + save under ~/.agents/output/<project>/markitdown/report/
/markitdown -s -p deck.pptx                   # use third-party plugins (e.g. markitdown-ocr)
/markitdown -d invoice.pdf                    # Azure Document Intelligence
/markitdown -k brand.html                     # keep base64 images inline
/markitdown https://youtu.be/dQw4w9WgXcQ      # YouTube transcript
/markitdown -l                                # list installed plugins, then exit
```

## Notes

- **YouTube URLs** are detected by the `https?://` prefix and passed straight to `markitdown`. The slug is derived from the URL's last path segment, so saved paths look like `~/.agents/output/<project>/markitdown/dqw4w9wgxcq/dQw4w9WgXcQ.md`.
- **Audio transcription** in the verified 0.1.7 converter calls `recognize_google`; it is not local Whisper. Inspect the installed implementation and [Microsoft's source](https://github.com/microsoft/markitdown/blob/main/packages/markitdown/src/markitdown/converters/_transcribe_audio.py) before processing. A local/private-only request needs an actually local configured tool; do not send audio externally under a local-processing promise.
- **Image OCR** requires a configured capable backend. The [Microsoft OCR plugin instructions](https://github.com/microsoft/markitdown#markitdown-ocr-plugin) require an `llm_client` and model; installing the plugin and passing `-p` alone is insufficient. Report unavailable OCR explicitly and use the documented integration only when its configuration and transport are authorized.
- **Saved-output collisions** fail before conversion if the destination already exists. Use another destination/input identity or obtain authorization to replace the existing output; slug naming alone does not preserve files.

## Why the wrapper

`markitdown` is already a great CLI; this skill exists to (a) follow the repo's `-s/-S/-f` convention so other skills can chain on the output, (b) translate "extract this pdf" into the right invocation without forcing the user to remember `-x`, `-m`, `-d`, `-e`, and (c) emit a uniform one-line report so terminals don't render multi-MB Markdown by accident.
