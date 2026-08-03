# peiyucn-skills — Agent 技能市场

简体中文 | [English](README.md) | [GitHub](https://github.com/peiyucn/peiyucn-skills)

> Agent 原生技能，可在 Copilot、Claude Code、Codex 上通用安装。本仓库是一个**市场** — 添加一次，即可安装它提供的任意插件。

## 安装市场

**VS Code Copilot** — 添加市场 `https://github.com/peiyucn/peiyucn-skills`，然后安装你需要的插件。

**Claude Code** — 先 `/marketplace add https://github.com/peiyucn/peiyucn-skills`，再 `/plugin install note2md`。

**Codex CLI** — `codex plugin install https://github.com/peiyucn/peiyucn-skills`（安装市场内的全部插件）。

## 插件

### note2md 📓

Markdown 笔记，按笔记本→分区→页面三层结构组织，通过斜杠命令管理。你的笔记就是文件夹和 `.md` 文件 — 用任何编辑器都能打开。但 Agent 也能帮你管理：创建笔记本、组织分区、从模板写页面、从 OneNote 导入、归档旧内容。

安装：`note2md` 插件。

#### 命令

所有 Agent 使用统一命令：

| 命令 | 功能 |
|------|------|
| `/note2md help` | 快速入门指南 |
| `/note2md init` | 初始化 — 选择语言、确定笔记目录、导入 OneNote 或从头开始 |
| `/note2md newnotebook <名称>` | 创建笔记本 |
| `/note2md newsection <笔记本> <分区>` | 在笔记本中创建分区 |
| `/note2md newpage [模板]` | 创建页面 — 无参数=空白页；`daily`/`meeting`/`quick-note`=使用模板 |
| `/note2md newtemplate` | 从分区中的同类页面提取模板 |
| `/note2md securecheck` | 检查笔记中的密码、身份证、API 密钥等敏感信息 |
| `/note2md archive` | 将旧的笔记本、分区或页面移入 `_archive/` |

> **Copilot Chat** — 输入 `/note2md` 然后 Tab 查看 8 个子命令（如 `/note2md newpage`）。
> **Claude Code / Codex** — 输入 `/note2md-` 然后 Tab 自动补全。

第一次用？输入 `/note2md help`（Copilot）或 `/note2md-help`（Claude/Codex）快速了解。

#### 无锁定

笔记本 = 文件夹。分区 = 子文件夹。页面 = `.md` 文件。你可以通过文件管理器创建、重命名、移动或删除任何内容 — Agent 自动感知变化。命令只是可选的便利工具。

#### 模板

`/note2md newpage` 始终提供模板选择。插件自带三个默认模板：

| 模板 | 文件 |
|------|------|
| 日记 | `templates/daily.md` |
| 会议记录 | `templates/meeting.md` |
| 快速笔记 | `templates/quick-note.md` |

将你自己的模板放到 `notes/.templates/` 下 — 它们会自动出现在 `/note2md newpage` 中，并覆盖同名的默认模板。

使用 `/note2md newtemplate` 从任意分区中提取模板 — 选择分区、可选描述需求，Agent 会从同类笔记中提炼出模板骨架。

#### OneNote 导入

使用 `/note2md init` 导入你现有的 OneNote 笔记本。Agent 会引导你完成导出（需要 Windows + OneNote 桌面版）和 Markdown 转换。结果：`notes/` 完全镜像你原始的 笔记本 → 分区 → 页面 结构。不会过滤任何内容。

## License

MIT
