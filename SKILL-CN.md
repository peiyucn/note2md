---
note: 本文是 plugins/onenote2md/skills/onenote2md/SKILL.md 的中文同步翻译，仅供作者对照检查。不被任何 Agent 加载。修改 SKILL.md 时必须同步更新本文。
---

# onenote2md — Agent 原生 Markdown 笔记管理

你是用户笔记系统的交互界面。所有笔记和 OneNote 一样，按 **笔记本 → 分区 → 页面** 三层组织。

```
{notes_root}/
├── {Notebook}/              # 笔记本（顶级分类）
│   ├── {Section}/           # 分区（主题区域）
│   │   ├── {page}.md        # 页面（单条笔记）
│   │   └── ...
│   └── ...
├── _archive/                # 归档 — Agent 默认不读取
└── .templates/              # 用户模板 — 覆盖插件默认
```

> `{notes_root}` 在 `/init` 中设定（默认：`./notes/`）。下文所有路径使用此变量。

---

## 命令参考

| 命令 | 功能 |
|------|------|
| `/init` | 设置向导 — 选择语言、确定根路径、导入或从头开始 |
| `/newnotebook [名称]` | 在 `{notes_root}` 下创建笔记本 |
| `/newsection [笔记本] [分区]` | 在笔记本内创建分区 |
| `/newpage` | 创建页面 — 选择模板或空白、指定位置、生成内容 |
| 归档 | 将旧笔记本移入 `_archive/` |
| `/archive` | 归档笔记本、分区或单个页面 |

---

## `/init` — 设置向导

多步骤引导流程。每个决策点使用平台原生提问界面（`askQuestions`）。

### Step 0 — 语言

```
问题: "Select your language / 选择语言："
选项: "中文" | "English"
```
选定语言后，本次会话所有提示、确认、生成内容均使用该语言。

### Step 1 — 根路径

扫描当前目录中是否有 `notes/`、`notebooks/`、`docs/` 等目录。

**找到了：**
```
问题: "发现已有目录 '{path}/'。用作笔记目录？"
选项:
  - "使用 {path}/"
  - "让我指定其他路径"
```

**没找到：**
```
问题: "笔记目录创建在哪里？"
选项:
  - "在当前目录创建 ./notes/"
  - "让我指定自定义路径"
```

记录结果为 `{notes_root}`。默认：`./notes/`。

### Step 2 — 模式

```
问题: "你想怎么开始？"
选项:
  - "从 OneNote 导入现有笔记"
  - "从头开始 — 创建第一个笔记本"
```

#### 导入路径

如果 `{notes_root}/` 已有笔记本（`_archive/` 除外），警告：
```
问题: "⚠️ {notes_root}/ 中已有笔记。导入会覆盖现有内容。继续？"
选项: "覆盖并导入" | "取消"
```
取消则停止。否则以 `{notes_root}` 为目标运行[导入流程](#导入流程)。导入完成后建议自动生成模板。

#### 从头开始

1. 询问："第一个笔记本叫什么名字？"
2. 创建：
   ```
   {notes_root}/
   ├── {Notebook}/
   ├── Quick Notes/
   ├── _archive/
   └── .templates/
   ```
3. 询问："在 {Notebook} 中创建什么分区？"
4. 创建 `{notes_root}/{Notebook}/{Section}/`
5. 确认："就绪！「{Notebook}」和「Quick Notes」已创建。用 `/newpage` 写第一篇笔记。"

### Step 3 — 更新配置

确保 `config.yaml` → `paths.notes_dir` = `{notes_root}`。

---

## `/newnotebook` — 创建笔记本

| 步骤 | 操作 |
|------|------|
| 1 | 获取名称 — 从参数（`/newnotebook Work`）或询问用户 |
| 2 | 若 `{notes_root}/{Name}/` 已存在 → 警告，换一个名字 |
| 3 | 创建 `{notes_root}/{Name}/` |
| 4 | 确认："笔记本「{Name}」已创建。用 `/newsection` 添加分区。" |

---

## `/newsection` — 创建分区

| 步骤 | 操作 |
|------|------|
| 1 | 获取笔记本 + 分区 — 从参数或询问（列出笔记本，排除 `_archive/`） |
| 2 | 创建 `{notes_root}/{Notebook}/{Section}/` |
| 3 | 确认："分区「{Section}」已在「{Notebook}」中创建。" |

---

## `/newpage` — 创建页面

模板优先；"空白页"始终作为最后一个选项。

### Step 1 — 发现模板

按优先级扫描：
1. `{notes_root}/.templates/*.md`（用户模板 — 最高优先级）
2. `<skill_dir>/templates/*.md`（插件默认 — 兜底）

插件默认：`daily.md`、`meeting.md`、`quick-note.md`。详见[模板系统](#模板系统)。

### Step 2 — 展示选项

```
问题: "选择哪个模板？"
选项:
  - "📅 日记 (daily)"
  - "🤝 会议记录 (meeting)"
  - "💡 快速笔记 (quick-note)"
  - ...用户在 .templates/ 中的任何模板...
  - "📄 空白页 — 不使用模板"
```

### Step 3 — 目标位置

询问：笔记本 → 分区 → 页面标题。允许在流程中新建笔记本/分区。

### Step 4 — Frontmatter

| 条件 | 操作 |
|------|------|
| 模板有 `---`...`---` YAML | 原样使用，替换 `{{VARIABLE}}` 占位符 |
| 模板无 frontmatter | 生成默认的 |

默认 frontmatter：
```yaml
---
date: YYYY-MM-DD
type: {文件名去掉.md}    # 如 "daily"、"meeting"；空白页用 "note"
title: {user_input}
tags: []
---
```

### Step 5 — 正文

| 选择 | 操作 |
|------|------|
| 模板 | 读取 `.md`，替换 `{{DATE}}`、`{{TITLE}}`、`{{TOPIC}}`。遇到未知 `{{KEY}}` 则询问 |
| 空白 | 无正文 — 仅 frontmatter |

### Step 6 — 文件名

按 `type` 匹配 `config.yaml` → `naming:` 规则（见[文件命名](#文件命名)）。已存在则追加 `(2)`。

### Step 7 — 确认

```
已创建：{notes_root}/{Notebook}/{Section}/{filename}.md
```

---

## `/archive` — 归档笔记本、分区或页面

触发：`/archive` 命令，或 Agent 发现 5+ 个笔记本时主动提醒。

### 第一步 — 选择范围

```
问题: "你要归档什么？"
选项:
  - "整个笔记本"
  - "某个分区"
  - "单个页面"
```

### 第二步 — 选择目标

| 范围 | 操作 |
|------|------|
| 笔记本 | 列出所有笔记本（*排除 `_archive/`*），询问哪个 |
| 分区 | 列笔记本 → 选一个 → 列其分区 → 选一个 |
| 页面 | 列笔记本 → 选分区 → 选页面 |

高亮 3 个月以上未触碰的项目。支持多选。

### 第三步 — 确认并移动

保持原始目录结构，移入 `_archive/`：

| 范围 | 移动 |
|------|------|
| 笔记本 | `{notes_root}/{Notebook}/` → `{notes_root}/_archive/{Notebook}/` |
| 分区 | `{notes_root}/{Notebook}/{Section}/` → `{notes_root}/_archive/{Notebook}/{Section}/` |
| 页面 | `{notes_root}/{Notebook}/{Section}/{page}.md` → `{notes_root}/_archive/{Notebook}/{Section}/{page}.md` |

移动后如果上级目录变空（如某笔记本下所有分区都被归档），清理空目录并询问是否删除该笔记本。

### 第四步 — 刷新上下文

归档大量内容可以节省 token 并将注意力集中在活跃笔记本上。归档完成后询问：

```
问题: "归档完毕。是否刷新上下文，聚焦精简后的活跃笔记以节省 token？"
选项:
  - "是 — 刷新上下文"（大量归档后推荐）
  - "暂不"
```

如果用户确认，重新扫描 `{notes_root}/`（排除 `_archive/`），仅加载活跃笔记本重建工作上下文。

### 规则

- 常规操作绝不读取 `_archive/`
- 仅在用户说"搜索归档"时搜索 `_archive/`
- 归档的条目可随时移回原路径恢复

---

## 模板系统

### 优先级

```
{notes_root}/.templates/{名称}.md    ← 用户版本（最高）
<skill_dir>/templates/{名称}.md      ← 插件默认（兜底）
```

### 内置默认

| 模板 | 文件 |
|------|------|
| 日记 | `daily.md` |
| 会议记录 | `meeting.md` |
| 快速笔记 | `quick-note.md` |

### 创建用户模板

**自动生成（推荐）：** 导入 OneNote 后，按 `type:` 对页面分组。对达到 N 篇的类型（`config.yaml` → `onboarding.min_samples_for_template`），提取公共结构并通过 `askQuestions` 提议。用户确认 → 写入 `{notes_root}/.templates/`。

**手动添加：** 往 `{notes_root}/.templates/` 丢 `.md` 文件。`/newpage` 自动发现。

**更新：** 用户说"更新我的模板" → 重新分析全部笔记。

---

## 导入流程

1:1 映射 — OneNote 结构原样保留。仅跳过回收站（系统目录，非用户内容）。

### 阶段 1 — 导出

```
问题: "OneNote 数据怎么导出？"
选项:
  - "自动导出（Windows + OneNote 桌面版）" → 运行 export-onenote.ps1
  - "我已有 XML 文件 — 指定路径即可"
```

自动导出时：
```
问题: "导出到哪个目录？"
选项: "默认路径（./onenote_export）" | "自定义路径"
```

运行：`powershell -File "<skill_dir>/tools/export-onenote.ps1" -OutputDir "<路径>"`
需 Windows + Office 2016+，COM API。

### 阶段 2 — 转换

运行 `<skill_dir>/tools/convert-xml2md.py` → 将 XML 转为 `{notes_root}/`，保持笔记本→分区→页面结构。`onenote_export/` 为临时目录 — 提醒用户删除。

### 阶段 3 — 分析并生成模板

扫描所有 `.md` 文件，按 `type:` 聚类，提议生成模板到 `{notes_root}/.templates/`。

---

## 文件命名

由 `config.yaml` → `naming:` 定义。默认规则：

| type | 命名规则 | 示例 |
|------|----------|------|
| `daily` | `{date}.md` | `2026-07-29.md` |
| `meeting` | `{date}-{topic}.md` | `2026-07-29-产品评审.md` |
| `quick-note` | `{date}-{title}.md` | `2026-07-29-灵感.md` |
| _(default)_ | `{title}.md` | `我的笔记.md` |

