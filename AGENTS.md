# 项目指令 — pyskills

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
* **提交时机**：每轮对话结束时，Agent 应根据改动情况自行判断是否 `git commit` + `git push`，无需等用户发指令。判断标准：
  * ✅ 该提交 — 一轮对话完成了一个独立的功能/修复/重构，改动原子化、可独立回溯
  * ✅ 该提交 — 用户明确说「好了」「可以了」「提交吧」
  * ❌ 先别交 — 还在讨论/探索/收集需求，方向未定
  * ❌ 先别交 — 中途打断、单轮改动不完整、留了 TODO 没处理
* **分支同步**：`push` 到 `dev` 后**必须**同步 `master`（`git push origin dev:master`）。Copilot Chat 市场安装拉的是 `master`，不同步会导致用户安装到旧版本
* **版本标签**：每个里程碑（如首个可用版本、大功能批次完成）**必须**打 tag。同步 `plugin.json` 中的 `version` 字段（市场 `marketplace.json` 无 version 字段），然后：
  ```bash
  git tag -a v{version} -m "v{version}: {简要说明}"
  git push origin v{version}
  ```

***

## GitHub 操作（gh cli）

* 本机已安装并登录 **gh cli**（账号 `peiyucn`，https 协议，凭据存 keyring），Agent 可直接使用 `gh` 命令操作 GitHub，无需等用户手动操作
* 本仓库远程：`https://github.com/peiyucn/pyskills.git`（原名 note2md，已改名）
* 常用操作：
  * 仓库改名：`gh repo rename <新名> --repo peiyucn/pyskills --yes`
  * 查看仓库信息：`gh repo view peiyucn/pyskills`
  * 创建仓库：`gh repo create <名称> --public --source . --remote origin --push`
* 改名后需同步更新本地 remote：`git remote set-url origin https://github.com/peiyucn/<新名>.git`

***

## 项目结构

仓库根即**市场（marketplace）**，插件放在 `plugins/` 下：

```
pyskills/                          — 仓库根 = 市场
├── .claude-plugin/
│   └── marketplace.json           — 市场货架清单（name: pyskills；三平台均识别此路径）
├── docs/
│   └── agent-compatibility.md     — 三平台兼容性分析与决策记录（为什么用 .claude-plugin 统一兼容）
├── plugins/note2md/               — 市场下的插件（插件名保持 note2md，命令命名空间 /note2md:xxx）
│   ├── commands/                  — 命令文件（8 个 .md，三平台通用：Claude Code / Codex / Copilot 均自动发现，命名空间 /note2md:xxx）
│   ├── .claude-plugin/
│   │   └── plugin.json            — 插件清单（声明 commands；skills 目录自动发现）
│   └── skills/note2md/
│       ├── SKILL.md               — **单一真相来源**：所有命令的完整执行逻辑
│       ├── templates/             — 内置模板（daily / meeting / quick-note）
│       │   ├── daily.md
│       │   ├── meeting.md
│       │   └── quick-note.md
│       └── tools/
│           ├── export-onenote.ps1 — OneNote 自动导出（Windows + COM API）
│           └── convert-xml2md.py  — OneNote XML → Markdown 转换
```

### 关键文件

| 文件 | 作用 |
|------|------|
| `.claude-plugin/marketplace.json` | 市场货架清单。`name` 即市场名（pyskills），插件条目声明 `source: ./plugins/note2md`；多余字段被各平台静默忽略 |
| `docs/agent-compatibility.md` | 三平台兼容性分析与决策记录（市场/插件安装/命令注册机制） |
| `plugins/note2md/skills/note2md/SKILL.md` | **核心**：所有 8 个命令的完整交互流程。是唯一需要维护逻辑的地方 |
| `SKILL-CN.md` | SKILL.md 的中文同步翻译，仅供作者对照。**修改 SKILL.md 时必须同步更新** |
| `plugins/note2md/commands/*.md` | 薄壳——仅含 frontmatter（name + description + argument-hint）+ 一句委托指令 |
| `plugins/note2md/.claude-plugin/plugin.json` | 插件清单，声明 commands 路径；skills 目录自动发现 |

### 设计原则

* **薄壳原则**：`commands/` 只做委托，不重复维护逻辑
* **统一 frontmatter**：命令文件使用同一套 YAML frontmatter（`name` + `description` + `argument-hint`）。多余字段被各平台静默忽略，不报错
* **修改流程**：改逻辑 → 只改 `SKILL.md` → 同步 `SKILL-CN.md`。如果改了命令的 frontmatter 字段 → 同步更新 commands 下对应文件

***

## 规则

* **诚实原则**：不确定的事直接说"不确定"，禁止编造 URL、API 接口、文档引用或任何事实性信息
* **查证原则**：引用文件位置、函数名、调用关系时，若不确定则先 grep 确认再写，禁止凭记忆编造
* **自检原则**：代码移动/提取后**必须**搜索确认旧位置已删除，不得留有死代码或同名遮蔽
