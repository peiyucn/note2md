# 参与贡献 note2md

简体中文 | [English](CONTRIBUTING.md) | [GitHub](https://github.com/peiyucn/note2md)

## 分支策略

- `master` — 稳定，可发布。禁止直接提交。
- `dev` — 活跃开发。所有工作从 `dev` 拉分支，合并回 `dev`。
- 功能分支 — `feature/<名称>` 从 `dev` 拉出，通过 PR 合并。

工作流：`dev` → 功能分支 → PR → `dev` →（就绪后）→ `master`。

## 核心原则

**笔记本 → 分区 → 页面 三层结构不可动摇。** 每条笔记位于 `{Notebook}/{Section}/{page}.md`。不得增加其他目录层级或扁平化结构。Agent 的导航、搜索和归档逻辑全部依赖此三层结构。添加任何功能前，先确认是否遵守此约束。

## 项目结构

```
note2md/
├── .claude-plugin/marketplace.json       # Claude Code 市场注册
├── plugins/note2md/
│   ├── .claude-plugin/plugin.json        # 插件元信息
│   └── skills/note2md/
│       ├── SKILL.md                      # Agent 行为 — 所有命令逻辑在此
│       ├── templates/                    # 内置页面模板
│       └── tools/
│           ├── export-onenote.ps1        # OneNote COM 导出（Windows）
│           └── convert-xml2md.py         # XML → Markdown 转换器
└── SKILL-CN.md                           # 作者中文参考（不被 Agent 加载）

> `notes/` 和 `.templates/` 属于用户空间 — 不在此仓库中。
```

## 工作原理

`SKILL.md` 是唯一真相来源。它定义了每个命令、每个交互流程、每个约定。Agent（Copilot、Claude Code、Codex）加载并遵循它。

没有运行时、没有构建步骤、没有配置文件 — 就是一个告诉 Agent 该怎么做的 Markdown 文件。

## 添加命令

编辑 `SKILL.md`：

1. 在 Command Reference 表格中添加命令。
2. 按步骤编写执行流程。
3. 同步更新 `SKILL-CN.md`（作者中文参考，不被 Agent 加载）。

## 添加模板

往 `plugins/note2md/skills/note2md/templates/` 中放入 `.md` 文件。

- 模板就是 Markdown，可带 frontmatter，支持 `{{VARIABLE}}` 占位符。
- 如果模板以 `---` YAML frontmatter 开头，将原样使用（占位符会被填充）。
- 如果没有，Agent 自动生成默认 frontmatter：`date`、`type`（取文件名）、`title`、`tags`。
