# onenote2md 🚀

> Agent Plugin：把 Markdown 文件夹变成 OneNote 风格的智能笔记本

## 这是什么？

一个 **Agent-Native 笔记管理插件**，在 Copilot、Claude Code、Codex 中用**统一的斜杠命令**管理 OneNote 风格笔记：

- `/init` — 首次设置（导入 OneNote 或创建第一个笔记本）
- `/newnotebook` `/newsection` `/newpage` — 创建笔记本、分区、笔记页（模板优先）
- 📦 归档旧笔记，避免上下文爆炸

## 安装

### VS Code Copilot

1. 添加市场：`https://github.com/peiyucn/onenote2md`
2. 在市场中选择 `onenote2md` 安装

### Claude Code

```
/marketplace add https://github.com/peiyucn/onenote2md
```
```
/plugin install onenote2md
```

## 使用

所有命令在 VS Code Copilot 和 Claude Code 中完全一致：

```bash
/init                       # First-time setup — pick language, import or start fresh
/newnotebook Work           # Create a notebook
/newsection Work Weekly     # Create a section
/newpage                    # Create a page — pick a template (daily/meeting/quick-note/blank)
/archive                    # Archive — notebooks, sections, or pages
```

| 命令 | 用途 | 示例 |
|------|------|------|
| `/help` | 显示快速入门指南 | `/help` |
| `/init` | 初始化（导入或新建） | `/init` |
| `/newnotebook` | 创建笔记本 | `/newnotebook Work` |
| `/newsection` | 在笔记本中创建分区 | `/newsection Work Weekly` |
| `/newpage` | 创建笔记页（模板优先，可选空白） | `/newpage` |
| `/archive` | 归档笔记本、分区或页面 | `/archive` |

> 💡 `/init` 首次设置笔记目录。如果已有笔记再运行，会提示确认后覆盖导入。

## 笔记模型（OneNote 风格）

```
notes/                        ← Your notes root directory
├── {Notebook}/               ← Notebook (folder)
│   ├── {Section}/            ← Section (subfolder)
│   │   ├── {page}.md         ← Page (Markdown file)
│   │   └── ...
│   └── ...
├── _archive/                 ← Archive (Agent ignores by default)
└── .templates/               ← Your templates (auto-discovered by /newpage)
```

> 💡 **No lock-in.** Every notebook is a folder, every page is a `.md` file. Create, rename, move, or delete through your file manager — the agent picks up changes automatically.

## 模板

插件自带 3 个通用默认模板，`/newpage` 默认从模板创建，也可选空白页：

| 模板 | 文件 | 适用场景 |
|------|------|----------|
| 📅 Daily Journal | `daily.md` | 日记 / 日志 |
| 🤝 Meeting Notes | `meeting.md` | 会议记录 |
| 💡 Quick Note | `quick-note.md` | 快速捕获 |

### 用户模板（覆盖默认）

你自己的模板放在 `notes/.templates/` 下，**自动覆盖同名默认模板**：

| 方式 | 说明 |
|------|------|
| `/newtemplate` | 选一个分区，Agent 分析其中同类笔记的结构，自动提炼模板 |
| ✍️ 手动添加 | 往 `notes/.templates/` 丢 `.md` 文件即可，Agent 自动发现 |

## OneNote 导入

导入流程分两步，Agent 会通过对话引导你完成：

### ① 导出（XML）

运行 `export-onenote.ps1`，通过 OneNote COM API 将笔记本导出为 XML 文件。

```
onenote_export/               ← Temporary directory — delete after conversion
├── {Notebook}/
│   ├── {Section}/
│   │   ├── {page}.xml
│   │   └── ...
```

- 自动跳过回收站
- 支持指定导出路径（默认 `./onenote_export/`）
- 需 Windows + OneNote 桌面版

### ② 转换（XML → MD）

运行 `convert-xml2md.py`，将 XML 转为 Markdown，按原样搬进 `notes/`：

```
onenote_export/          →    notes/
  Diary/                           Diary/
    Daily/                           Daily/
      2026-07-29.xml                  2026-07-29.md
```

> 导入是 **1:1 映射**，不会跳过或修改任何用户分区。

## 核心设计

| 特性 | 说明 |
|------|------|
| ⌨️ 统一命令 | `/help` `/init` `/newnotebook` `/newsection` `/newpage` `/newtemplate` `/securecheck` `/archive` |
| 🧠 Agent-Native | 没有 GUI，Agent 就是界面 |
| 📦 零依赖 | 纯 Markdown 文件，任何编辑器都能打开 |
| 🗂️ Notebook→Section→Page | 三层结构，和 OneNote 一模一样 |
| 🧩 动态模板 | 3 个默认模板 + `/newtemplate` 从分区提炼自定义模板 |
| 📥 归档机制 | 旧笔记本移到 `_archive/`，Agent 不自动加载 |
| 🔌 跨平台 | GitHub Copilot、Claude Code、Codex 都能用 |
| 🏗️ 无锁定 | 文件夹和 .md 文件，文件管理器也能操作 |

## 项目结构

```
onenote2md/
├── plugins/onenote2md/
│   └── skills/onenote2md/
│       ├── SKILL.md             ← Agent 行为指南（含命令定义）
│       ├── templates/           ← 默认模板
│       └── tools/               ← OneNote 迁移脚本
├── SKILL-CN.md                  ← 中文参考（作者对照用，不被 Agent 加载）
└── README.md
```

> `notes/`、`templates/` 都属于用户空间，不在插件项目中。

## License

MIT
