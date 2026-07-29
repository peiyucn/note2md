# onenote2md �

> OneNote-style Markdown notes, managed through slash commands.

## Why

Your notes are just folders and `.md` files — open them in any editor. But an agent can also manage them: create notebooks, organize sections, write pages from templates, import from OneNote, archive old content.

## Install

**VS Code Copilot** — Add marketplace `https://github.com/peiyucn/onenote2md`, then install `onenote2md`.

**Claude Code** — `/marketplace add https://github.com/peiyucn/onenote2md` then `/plugin install onenote2md`.

## Commands

All agents use the same commands:

| Command | What it does |
|---------|-------------|
| `/help` | Quick-start guide |
| `/init` | Setup — pick language, choose notes directory, import OneNote or start fresh |
| `/newnotebook <name>` | Create a notebook |
| `/newsection <notebook> <section>` | Create a section inside a notebook |
| `/newpage` | Create a page — pick a template (daily, meeting, quick-note, or blank) |
| `/newtemplate` | Extract a template from a section of similar pages |
| `/securecheck` | Scan your notes for passwords, IDs, API keys, and other sensitive data |
| `/archive` | Move old notebooks, sections, or pages to `_archive/` |

First time? Type `/help` in any chat for a quick tour.

### No lock-in

Notebook = folder. Section = subfolder. Page = `.md` file. You can create, rename, move, or delete anything through your file manager — the agent picks up changes automatically. Commands are optional convenience.

## Templates

`/newpage` always offers templates. Three built-in defaults ship with the plugin:

| Template | File |
|----------|------|
| Daily Journal | `templates/daily.md` |
| Meeting Notes | `templates/meeting.md` |
| Quick Note | `templates/quick-note.md` |

Add your own templates to `notes/.templates/` — they automatically appear in `/newpage` and override the built-in ones with the same filename.

Use `/newtemplate` to extract a template from any section with similar pages — pick a section, optionally describe what you want, and the agent builds a template skeleton from the common patterns it finds.

## OneNote Import

Use `/init` to import your existing OneNote notebooks. The agent guides you through export (Windows + OneNote desktop required) and markdown conversion. Result: `notes/` mirrors your original Notebook → Section → Page structure exactly. No content is filtered.

## License

MIT

> [中文版](README.zh-CN.md)
