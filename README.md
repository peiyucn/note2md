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
/init                    # 首次设置 — 选择语言，导入 OneNote 或从头开始
/newnotebook Work        # 创建笔记本
/newsection Work 周报     # 创建分区
/newpage                 # 创建笔记 — 选择模板（日记/会议/快速笔记/空白）
/archive                 # 归档 — 笔记本、分区或单个页面
```

| 命令 | 用途 | 示例 |
|------|------|------|
| `/help` | 显示快速入门指南 | `/help` |
| `/init` | 初始化（导入或新建） | `/init` |
| `/newnotebook` | 创建笔记本 | `/newnotebook Work` |
| `/newsection` | 在笔记本中创建分区 | `/newsection Work 周报` |
| `/newpage` | 创建笔记页（模板优先，可选空白） | `/newpage` |
| `/archive` | 归档笔记本、分区或页面 | `/archive` |

> 💡 `/init` 首次设置笔记目录。如果已有笔记再运行，会提示确认后覆盖导入。

## 笔记模型（OneNote 风格）

```
notes/                        ← 你的笔记本根目录
├── {笔记本}/                  ← 笔记本
│   ├── {分区}/                ← 分区
│   │   └── {页面}.md          ← 笔记
├── _archive/                 ← 归档区（Agent 默认不看）
└── .templates/               ← 你的模板（Agent 自动学习生成）
```

> 💡 **无锁定。** 每个笔记本就是文件夹，每个页面就是 `.md` 文件。不用命令，用文件管理器也能创建、改名、移动、删除。Agent 会自动感知变化。

## 模板

插件自带 3 个通用默认模板，`/newpage` 默认从模板创建，也可选空白页：

| 模板 | 适用场景 |
|------|----------|
| 📅 日记 | 日记 / 日志 |
| 🤝 会议记录 | 会议记录 |
| 💡 快速笔记 | 快速捕获 |

### 用户模板（覆盖默认）

你自己的模板放在 `notes/.templates/` 下，**自动覆盖同名默认模板**：

| 方式 | 说明 |
|------|------|
| 🔍 导入后自动生成 | 从 OneNote 导入后，Agent 分析你的笔记结构，自动提炼模板 |
| ✍️ 手动添加 | 往 `notes/.templates/` 丢 `.md` 文件即可，Agent 自动发现 |
| 📊 持续学习 | 笔记多了说"更新我的模板"，重新分析全部笔记 |

## OneNote 导入

导入流程分两步，Agent 会通过对话引导你完成：

### ① 导出（XML）

运行 `export-onenote.ps1`，通过 OneNote COM API 将笔记本导出为 XML 文件。

```
onenote_export/               ← 临时目录，转换完可删除
├── {笔记本}/
│   ├── {分区}/
│   │   ├── {页面}.xml
│   │   └── ...
```

- 自动跳过回收站
- 支持指定导出路径（默认 `./onenote_export/`）
- 需 Windows + OneNote 桌面版

### ② 转换（XML → MD）

运行 `convert-xml2md.py`，将 XML 转为 Markdown，按原样搬进 `notes/`：

```
onenote_export/    →    notes/
  Work/                       Work/
    IT周例会/                    IT周例会/
      2026-7-23.xml              2026-7-23.md
```

> 导入是 **1:1 映射**，不会跳过或修改任何用户分区。

## 核心设计

| 特性 | 说明 |
|------|------|
| ⌨️ 统一命令 | `/init` `/newnotebook` `/newsection` `/newpage`，跨 Agent 一致 |
| 🧠 Agent-Native | 没有 GUI，Agent 就是界面 |
| 📦 零依赖 | 纯 Markdown 文件，任何编辑器都能打开 |
| 🗂️ Notebook→Section→Page | 三层结构，和 OneNote 一模一样 |
| 🧩 动态模板 | 模板从你的笔记习惯中自动学习，不预设 |
| 📥 归档机制 | 旧笔记本移到 `_archive/`，Agent 不自动加载 |
| 🔌 跨平台 | GitHub Copilot、Claude Code、Codex 都能用 |
| 🏗️ 可定制 | 加模板、改配置，甚至直接用文件夹操作 |

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
