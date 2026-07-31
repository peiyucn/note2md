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
├── _archive/                # Archive — agent never reads this by default
└── .templates/              # User templates — override plugin defaults
```

>   No lock-in.   Every notebook is a folder, every section is a subfolder, every page is a `.md` file. You can create, rename, move, or delete anything through your file manager — the agent picks up the changes automatically. Commands are optional convenience.

> `{notes_root}` is set during `init` (default: `./notes/`). All paths below use this variable.

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
  init handles the full import. Windows + OneNote desktop required for auto-export.

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

**Prerequisite — Python check:**

Before import, verify Python is available by running `python --version` or `python3 --version`. If neither works:

```
Question: "OneNote import requires Python 3. To install it, run: winget install Python.Python.3.12
Or download from https://python.org. After installing, re-run init. Ready to continue?"
Options:
  - "I'll install Python and come back"
  - "Skip import — start fresh instead"
```

If user skips, fall back to the Fresh Start path. Otherwise, wait for them to install and retry.

**Start import:**

If `{notes_root}/` already has notebooks (excluding `_archive/`), warn:

```
Question: "⚠️ {notes_root}/ already has notes. Import will OVERWRITE them. Continue?"
Options: "Overwrite and import" | "Cancel"
```

If cancelled, stop. Otherwise run the [Import Pipeline](#import-pipeline) targeting `{notes_root}`. After import, tell the user: "Import complete. Use `newtemplate` on any section with similar pages to create templates."

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



Fast path

: `newpage` with no argument → skip template selection, create a blank page directly. User only needs to pick destination and title.



With argument

: `newpage daily` → use daily template; `newpage meeting` → use meeting template, etc.

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
| Notebook | List all notebooks ((excluding `_archive/`(), ask which one        |
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

If user confirms, re-scan `{notes_root}/` (excluding `_archive/`) to rebuild the working context with only active notebooks.

### Rules

* Never read `_archive/` during normal operations
* Only search `_archive/` when user says "search archive"
* Archived items can be restored by moving them back to their original path

***

## `securecheck` — Security Check

Scans `{notes_root}/` (excluding `_archive/`) for sensitive information. Read files directly — you understand context, not just regex.

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
3. Search across `{notes_root}/` (skip `_archive/` and `.templates/`)
4. For each match:

   * Report the file path and line number
   * Show the matching category (NOT the actual sensitive value)
   * Example: `⚠️ notes/Work/Projects/credentials.md:12 — Possible password`
5.   Never output the actual sensitive value.   Use `[REDACTED]` if context is needed.
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



`newtemplate` — Extract template from a section:



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



Manual:

 Drop `.md` files into `{notes_root}/.templates/`. Auto-discovered by `newpage`.

***

## Import Pipeline

1:1 mapping — OneNote structure preserved as-is. Only the Recycle Bin is skipped (system folder, not user content).

### Phase 1 — Export

```
Question: "How to export your OneNote data?"
Options:
  - "Auto-export (Windows + OneNote desktop)" → runs export-onenote.ps1
  - "I already have XML files — point me to the path"
```

If auto-export:

```
Question: "Export to which directory?"
Options: "Default (./onenote_export)" | "Custom path"
```

Run: `powershell -File "<skill_dir>/tools/export-onenote.ps1" -OutputDir "<path>"`
Requires Windows + Office 2016+, COM API.

### Phase 2 — Convert

Run `<skill_dir>/tools/convert-xml2md.py` → converts XML to `{notes_root}/` preserving Notebook→Section→Page. `onenote_export/` is temporary — remind user to delete it.

***

## File Naming

Default naming rules:

| type | pattern | example |
|------|---------|---------|
| `daily` | `{date}.md` | `2026-07-29.md` |
| `meeting` | `{date}-{topic}.md` | `2026-07-29-product-review.md` |
| `quick-note` | `{date}-{title}.md` | `2026-07-29-idea.md` |
|  (default)   | `{title}.md`        | `my-note.md`                   |

> ⚠️ When editing this file, keep `SKILL-CN.md` (project root) in sync. It is the Chinese reference version for the plugin author.

