# note2md 📓

[简体中文](README.zh-CN.md) | English | [GitHub](https://github.com/peiyucn/note2md)

> Markdown notes with Notebook→Section→Page hierarchy, managed through slash commands.

## Why

Your notes are just folders and `.md` files — open them in any editor. But an agent can also manage them: create notebooks, organize sections, write pages from templates, import from OneNote, archive old content.

## Install

**VS Code Copilot** — Add marketplace `https://github.com/peiyucn/note2md`, then install `note2md`.

**Claude Code** — `/marketplace add https://github.com/peiyucn/note2md` then `/plugin install note2md`.

**Codex CLI** — `codex plugin install https://github.com/peiyucn/note2md`.

## Commands

All agents use the same commands:

| Command | What it does |
|---------|-------------|
| `/n2m:help` | Quick-start guide |
| `/n2m:init` | Setup — pick language, choose notes directory, import OneNote or start fresh |
| `/n2m:newnotebook <name>` | Create a notebook |
| `/n2m:newsection <notebook> <section>` | Create a section inside a notebook |
| `/n2m:newpage [template]` | Create a page — no arg = blank page; `daily`/`meeting`/`quick-note` = use template |
| `/n2m:newtemplate` | Extract a template from a section of similar pages |
| `/n2m:securecheck` | Scan your notes for passwords, IDs, API keys, and other sensitive data |
| `/n2m:archive` | Move old notebooks, sections, or pages to `_archive/` |

> **Copilot Chat** — Type `/note2md` then Tab to see all 8 sub-commands (e.g. `/note2md newpage`).
> **Claude Code / Codex** — Type `/note2md-` then Tab for autocomplete.

First time? Type `/note2md help` (Copilot) or `/note2md-help` (Claude/Codex) for a quick tour.

### No lock-in

Notebook = folder. Section = subfolder. Page = `.md` file. You can create, rename, move, or delete anything through your file manager — the agent picks up changes automatically. Commands are optional convenience.

## Templates

`/n2m:newpage` always offers templates. Three built-in defaults ship with the plugin:

| Template | File |
|----------|------|
| Daily Journal | `templates/daily.md` |
| Meeting Notes | `templates/meeting.md` |
| Quick Note | `templates/quick-note.md` |

Add your own templates to `notes/.templates/` — they automatically appear in `/n2m:newpage` and override the built-in ones with the same filename.

Use `/n2m:newtemplate` to extract a template from any section with similar pages — pick a section, optionally describe what you want, and the agent builds a template skeleton from the common patterns it finds.

## OneNote Import

Use `/n2m:init` to import your existing OneNote notebooks. The agent guides you through export (Windows + OneNote desktop required) and markdown conversion. Result: `notes/` mirrors your original Notebook → Section → Page structure exactly. No content is filtered.

## License

MIT
