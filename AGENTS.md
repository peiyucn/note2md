# 项目指令 — note2md

## 语言

* **始终用简体中文回复**

***

## Git 提交规范

* commit 描述用**中文**，类型前缀保留英文
* 可用类型：`feat` `fix` `refactor` `chore` `docs` `style` `perf` `build` `revert`
  * `feat`: 新功能
  * `fix`: 缺陷修复
  * `refactor`: 重构（不改变行为）
  * `chore`: 杂务（依赖、配置、工具链）
  * `docs`: 文档/注释
  * `style`: 格式（空格、缩进等，不影响逻辑）
  * `perf`: 性能优化
  * `build`: 构建系统或外部依赖
  * `revert`: 回滚
* 例：`feat: 新增命令自动补全`、`fix: 修复模板排序`、`docs: 补充命令交互流程文档`
* **逐项提交**：每完成一个独立任务**必须**单独 `git commit`，禁止多个任务混在一个 commit 中（方便出问题时精确回溯）

***

## 项目结构

```
plugins/note2md/
├── .prompts/                    — 命令文件（Copilot Chat 专用，*.prompt.md）
│   ├── help.prompt.md
│   ├── init.prompt.md
│   ├── newnotebook.prompt.md
│   ├── newsection.prompt.md
│   ├── newpage.prompt.md
│   ├── newtemplate.prompt.md
│   ├── securecheck.prompt.md
│   └── archive.prompt.md
├── commands/                    — 命令文件（Claude Code + Codex 共用）
│   ├── note2md-help.md
│   ├── note2md-init.md
│   ├── note2md-newnotebook.md
│   ├── note2md-newsection.md
│   ├── note2md-newpage.md
│   ├── note2md-newtemplate.md
│   ├── note2md-securecheck.md
│   └── note2md-archive.md
├── .codex/commands/             — 命令文件（Codex CLI 专用，...8 个 .md）
├── .claude-plugin/
│   └── plugin.json              — Claude Code 插件清单（skills + commands + prompts）
├── skills/note2md/
│   ├── SKILL.md                 — **单一真相来源**：所有命令的完整执行逻辑
│   ├── templates/               — 内置模板（daily / meeting / quick-note）
│   │   ├── daily.md
│   │   ├── meeting.md
│   │   └── quick-note.md
│   └── tools/
│       ├── export-onenote.ps1   — OneNote 自动导出（Windows + COM API）
│       └── convert-xml2md.py    — OneNote XML → Markdown 转换
```

### 关键文件

| 文件 | 作用 |
|------|------|
| `skills/note2md/SKILL.md` | **核心**：所有 8 个命令的完整交互流程。是唯一需要维护逻辑的地方 |
| `SKILL-CN.md` | SKILL.md 的中文同步翻译，仅供作者对照。**修改 SKILL.md 时必须同步更新** |
| `commands/*.md` / `.prompts/*.md` / `.codex/commands/*.md` | 薄壳——仅含 frontmatter（name + description + argument-hint）+ 一句委托指令 |
| `plugin.json` | Claude Code 插件清单，声明 skills / commands / prompts 路径 |
| `docs/` | 内部分析文档（不进 git），如 command-registration-analysis.md |

### 设计原则

* **薄壳原则**：`commands/`、`.prompts/`、`.codex/commands/` 三个目录下的文件内容完全一致（仅扩展名不同），都只做委托。不重复维护逻辑
* **统一 frontmatter**：三个平台的命令文件使用同一套 YAML frontmatter（`name` + `description` + `argument-hint`）。多余字段被各平台静默忽略，不报错
* **修改流程**：改逻辑 → 只改 `SKILL.md` → 同步 `SKILL-CN.md`。如果改了命令的 frontmatter 字段 → 同步更新三个目录下对应文件

***

## 规则

* **诚实原则**：不确定的事直接说"不确定"，禁止编造 URL、API 接口、文档引用或任何事实性信息
* **查证原则**：引用文件位置、函数名、调用关系时，若不确定则先 grep 确认再写，禁止凭记忆编造
* **自检原则**：代码移动/提取后**必须**搜索确认旧位置已删除，不得留有死代码或同名遮蔽
* **提交原则**：每轮对话结束时，Agent 应根据改动情况自行判断是否 `git commit` + `git push`，无需等用户发指令。判断标准：
  * ✅ 该提交 — 一轮对话完成了一个独立的功能/修复/重构（如「SKILL.md 三处改动 + SKILL-CN.md + 命令文件 + README 全部同步完」），改动原子化、可独立回溯
  * ✅ 该提交 — 用户明确说「好了」「可以了」「提交吧」
  * ❌ 先别交 — 还在讨论/探索/收集需求，方向未定
  * ❌ 先别交 — 中途打断、单轮改动不完整、留了 TODO 没处理
* **分支同步**：`push` 到 `dev` 后**必须**同步 `master`（`git push origin dev:master`）。Copilot Chat 市场安装拉的是 `master`，不同步会导致用户安装到旧版本
