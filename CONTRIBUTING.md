# Contributing to onenote2md

## Project Structure

```
onenote2md/
├── .claude-plugin/marketplace.json       # Claude Code marketplace registry
├── plugins/onenote2md/
│   ├── .claude-plugin/plugin.json        # Plugin metadata
│   └── skills/onenote2md/
│       ├── SKILL.md                      # Agent behavior — all command logic lives here
│       ├── templates/                    # Built-in page templates
│       └── tools/
│           ├── export-onenote.ps1        # OneNote COM export (Windows)
│           └── convert-xml2md.py         # XML → Markdown converter
└── SKILL-CN.md                           # Chinese reference for the author (not loaded by agents)

> `notes/` and `.templates/` are user-space — they do not live in this repo.
```

## Guiding Principle

**Notebook → Section → Page is the foundation.** Every note lives at `{Notebook}/{Section}/{page}.md`. Do not add other directory levels or flatten the hierarchy. The agent's navigation, search, and archive logic all depend on this three-level structure. Before adding any feature, confirm it respects this constraint.

`SKILL.md` is the single source of truth. It defines every command, every interaction flow, and every convention. Agents (Copilot, Claude Code, Codex) load it and follow it.

There is no runtime, no build step, no configuration file — just a Markdown file that tells the agent what to do.

## Adding a Command

Edit `SKILL.md`:

1. Add the command to the Command Reference table.
2. Write a section with the step-by-step flow.
3. Keep `SKILL-CN.md` in sync (Chinese reference for the author, never loaded by agents).

## Adding a Template

Drop a `.md` file into `plugins/onenote2md/skills/onenote2md/templates/`.

- Templates are just Markdown with optional frontmatter and `{{VARIABLE}}` placeholders.
- If the template starts with `---` YAML frontmatter, it will be used as-is (with placeholders filled).
- If not, the agent auto-generates frontmatter with `date`, `type` (from the filename), `title`, and `tags`.

> [中文版](CONTRIBUTING.zh-CN.md)
