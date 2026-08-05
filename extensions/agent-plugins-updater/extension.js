// Agent Plugins Updater — thin wrapper that exposes VS Code's built-in
// agent-plugin update commands on the "Agent Plugins - Installed" view.
//
// The underlying commands are provided by VS Code itself:
//   - workbench.agentPlugins.checkForUpdates   (git pull on marketplace repos)
//   - workbench.agentPlugins.forceUpdate       (also re-installs npm/pip pkgs)
// This extension only adds visible UI (view title button + context menu item)
// and command-palette aliases — no plugin logic lives here.

'use strict';

const vscode = require('vscode');

const BUILTIN_UPDATE = 'workbench.agentPlugins.checkForUpdates';
const BUILTIN_FORCE_UPDATE = 'workbench.agentPlugins.forceUpdate';

/** @param {vscode.ExtensionContext} context */
function activate(context) {
	context.subscriptions.push(
		vscode.commands.registerCommand('agentPluginsUpdater.updateAll', async () => {
			await vscode.commands.executeCommand(BUILTIN_UPDATE);
		}),
		vscode.commands.registerCommand('agentPluginsUpdater.forceUpdateAll', async () => {
			await vscode.commands.executeCommand(BUILTIN_FORCE_UPDATE);
		})
	);
}

function deactivate() { }

module.exports = { activate, deactivate };
