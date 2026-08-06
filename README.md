# peiyucn-skills — Agent Skills Marketplace

[简体中文](README.zh-CN.md) | English | [GitHub](https://github.com/peiyucn/peiyucn-skills)

> Agent-native skills, installable across Copilot, Claude Code, and Codex. This repo is a **marketplace** — add it once, then install any plugin it ships.

## Install the Marketplace

**VS Code Copilot** — Add marketplace `https://github.com/peiyucn/peiyucn-skills`, then install the plugins you want.

**Claude Code** — `/marketplace add https://github.com/peiyucn/peiyucn-skills` then `/plugin install note2md`.

**Codex CLI** — `codex plugin install https://github.com/peiyucn/peiyucn-skills` (installs all plugins in the marketplace).

## Plugins

### note2md 📓

Markdown notes with Notebook→Section→Page hierarchy, managed through slash commands. Your notes are just folders and `.md` files — open them in any editor. But an agent can also manage them: create notebooks, organize sections, write pages from templates, import from OneNote, archive old content.

Install: `note2md` plugin.

#### Commands

All agents use the same commands:

| Command | What it does |
|---------|-------------|
| `/note2md help` | Quick-start guide |
| `/note2md init` | Setup — pick language, choose notes directory, import OneNote or start fresh |
| `/note2md newnotebook <name>` | Create a notebook |
| `/note2md newsection <notebook> <section>` | Create a section inside a notebook |
| `/note2md newpage [template]` | Create a page — no arg = blank page; `daily`/`meeting`/`quick-note` = use template |
| `/note2md newtemplate` | Extract a template from a section of similar pages |
| `/note2md securecheck` | Scan your notes for passwords, IDs, API keys, and other sensitive data |
| `/note2md archive` | Move old notebooks, sections, or pages to `_archive/` |

> **Copilot Chat** — Type `/note2md` then Tab to see all 8 sub-commands (e.g. `/note2md newpage`).
> **Claude Code / Codex** — Type `/note2md-` then Tab for autocomplete.

First time? Type `/note2md help` (Copilot) or `/note2md-help` (Claude/Codex) for a quick tour.

#### No lock-in

Notebook = folder. Section = subfolder. Page = `.md` file. You can create, rename, move, or delete anything through your file manager — the agent picks up changes automatically. Commands are optional convenience.

#### Templates

`/note2md newpage` always offers templates. Three built-in defaults ship with the plugin:

| Template | File |
|----------|------|
| Daily Journal | `templates/daily.md` |
| Meeting Notes | `templates/meeting.md` |
| Quick Note | `templates/quick-note.md` |

Add your own templates to `notes/.templates/` — they automatically appear in `/note2md newpage` and override the built-in ones with the same filename.

Use `/note2md newtemplate` to extract a template from any section with similar pages — pick a section, optionally describe what you want, and the agent builds a template skeleton from the common patterns it finds.

#### OneNote Import

Use `/note2md init` to import your existing OneNote notebooks. **No Python or other runtime required** — the agent converts the XML to Markdown natively, with a mandatory verification pass (count check + spot check).

- **Windows + OneNote desktop:** an optional PowerShell script auto-exports your notebooks.
- **macOS / Linux (or no OneNote desktop):** auto-export is not available (the COM API is Windows-only) — you must export your notebooks to XML yourself (e.g. on a Windows machine with OneNote desktop) and point `init` at that folder.

Result: `notes/` mirrors your original Notebook → Section → Page structure, with text, tables, lists, headings, and to-dos converted to Markdown.

All import artifacts (auto-exported XML, pretty-printed copies) land in a temporary `_import/` staging directory **inside** your notes root and are deleted after the import. If you export OneNote to XML yourself, put the files under `{notes_root}/_import/` before running `init`, and the agent picks them up from there.

> **Known limitations:** images, file attachments, hyperlinks, ink/drawings, math, audio, and video are **not** extracted yet (see [docs/onenote-loss-matrix.md](docs/onenote-loss-matrix.md) for the full breakdown and roadmap). Only text-based content is guaranteed.

## License

MIT
