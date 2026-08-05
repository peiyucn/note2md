# Agent Plugins Updater

把 VS Code 里藏得很深的 **「Update Plugins」** 命令放到 **Agent Plugins 视图** 上，一键更新 agent 插件（如 note2md），无需删了重装。

> 背景：VS Code 的 agent 插件更新命令 `workbench.agentPlugins.checkForUpdates` 只注册在命令面板（Ctrl+Shift+P → "Update Plugins"），没有可见按钮。本扩展只是一个**纯配置薄壳**，把该命令挂到「Agent Plugins - Installed」视图上。

## 功能

- **视图标题栏按钮**：打开「Agent Plugins - Installed」视图（扩展视图侧边栏 → `@agentPlugins` 搜索结果里的已安装插件视图），标题栏右侧出现「Update Agent Plugins」按钮，点击即更新所有 agent 插件（内部执行 `git pull`）
- **右键菜单**：在已安装插件条目上右键 → 「Update Agent Plugins (Force)」，强制更新（含 npm/pip 包重装）
- **命令面板**：新增 `Agent Plugins: Update Agent Plugins` / `Agent Plugins: Update Agent Plugins (Force)` 两个别名

## 安装（二选一）

**方式 A：VSIX 安装（推荐）**

```bash
# 在扩展目录下打包
cd extensions/agent-plugins-updater
npx @vscode/vsce package
# 生成 agent-plugins-updater-0.1.0.vsix
```

VS Code → 扩展视图（Ctrl+Shift+X）→ 右上角 `...` → **Install from VSIX...** → 选择生成的 `.vsix`

**方式 B：直接加载源码**

VS Code → 命令面板（Ctrl+Shift+P）→ `Developer: Install Extension from Location...` → 选择 `extensions/agent-plugins-updater/` 目录

## 更新机制说明

- 装好本扩展后，**正常更新走自动**：VS Code 约每 24 小时自动检查 agent 插件市场仓库是否有新提交并 `git pull`（前提：设置 `extensions.autoUpdate` 未关闭）
- 想**立即**更新 → 点视图标题栏的按钮，或命令面板 `Update Agent Plugins`
- 更新后插件命令/skills 即时生效（VS Code 监听文件变化），通常无需重启

## 本扩展无状态

不读取、不修改任何 agent 插件数据，仅调用 VS Code 内置命令。卸载无副作用。

## License

MIT
