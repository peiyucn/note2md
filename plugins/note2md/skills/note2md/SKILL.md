---
name: note2md
description: Agent-native Markdown note management with Notebook→Section→Page hierarchy. Slash commands: help, init, newnotebook, newsection, newpage (template-first), newtemplate, securecheck, archive. Plugin ships with daily, meeting, and quick-note templates; user templates take priority. Use when the user wants to manage notes, create a notebook/section/page, import from OneNote, or archive old notes.
---

# note2md — Agent-Native Markdown Note Management

You are the interface to the user's note system. All notes use the same **Notebook → Section → Page** hierarchy as OneNote.

```
{notes_root}/
├── {Notebook}/              # Notebook (top-level category)
│   ├── {Section}/           # Section (topic area)
│   │   ├── {page}.md        # Page (an individual note)
│   │   └── ...
│   └── ...
├── _import/                 # Temporary staging for OneNote imports (created on demand)
├── _archive/                # Archive — agent never reads this by default
└── .templates/              # User templates — override plugin defaults
```

>   No lock-in.   Every notebook is a folder, every section is a subfolder, every page is a `.md` file. You can create, rename, move, or delete anything through your file manager — the agent picks up the changes automatically. Commands are optional convenience.

> `{notes_root}` is set during `init` (default: `./notes/`). All paths below use this variable.

> **Root discipline:** once `{notes_root}` is resolved, every artifact — notebooks, `_archive/`, `.templates/`, and the temporary `_import/` staging area — lives under it. Never write import/export artifacts to the current working directory unless the user explicitly chose it as `{notes_root}`.

***

## Command Reference

| Command | What it does |
|---------|-------------|
| `help` | Show this quick-start guide |
| `init` | Setup wizard — pick language, choose root path, import or start fresh |
| `newnotebook [name]` | Create a notebook under `{notes_root}` |
| `newsection [notebook] [section]` | Create a section inside a notebook |
| `newpage` | Create a page — pick template or blank, ask destination, build it |
| `newtemplate` | Extract a template from a section of similar pages |
| `securecheck` | Scan notes for sensitive info (passwords, IDs, bank cards, tokens) |
| `archive` | Archive a notebook, section, or single page |

***

## `help` — Quick-Start Guide

When the user types `help`, reply with a concise guide in their chosen language (default English):

```
📓 note2md — Your Markdown Notebook

Commands:
  init           First-time setup (import OneNote or start fresh)
  newnotebook    Create a new notebook
  newsection     Create a section inside a notebook  
  newpage        Write a note (pick a template — diary, meeting, quick note, or blank)
  newtemplate    Extract a template from a section of similar notes
  archive        Clean up old notebooks, sections, or pages

First time?
  Type init to import your OneNote or create your first notebook.
  Then newnotebook → newsection → newpage to start writing.

Templates?
  newpage always offers templates. The plugin comes with diary, meeting, and quick-note.
  Add your own under notes/.templates/ — they'll appear automatically.
  newtemplate extracts a template from any section with similar pages.

OneNote?
  init imports text content (tables, lists, headings, to-dos). Images, attachments, links, ink, and media are not extracted yet.
  No Python or other runtime needed — conversion is done by the agent itself.
  Auto-export needs Windows + OneNote desktop; on other platforms, point init at any folder of OneNote XML exports.

Security?
  securecheck checks your notes for passwords, ID numbers, bank cards, and API tokens.

Questions? Just ask — you don't need to memorize commands.

No lock-in — every notebook/section/page is just a folder or .md file. You can manage everything through your file manager too.
```

***

## `init` — Setup Wizard

Multi-step guided flow. Use the platform's native question UI (`askQuestions`) at each decision point.

### Step 0 — Language

```
Question: "Select your language / 选择语言："
Options: "中文" | "English"
```

Use the chosen language for all subsequent prompts, confirmations, and generated content.

### Step 1 — Root Path

Don't scan or guess. Just ask:

```
Question: "Use the current directory '{cwd}' as your notes root?"
Options:
  - "Yes — use {cwd}/"
  - "No — let me specify a path"
```

If user specifies a path, use that. Otherwise use `{cwd}/`. Record the result as `{notes_root}`.

### Step 2 — Mode

```
Question: "How would you like to start?"
Options:
  - "Import from OneNote"
  - "Start fresh — create my first notebook"
```

#### Import Path

**No prerequisites.** No Python, no Node, no runtime — conversion is done by you (the agent) natively. The only optional helper is a bundled PowerShell export script, used solely for Windows users with OneNote desktop.

Proceed to the [Import Pipeline](#import-pipeline), which handles platform detection and export options.

**Start import:**

First, check whether `{notes_root}/` already contains anything (excluding `_import/`, `_archive/`, and `.templates/`).

If it is **empty**, proceed straight to the [Import Pipeline](#import-pipeline) — no conflict to resolve.

If it **already has content**, do NOT silently overwrite or clear anything. Ask the user which import mode they want:

```
Question: "⚠️ {notes_root}/ already has notes. How should I handle the existing content?"
Options:
  - "Merge — keep everything, add a (2)/(3)… suffix on any same-name pages" (recommended, non-destructive)
  - "Clear then import — delete everything under {notes_root}/ first, then import fresh"
  - "Cancel"
```

- **Merge** (default): run the Import Pipeline as-is. The existing files stay untouched; the Phase 2 rule "avoid overwrites" (`(2)`, `(3)`, … suffix) applies on top of them.
- **Clear then import**: before running the pipeline, delete the contents of `{notes_root}/` **except** `_import/`, `_archive/`, and `.templates/` — and confirm once more before deleting:

  ```
  Question: "This will permanently delete all current notes under {notes_root}/. Continue?"
  Options: "Yes, clear everything and import" | "No, go back"
  ```

  Only after the user confirms, delete those folders/files, then run the [Import Pipeline](#import-pipeline).

After import, tell the user: "Import complete. Use `newtemplate` on any section with similar pages to create templates."

#### Fresh Start Path

1. Ask: "First notebook name?"
2. Create:

   ```
   {notes_root}/
   ├── {Notebook}/
   ├── Quick Notes/
   ├── _archive/
   └── .templates/
   ```
3. Ask: "First section name in {Notebook}?"
4. Create `{notes_root}/{Notebook}/{Section}/`
5. Confirm: "All set! '{Notebook}' and 'Quick Notes' created. Use `newpage` to write your first note."

### Step 3 — Done

Setup complete. The resolved `{notes_root}` is used for all subsequent operations.

***

## `newnotebook` — Create Notebook

| Step | Action |
|------|--------|
| 1 | Get name — from argument (`newnotebook Work`) or ask user |
| 2 | If `{notes_root}/{Name}/` exists → warn, ask for a different name |
| 3 | Create `{notes_root}/{Name}/` |
| 4 | Confirm: "Notebook '{Name}' created. Use `newsection` to add sections." |

***

## `newsection` — Create Section

| Step | Action |
|------|--------|
| 1 | Get notebook + section — from arguments or ask (list notebooks, exclude `_archive/`) |
| 2 | Create `{notes_root}/{Notebook}/{Section}/` |
| 3 | Confirm: "Section '{Section}' created in '{Notebook}'." |

***

## `newpage` — Create Page

Template-first; "blank page" always available as the last option.

**Fast path**: `newpage` with no argument → skip template selection, create a blank page directly. User only needs to pick destination and title.

**With argument**: `newpage daily` → use daily template; `newpage meeting` → use meeting template, etc.

### Step 1 — Discover Templates

Scan in priority order:

1. `{notes_root}/.templates/*.md` (user templates — highest priority)
2. `<skill_dir>/templates/*.md` (plugin defaults — fallback)

Plugins defaults: `daily.md`, `meeting.md`, `quick-note.md`. See [Template System](#template-system).

### Step 2 — Resolve Template

| Condition | Action |
|-----------|--------|
| `newpage` (no argument) | Skip to Step 3 — blank page |
| `newpage {name}` (argument provided) | Try exact match against discovered templates. If found → use it. If not found or ambiguous → present choices: |

```
Question: "Which template?"
Options:
  - ...any user templates found in .templates/...  ← user templates FIRST
  - "📅 Daily Journal (daily)"
  - "🤝 Meeting Notes (meeting)"
  - "💡 Quick Note (quick-note)"
  - "📄 Blank page — no template"
```

### Step 3 — Destination

Ask: notebook → section → page title. Allow creating new notebook/section inline.

### Step 4 — Frontmatter

| Condition | Action |
|-----------|--------|
| Template has `---`...`---` YAML | Use as-is, replace `{{VARIABLE}}` placeholders |
| No frontmatter in template | Generate default |

Default frontmatter:

```yaml
---
date: YYYY-MM-DD
type: {filename_without_.md}    # e.g. "daily", "meeting"; "note" for blank
title: {user_input}
tags: []
---
```

### Step 5 — Body

| Choice | Action |
|--------|--------|
| Template | Read `.md`, replace `{{DATE}}`, `{{TITLE}}`, `{{TOPIC}}`. Ask for unknown `{{KEY}}`. |
| Blank | No body — frontmatter only |

### Step 6 — Filename

Match `type` against the naming rules below (see [File Naming](#file-naming)). Append `(2)` if exists.

### Step 7 — Confirm

```
Created: {notes_root}/{Notebook}/{Section}/{filename}.md
```

***

## `archive` — Archive Notebooks, Sections, or Pages

Triggered by `archive` command, or when agent notices 5+ notebooks.

### Step 1 — Scope

```
Question: "What do you want to archive?"
Options:
  - "Entire notebook"
  - "A specific section"
  - "A single page"
```

### Step 2 — Select Target

| Scope | Action |
|-------|--------|
| Notebook | List all notebooks (excluding `_archive/`), ask which one |
| Section | List notebooks → ask which one → list its sections → ask which one |
| Page | List notebooks → section → ask which page |

Highlight items untouched for > 3 months. Allow multi-select.

### Step 3 — Confirm & Move

Preserve the original directory structure under `_archive/`:

| Scope | Moves |
|-------|-------|
| Notebook | `{notes_root}/{Notebook}/` → `{notes_root}/_archive/{Notebook}/` |
| Section | `{notes_root}/{Notebook}/{Section}/` → `{notes_root}/_archive/{Notebook}/{Section}/` |
| Page | `{notes_root}/{Notebook}/{Section}/{page}.md` → `{notes_root}/_archive/{Notebook}/{Section}/{page}.md` |

Empty parent directories left behind? Clean them up (e.g. if all sections of a notebook are archived, the notebook folder becomes empty — ask if it should be removed).

### Step 4 — Context Refresh

Archiving large content saves tokens and keeps attention focused on active notebooks. After archiving, ask:

```
Question: "Archive done. Refresh context to focus on the leaner active set and save tokens?"
Options:
  - "Yes — refresh context" (recommended after large archives)
  - "Not now"
```

If user confirms, re-scan `{notes_root}/` (excluding `_import/` and `_archive/`) to rebuild the working context with only active notebooks.

### Rules

* Never read `_import/` or `_archive/` during normal operations
* Only search `_archive/` when user says "search archive"
* Archived items can be restored by moving them back to their original path

***

## `securecheck` — Security Check

Scans `{notes_root}/` (excluding `_import/` and `_archive/`) for sensitive information. Read files directly — you understand context, not just regex.

### What to Look For

Read each page and flag anything that looks like:

* Passwords or credentials (`password`, `pwd`, `密码` near `=` or `:`)
* Government IDs (Chinese 18-digit ID, US SSN, passport numbers, driver's license)
* Financial data (bank card numbers, `credit`, `银行卡`)
* API keys and tokens (`sk-...`, `ghp_...`, `Bearer ...`, `Authorization:` headers)
* Personal contact (phone numbers, email addresses in unexpected places)

Use your judgment — if it walks like a secret, flag it.

### Procedure

1. Announce: "Scanning your notes for sensitive information…"
2. Ask if user wants to add custom checks:

   ```
   Question: "I'll check for passwords, IDs, bank cards, API keys, and personal contact info. Anything else to look for?"
   Options:
     - "No — just the defaults" (default)
     - "Let me add custom patterns" (free text input — e.g. "internal project codes like PRJ-XXXX", "company confidential headers")
   ```

   If custom patterns provided, add them to the scan list.
3. Search across `{notes_root}/` (skip `_import/`, `_archive/` and `.templates/`)
4. For each match:

   * Report the file path and line number
   * Show the matching category (NOT the actual sensitive value)
   * Example: `⚠️ notes/Work/Projects/credentials.md:12 — Possible password`
5. Never output the actual sensitive value. Use `[REDACTED]` if context is needed.
6. Summary: "Found N potential issues across M files."
7. Remind: "You can move sensitive files to \_archive/ or delete them. Use archive to clean up."

### Scope Options

If user wants targeted scan:

```
Question: "Scan everything, or a specific area?"
Options:
  - "All notebooks (recommended)"
  - "A specific notebook"
  - "A specific section"
```

***

## Template System

### Priority

```
{notes_root}/.templates/{name}.md    ← User override (highest)
<skill_dir>/templates/{name}.md      ← Plugin default (fallback)
```

### Built-in Defaults

| Template | File |
|----------|------|
| Daily Journal | `daily.md` |
| Meeting Notes | `meeting.md` |
| Quick Note | `quick-note.md` |

### Creating User Templates

**`newtemplate` — Extract template from a section:**



1. Ask: which notebook → which section to analyze.
2. Give the user a chance to describe their needs before extracting:

   ```
   Question: "I'll analyze the pages in '{Section}' to build a template. Any specific requirements?"
   Options:
     - "No preference — just find the common structure" (default)
     - "Let me describe what I want" (free text input)
   ```
3. Read all `.md` pages in that section. If the user provided requirements, use them to guide the extraction (e.g. "focus on the action items section", "combine the agenda and notes patterns").
4. Compare their structure to find common patterns:

   * Same frontmatter keys appearing in ≥ 60% of pages → keep as `{{VARIABLE}}`
   * Same heading hierarchy (##, ###) → keep the skeleton
   * Body text that varies → replace with representative {{PLACEHOLDER}}
5. Show the extracted template and report: "Found N pages with similar structure in '{Section}'."
6. Ask: "Save this template? Give it a name."
7. Write to `{notes_root}/.templates/{name}.md`. From now on, `newpage` will include it.



**Manual**: Drop `.md` files into `{notes_root}/.templates/`. Auto-discovered by `newpage`.

***

## Import Pipeline

1:1 mapping — OneNote structure preserved as-is. Only the Recycle Bin is skipped (system folder, not user content).

**No runtime dependencies.** No Python, no Node — conversion is done by you (the agent) natively. The only optional helpers are bundled PowerShell scripts: `export-onenote.ps1` (Windows-only, OneNote COM API) and `format-onenote-xml.ps1` (pretty-printing, see Phase 1.5).

### Phase 0 — Platform Detection

Detect the user's OS before offering any export option:

| Platform | How to detect |
|----------|---------------|
| Windows | `$env:OS` / `ver` in PowerShell, or check for a `C:\` drive |
| macOS | `uname -s` → `Darwin` |
| Linux | `uname -s` → `Linux` |

If you cannot detect reliably, just ask the user.

### Phase 1 — Obtain XML Export

**Windows + OneNote desktop (2016+):** offer auto-export.

```
Question: "How to export your OneNote data?"
Options:
  - "Auto-export (Windows + OneNote desktop)" → runs export-onenote.ps1
  - "I already have XML files — point me to the path"
```

If auto-export:

```
Question: "Export to which directory?"
Options: "Default ({notes_root}/_import/)" | "Custom path"
```

The default is inside `{notes_root}` (never the current working directory) so import artifacts never pollute the workspace. If the user picks the default, use `{notes_root}/_import/` — create the directory if missing. If they pick custom, use their path as-is.

Run: `powershell -File "<skill_dir>/tools/export-onenote.ps1" -OutputDir "<path>"`
Requires Windows + Office 2016+, COM API. The script refuses to run without an explicit `-OutputDir`.

**Verify the export result (mandatory) — never proceed on an unverified export:**

1. The script completed without errors (check the exit code and error output).
2. The output directory contains **at least one** `*.xml` file. Zero XML files means the export failed — e.g. OneNote desktop not installed, COM not registered, or all notebooks empty.
3. Scan the script output for `FAIL:` lines; report every failed page to the user by name.
4. Structure sanity check: pages sit under Notebook/Section folders as `{PageName}.xml`.

If the export failed or produced no XML: tell the user what went wrong and fall back to the manual path below. Never continue to conversion with an empty or broken export.

**macOS / Linux (or no OneNote desktop):** the COM API is Windows-only, so `export-onenote.ps1` **cannot run here** — auto-export is not available. Tell the user this plainly: *they must obtain the XML exports themselves* (e.g. run the export on a Windows machine with OneNote desktop, or use any tool that produces OneNote page XML). You only handle the conversion. Then offer:

```
Question: "Auto-export isn't available on this system (needs Windows + OneNote desktop). Please export your notebooks to XML yourself, or choose another option:"
Options:
  - "I have XML exports (e.g. exported elsewhere) — point me to the path"
  - "Skip import — start fresh instead"
```

If the user points to a path, verify it actually contains XML files before continuing (see the checks above).

XML exports are plain files — they can come from any machine or tool. What matters: each page is a `.xml` file containing OneNote page XML (namespace `http://schemas.microsoft.com/office/onenote/2013/onenote`), typically named `{PageName}.xml` inside a Notebook/Section folder structure. Accept any path containing such files.

### Phase 1.5 — Pretty-print XML for Reliable Reading

OneNote page XML is often a **single very long line** (tens of thousands of characters per file). Agent file-reading tools truncate long lines, so a raw export cannot be read faithfully — content gets silently dropped during conversion.

**Before converting, make sure every `.xml` file is readable in full.** Sample 2–3 files first: if any line exceeds ~2,000 characters, pretty-print the export.

How to pretty-print (choose one):

1. **Bundled helper** (Windows, or anywhere `powershell` is available):
   `powershell -File "<skill_dir>/tools/format-onenote-xml.ps1" -InputDir "<export_dir>"`
   - Output goes to `<export_dir>_pretty/` by default.
   - `-InPlace` rewrites the files in place; `-OutputDir "<path>"` writes elsewhere.
   - Keep everything under the staging area — never write to the workspace root.
2. **Agent-native** (no script): read each file, parse it, and write it back indented. The bundled script is the reference behavior; a capable agent can do the same thing directly.

Verification after formatting (mandatory):

1. Re-sample the formatted files — every `<one:OE>` / `<one:T>` line must now be on its own readable line.
2. Confirm the formatted tree has the same Notebook/Section structure and the same set of `.xml` files as the source (count match).

Point the conversion step at the pretty-printed copy (or keep the same path if `-InPlace`). The `.xml` → `.md` rules below apply unchanged.

### Phase 2 — Convert (agent-native, no scripts)

You do the conversion yourself — this is the core of the import and needs no external tools:

1. Walk the export directory recursively for `*.xml` files. If Phase 1.5 produced a pretty-printed copy, walk **that** copy; otherwise walk the original export.
2. Preserve the relative folder structure: Notebook → SectionGroup → Section.
3. Convert each page per the [XML → Markdown Conversion Rules](#xml--markdown-conversion-rules).
4. Write `{title}.md` (YAML frontmatter + body) into `{notes_root}/`, mirroring the structure.
5. Avoid overwrites: if a `.md` already exists, append `(2)`, `(3)`, …
6. Report: "Converted N pages → {notes_root}."

`{notes_root}/_import/` is temporary staging — remind the user to delete it after the import.

### Phase 3 — Verify (mandatory)

Conversion is format mapping, not creative writing. Determinism comes from a hard verification pass — never skip it:

1. **Count check**: number of `*.xml` files found == number of `.md` files written. A mismatch means something was dropped.
2. **Spot check**: open 2–3 random source XML files and their `.md` outputs; verify title, headings, tables, lists, and to-dos match the rules exactly.
3. **Failure report**: any page that failed to convert → report its path and reason to the user. Never silently drop.
4. **Fix and re-verify**: correct any deviation found, then re-run checks 1–2.
5. **Large imports**: process in batches (e.g. 50 pages at a time) to avoid attention decay; verify each batch before moving on.

Then report: "Converted N pages → {notes_root}." (If any failed, add: "M pages failed — see list above.")

### XML → Markdown Conversion Rules

Apply page by page, mechanically. This is format conversion, not creative writing — follow the tables exactly. Do not add, omit, rewrite, or "improve" content. If something does not match any rule, note it and ask — do not guess.

**Frontmatter**

| Field | Source |
|-------|--------|
| `title` | `<one:Page name="...">` attribute; fallback: text of first `<one:Title/one:OE>`; last resort: filename |
| `date` | `dateTime` or `lastModifiedTime` attribute, take `YYYY-MM-DD`; fallback: today |
| `type` | Heuristic from title/content: `meeting` (例会/会议/meeting/review), `daily` (日记/daily/journal), `task` (待办/todo/action item), else `note` |
| `tags` | `[]` |

**Body — element mapping**

| OneNote element | Markdown output |
|-----------------|-----------------|
| Text — collect all `<one:T>` descendants | plain text; strip embedded HTML `<span>` tags, unescape entities |
| `<one:OE bold="1">` / `italic="1"` | `**text**` / `*text*` (both → `***text***`) |
| Heading (`quickStyleIndex` or `style` containing "heading") | `#` × min(level, 6) |
| To-do — `<one:Tag index="0">` | `- [ ] ` unchecked |
| To-do — `<one:Tag index="1">` | `- [x] ` checked |
| List — `<one:List>` present, or `<one:Tag>` with other index | `- ` bullet; nested `<one:OE>` children indent 2 spaces per level |
| `<one:Table>` → `<one:Row>` → `<one:Cell>` | Markdown table; line breaks inside a cell → `<br>`; skip fully empty rows |

**To-dos inside table cells** — GFM table cells cannot contain Markdown task lists (`- [ ]` inside a cell is not valid and loses the checkbox). When a to-do `<one:Tag index="0|1">` appears **inside a `<one:Cell>`**, keep the table structure and use a **text marker** instead of a list:

| Cell content | Markdown output |
|---|---|
| `<one:Tag index="0">` + text in a cell | `[ ] text` |
| `<one:Tag index="1">` + text in a cell | `[x] text` |
| Multiple `<one:OE>` in one cell | Join with `<br>`, prefix each to-do OE with its `[ ]` / `[x]` marker |

Example: a cell containing two OEs — plain text then an unchecked to-do — becomes `plain text<br>[ ] action item`.

**Lists (ordered/unordered) inside table cells** — the same constraint applies to any list inside a cell: `<one:Number>` (ordered), `<one:Bullet>` (unordered), and `<one:Tag>` all cannot render as native Markdown lists inside a cell. Use text markers too:

| Cell content | Markdown output |
|---|---|
| Ordered item — `<one:List><one:Number text="1.">` + text | `1. text` (use the `text` attribute, fallback to auto-numbering from 1) |
| Unordered item — `<one:List><one:Bullet>` + text | `- text` (literal dash + space, NOT a list) |
| Nested `<one:OEChildren>` inside a cell | indent with **2 spaces per level**, same as outside tables |

**Mixed nested trees inside a cell** — when a cell contains a multi-level tree mixing to-dos, ordered items, and plain text (very common in OneNote — e.g. a 2-column table whose content column holds a whole task tree), render the tree **inline inside the cell** as a text tree using `↳` (U+21B3) at each nesting level:

- Top-level items are joined by `<br>`.
- Each nesting level is prefixed by `↳ ` (one `↳` per level, with a leading space per level).
- Markers are kept: `[ ]`/`[x]` for to-dos, `1.`/`2.` or the literal `text` attribute for ordered, `-` for unordered.
- Cell content that is only plain text stays as-is.

Example — a cell containing:
```
[ ] I17情况追踪
  ↳ [x] 基本情况与进度
  ↳ [ ] 测试阶段
[x] 2026年IT预算
```
becomes: `[ ] I17情况追踪<br>↳ [x] 基本情况与进度<br>↳ [ ] 测试阶段<br>[x] 2026年IT预算`

When a whole row (or the whole table) is just a list/tree with no real tabular structure (e.g. a single column of to-dos used as a checklist), the agent **may** extract it from the table and render it as a native Markdown list below the table, keeping a stub cell in the table — flag this in the final report.

**Fallback — anything not covered above:** if a cell contains a structure none of the rules above handle, do NOT guess or drop content. Export conservatively: a plain Markdown table cell with **every text fragment joined by `<br>`**, in source order, stripping only markup. The goal is zero text loss — every word stays inside the table even if the structure flattens. Note the cell in the final report as "fallback-rendered".
| `<one:Image>` | skip (not extracted yet) |

Structure notes:

- `<one:OEChildren>` is a wrapper — recurse into it, emit nothing.
- An `<one:OE>` that only contains `Table`/`OEChildren` emits nothing itself.
- Skip Recycle Bin content (`OneNote_RecycleBin`, `isRecycleBin="true"`).
- Body starts with `# {title}`.
- Filenames: replace `\/:*?"<>|` with `_`.
- Collapse 3+ blank lines to 2; strip trailing whitespace.

**Loss matrix:** images, attachments, hyperlinks, ink, math, audio, and video are intentionally not converted. Full breakdown: `docs/onenote-loss-matrix.md` in the plugin repo.

***

## File Naming

Default naming rules:

| type | pattern | example |
|------|---------|---------|
| `daily` | `{date}.md` | `2026-07-29.md` |
| `meeting` | `{date}-{topic}.md` | `2026-07-29-product-review.md` |
| `quick-note` | `{date}-{title}.md` | `2026-07-29-idea.md` |
|  (default)   | `{title}.md`        | `my-note.md`                   |

> ⚠️ When editing this file, keep `SKILL-CN.md` (`../../SKILL-CN.md`) in sync. It is the Chinese reference version for the plugin author.

