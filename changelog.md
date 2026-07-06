---
title: Changelog
description: Termark release notes and product updates.
---

# Changelog

This page records Termark product updates, bug fixes, and behavior changes.

## v1.0.47 (2026-07-07)

### Added

- Added a shortcut for toggling the sidebar.
- Workspace sidebar collapsed state is now remembered.

### Fixed

- Fixed stale state remaining after canceling an AI command.
- Fixed terminal font name parsing errors.
- Fixed Chinese IME compatibility for `@` mentions in the AI input box.

### Changed

- Refactored lock-screen startup theme initialization.
- Terminal command snippet groups are now collapsed by default.

## v1.0.46 (2026-07-03)

### Added

- Added a quick-connect shortcut for hosts.
- Quick Connect now supports NextTerminal SSH assets.
- AI can now read command snippets on demand.

### Fixed

- Fixed lock screen background transparency.
- Fixed host ordering changing after editing a host.

### Changed

- Improved background image transparency and terminal split-pane spacing.
- Improved debounce behavior for terminal size synchronization.
- Improved newly added data IDs and the AI context format.

## v1.0.45 (2026-07-02)

### Added

- Added an Authorization Center entry to the account menu in Settings.
- Added the OpenAI-Response provider type.

### Fixed

- Preloaded terminal fonts to avoid abnormal spacing on first open.
- Fixed an issue with copying IP addresses from the terminal menu.
- Fixed line wrapping in the cloud sync interval description.
- Fixed the opaque background on the global AI page.

### Changed

- Adjusted the terminal menu.
- Removed the feature for opening a new terminal by reusing an SSH connection.
- Improved collapsed-state detection for the top sidebar menu.
- Limited AI command output length while preserving the beginning and end.
- Improved theme background following and interactive state colors.
- Improved asset tree interaction states and follow-mode details.
- Improved interaction details in the top bar and terminal sidebar.
- Improved theme following and interaction hierarchy on the settings page.
- Improved terminal icon display in the tab bar.
- Improved the default theme colors.

## v1.0.43 (2026-06-29)

### Added

- Global AI `@` mentions can now show all machines.
- Global AI `@` mentions now support selecting machines by group.

### Fixed

- Fixed the sync password verification and modification flow.
- Fixed overlap in the bottom action area of the AI input box.

### Changed

- Global AI `@` mentions can now only select machines with AI capabilities enabled.
- Switched to the new download update URL.
- Removed the terminal WebGL renderer.

## v1.0.42 (2026-06-28)

### Fixed

- Fixed terminal blank screens caused by frequent WebGL context destruction and recreation.

## v1.0.41 (2026-06-28)

### Added

- Added the global AI assistant.
- Added host-level AI command execution policy configuration.
- Added support for opening the containing folder after a file download completes.
- Added support for pruning unused Docker images.
- Added support for NextTerminal asset terminal watermarks.

### Fixed

- Fixed recursive default value handling for the Windows local terminal `pwsh`.
- Fixed tmux window and cursor misalignment caused by terminal resize updates being lost while in use.

### Changed

- Improved the window behavior when using the close-tab shortcut again in an empty window by minimizing the window.
- Simplified Windows shell detection.
- Improved the AI command execution policy.
- Enhanced NextTerminal WebSocket proxy error details.

## v1.0.40 (2026-06-25)

### Added

- Added a test connection feature to the local host modal.

### Fixed

- Fixed window close behavior in macOS fullscreen mode.
- Fixed lag on the terminal settings page on Windows.
- Fixed the error reported when no socket is found during the first tmux detection.

### Changed

- Refactored the implementation and unified segmented selector styles across multiple places.

## v1.0.39 (2026-06-25)

### Added

- Added terminal tmux management.
- Local terminals now support PowerShell 7 and WSL.
- Added SSH capability configuration.

### Fixed

- Fixed abnormal remote file permissions after sync.
- Fixed inconsistent file verification after pausing and resuming transfers.
- Fixed local terminal path detection on Windows.
- Fixed tmux display issues caused by terminal size synchronization.
- Fixed the context menu stealing focus after right-click paste in the terminal.

### Changed

- Adjusted Docker resource action button states.
- Split main page background configuration for light and dark modes.
- Added a common icon button and improved terminal sidebar hints.
- Improved local terminal path settings.
- Improved sync status check time display.
- Improved AI tool call content display.
- Improved terminal settings font selector rendering.

## v1.0.38 (2026-06-22)

### Added

- Added support for hiding terminal tools in restricted SSH environments.
- Added support for AI command execution in restricted shells.

### Fixed

- Fixed Shift+Enter newline input in the terminal.
- Fixed terminal focus loss after paste or copy operations on Windows.

### Changed

- Refactored terminal theme management and simplified theme background-following behavior.
- Removed resumed byte display from the transfer list.
- Unified SFTP toolbar download capabilities and simplified the download button.
- Unified single-input dialog styles.
- Improved the SFTP permissions modal layout.
- Hid the Docker image acceleration button.
- Improved remote Docker command compatibility.

## v1.0.37 (2026-06-19)

### Added

- Added a remote Docker management panel.
- Tabs can now be renamed.
- Added a setting for copy success feedback.
- Host environment variables now support quick tag insertion.
- SFTP workspaces now support directory sync and accelerated downloads.
- Port forwarding rules can now start automatically on launch.
- Added FTP and SFTP sync configuration.
- Cloud sync now supports configurable automatic sync intervals.
- Keyword highlight rules no longer have a quantity limit.

### Changed

- Removed default encoding environment variable injection for SSH sessions.
- Removed the sync button from the tab bar.
- Unified switch styles on the settings page.
- Split advanced settings in the local host modal.
- Terminal theme sync now only synchronizes the background color.
- Adjusted the minimum window size to support half-screen layouts.
- Optimized directory sync to skip unchanged files.
- Removed the accelerated upload recommendation for folders.
- Removed the SFTP entry from the sidebar and added support for opening multiple SFTP panels.

## v1.0.35

### Added

- Added support for accessing bastion host RDP assets.
- Added a cloud sync restore button to the tab bar and displayed sync status.
- Added support for detecting SFTP symlink directories and adjusted the symlink icon.
- Added support for pausing SFTP transfers and reusing the same record when resuming.

### Fixed

- Fixed invalid filenames when downloading files over SFTP on Windows.
- Fixed the local asset host port input not being clearable.
- Fixed file upload and download progress not being displayed in SFTP.
- Fixed the NextTerminal list API returning `null` for empty data.
- Fixed SFTP transfer progress not refreshing after the app was locked.

### Changed

- Improved the bastion host connection copy.
- Refactored the SFTP transfer list and unified the pause/resume interaction.
- Optimized terminal password prompt recognition logic.
- Adjusted error display logic during the terminal pre-connection state.

## v1.0.34

### Added

- Added account badge information.

### Fixed

- Fixed the top window area not being draggable after opening a tab.
- Fixed abnormal input box styling when the AI history modal contains many conversations.
- Fixed AI history conversation continuation context issues.
- Fixed occasional terminal focus loss after pasting from the context menu.

### Changed

- Relaxed terminal password prompt recognition rules.
- Improved the Windows maximize and restore icons, and adjusted the button hover background color.

## v1.0.33

### Added

- Terminal login credentials can now be auto-filled.

### Fixed

- Added compatibility with Xiaomi LLM APIs and fixed the AI assistant error `Unexpected end of JSON input`.
- Fixed the terminal losing focus after pasting from the context menu.

### Changed

- Adjusted the default official AI model and context window.

## v1.0.32

### Added

- Added the official AI channel.
- Added detailed AI logs.
- Import preview tables now support field sorting.
- Local assets now support multi-select drag-and-drop moves.

### Fixed

- Fixed garbled Chinese text when importing from MobaXterm.
- Fixed the app lock clearing the sidebar cache.
- Fixed too many tabs affecting sidebar drag-and-drop.
- Fixed AI output tables where the scrollbar could not be clicked and dragged.
- Fixed SSH environment variable settings getting stuck.

### Changed

- Unified the batch execution command bar and added a Ctrl+C button.
- Optimized the logo.
- Adapted the free account status display.

## v1.0.31

### Added

- Added support for SFTP resume and retry operations.
- Added support for selecting existing credentials during terminal pre-connection.

### Fixed

- Fixed scrolling issues in the NextTerminal configuration modal and pinned the footer action buttons.
- Fixed Termius data import issues and removed Tabby data import.

### Changed

- Port forwarding rules are now returned in descending order by creation time.
- Instance files now sync according to the external CLI switch.
- Merged the local client asset import path selection entry points.
- Unified icon button component styling.
- Terminal connections now stay connected while the app is locked.

## v1.0.30

### Added

- Built-in AI now supports HTTP proxy configuration.
- Added local client asset import, with support for importing assets from Tabby, Termius, MobaXterm, and Xshell.
- CSV imports can now bind to existing credentials.
- Added terminal OSC 52 remote copy support.
- Added an SFTP entry to the asset tree context menu.
- CLI now supports searching NextTerminal assets by ID.

### Fixed

- Fixed the macOS fullscreen button issue and removed fullscreen state persistence.
- Fixed the AI input box stealing focus when a terminal reconnects.
- Fixed the AI panel automatically focusing the input box when activated.
- Fixed shortcut configuration loading during startup.
- Fixed AI context usage display.
- Fixed the AI input box height.
- Fixed terminal content being lost after splitting panes.
- Fixed modal close button clicks not working.

### Changed

- Close-tab confirmation is now enabled by default, and the port forwarding entry and close-tab prompt were adjusted.
- Adjusted the default close-tab shortcut on Windows.
- Moved help documentation and report bug entries to version settings.
- Adjusted the AI model switch position, AI execution mode switch styling, and segmented icon switch styling.
- Split the credential creation button and added reference checks when deleting credentials.
- Frontend base64 encoding and decoding now consistently use `js-base64`.
- Refactored the terminal session lifecycle and serial port close logic, and terminal session creation now fills the host ID.
- Fixed the header and footer layout in modals.
- Improved the local client asset import flow and compatibility.

## v1.0.29

### Added

- Added the CLI directory sync command and support for searching the asset list by ID.
- Added quick local private key import.
- SSH asset import previews now support editing and credential binding, and jump hosts can be selected with the asset selector.
- SSH session cloning now reuses the logged-in connection.
- Interactive authentication and manually entered username/password connections can now save connection information.
- Added host-level SFTP directory-follow policy.
- Added quick SFTP deletion.
- Changing the local encryption key is now supported and takes effect after restart.
- AI command execution mode can now be switched per host or temporarily, and AI commands now support background execution.
- Added support for DeepSeek and Qwen reasoning modes.
- Added a help documentation link on the settings page.

### Fixed

- Fixed focus being lost after entering an incorrect app lock password.
- Fixed split terminals still showing a blue border after losing focus.
- Fixed the terminal automatic reconnect attempt limit not taking effect.
- Fixed terminal shortcuts not working on the batch execution page.
- Fixed custom shortcuts not taking effect after restart.
- Fixed abnormal scrollbars in empty SFTP lists.

### Changed

- Improved terminal pane shortcuts and batch execution menu states.
- Refactored `exec` command argument passing.
- Online editing is now a free feature.
- Adjusted the credential modal width, made credential usernames optional, and disallowed duplicate credential names when adding or editing credentials.
- Refactored the SSH asset import preview flow and adjusted the import button position.
- Adjusted the default dropdown menu placement.
- Window fullscreen and maximized states are now remembered.
- Optimized CLI transfer progress display with a progress bar library and improved transfer progress synchronization.
- Refactored the terminal sidebar lifecycle and simplified the local asset host edit modal.
- Improved terminal Chinese font fallback.
- Improved AI panel command execution result display and refactored built-in AI reasoning protocol configuration.
- Unified SFTP configuration styling in host advanced settings and removed the SFTP sudo privilege escalation mode parameter.
- Refactored the SFTP panel to reuse list query state and simplified SFTP mounting logic in the terminal sidebar.
- Unified icons.

## v1.0.28

### Added

- Added copy buttons to AI conversation messages.
- Port forwarding asset selection now uses the asset tree and supports NextTerminal assets.
- SSH sessions now support drag-and-drop file uploads through `rz`.
- Port forwarding now supports HTTP and SOCKS5 proxies.
- Added feedback for modal close buttons.

### Fixed

- Fixed the SFTP upload speed regression caused by cancellation support.
- Fixed AI output text copying being intercepted by shortcuts.
- Fixed garbled Chinese filenames during `rz` uploads.
- Fixed Windows CLI installation to PATH.

### Changed

- Adjusted the default sidebar width.
- Adjusted the default and minimum window sizes.
- Updated to the new logo.

## v1.0.27

### Added

- SSH key upload now supports passphrases and `.ppk` keys.
- Added accelerated SFTP uploads.

### Fixed

- Fixed SFTP uploads and downloads not being cancellable.
- Fixed directory-follow configuration detection failures in fish.
- Fixed missing icons in Linux packages.

### Changed

- Removed terminal keyword highlight rule IDs.
- Changed keyboard shortcuts to use independent event dispatch.
- Unified portable-version local data key logic.
- Removed the split-pane button from the tab context menu.
- Changed the default terminal scrollback to 1000 lines.
- Adjusted tab context menu actions.

## v1.0.26

### Fixed

- Fixed AI getting stuck on multiline commands.

### Changed

- Adjusted the priority rules for overlapping keyword highlights.
- Adjusted split-pane title bar transparency.
- Improved AI tool calls and display.
- Optimized SFTP file upload speed, improving it by 10x.
- Refactored keyboard shortcuts.

## v1.0.25

### Fixed

- Fixed local encrypted credential reads for sync configuration.
- Fixed terminal display corruption.

### Changed

- Improved terminal selection copy behavior.
- Adjusted the split-pane layout on the batch execution page.

## v1.0.24

### Added

- Credential mode now supports overriding the username.

### Fixed

- Fixed password retry failures in quick connections.
- Fixed incorrect YAML indentation when pasting into Vim.
- Fixed terminal display corruption when switching split panes.

### Changed

- Frontend data now refreshes after a successful sync.
- Improved asset selection and command dispatch for split terminals.
- Optimized and refactored the settings page.
- Reused SSH configuration construction logic.
- Configuration changes now sync through backend events.

## v1.0.23

### Fixed

- Fixed forms being reset too frequently.

### Changed

- Improved cloud sync logic.

## v1.0.22

### Added

- Added a main page background toggle and consolidated transparent background behavior.
- Portable mode now supports manually configuring the encryption password.

### Changed

- Keyword highlighting in terminals now only uses text color, with settings migration support.
- Disabled the scrollbar in the SFTP toolbar.
- Adjusted the NextTerminal instance settings interface.
- Adjusted automatic credential naming for NextTerminal.
- Improved terminal code structure.
- Refactored update check state management.

## v1.0.21

### Added

- Added a conflict resolution dialog when uploading files with the same name.
- Added asset ID copy support and unified CLI asset IDs.

### Fixed

- Fixed ZMODEM getting stuck when a file with the same name already exists.
- Fixed pasted terminal content being highlighted in black.
- Fixed the terminal Ctrl+R history search shortcut.
- Fixed the missing second confirmation when closing the window on Windows.

### Changed

- Appearance settings no longer follow cloud sync.
- Changed the default AI command execution timeout to 30 seconds.
- Unified the add and edit parameters for NextTerminal instances.
- Adjusted the lrzsz location and added ZMODEM internationalization.
- Adjusted the light terminal theme colors.
- Recognized Ctrl-C cancellations for AI terminal commands and added cancellation guidance.
- Adjusted the AI command echo color to the #218bff blue palette.
- Improved SFTP file toolbar buttons.
- SSH terminal sessions now automatically inject encoding environment variables.

## v1.0.20

### Fixed

- Fixed settings API splitting behavior and prevented the external CLI switch from being reset.
- Fixed duplicate rendering in the terminal font preview.
- Fixed blurry terminal fonts after switching to a light theme.

### Changed

- Adjusted opacity percentage display.
- Replaced the color picker on the settings page.
- Improved AI panel input queue interactions.

## v1.0.19

### Added

- Added collapsible CPU core metrics.
- Added manual host operating system detection, with optional automatic detection.
- Added terminal background image and background opacity settings.
- The AI assistant now supports switching models.
- Added built-in default terminal fonts: Meslo on macOS and Cascadia Code on Windows.
- Sync settings now support showing passwords.
- Added recovery mode for cases where the encryption key is missing.

### Fixed

- Fixed terminal metrics not being isolated by session.
- Fixed the SFTP transfer list being too tall, and added Enter confirmation when creating folders.
- Fixed serial connection parameters and asset tree tooltip text.
- Fixed settings page internationalization and system language following.
- Fixed false conflict prompts when syncing on the same device.
- Fixed inaccurate memory statistics when Available is empty by falling back to Free.
- Fixed occasional AI command hangs and switched to streaming output parsing.
- Fixed sync configuration default options and password field layout.

### Changed

- Improved the AI command whitelist.
- Updated the Agent prompts.
- Removed authorization restrictions for SFTP batch downloads and image preview.

## v1.0.18

### Added

- The CLI now supports file upload and download.

### Fixed

- Fixed AI command execution timeouts.
- Fixed focus conflicts between the AI assistant and the terminal.
- Fixed focus handling for the host key accept button.
- Fixed unclear active states for asset sources in dark mode.
- Fixed node-pty executable permissions.
- Fixed inconsistent built-in Agent tool call and tool result pairing.
- Fixed Telnet sessions that produced no output and could reconnect repeatedly after disconnecting.
- Fixed context errors after the Agent refused to execute a command.
- Fixed cases where command execution could get stuck.
- Fixed appearance initialization before the app lock is shown.
- Fixed a crash that could happen when switching languages.

### Changed

- Improved the AI command execution flow.
- Removed the Claude Code ACP adapter.
- Upgraded Vite.
- Changed the editor to load asynchronously.
- Improved AI settings.
- Improved SSH authentication failure messages.
- Removed interactive AI command execution.
- Improved Agent processing.
- Removed AI output filtering.
- Refactored terminal handling logic.
- Improved PTY markers.
- Improved focus handling between terminals and input fields.

## v1.0.16

### Added

- Added built-in AI profiles.
- NextTerminal settings now use cards.
- The CLI now supports file upload and download.
- Added a report bug button.

### Fixed

- Fixed AI settings test streaming.
- Fixed the app lock close button.
- Fixed the NextTerminal CLI source name.
- Fixed external CLI settings copy.

### Changed

- Refactored external CLI skills.
- Updated release packaging targets.

## v1.0.15

### Added

- Added external CLI support, allowing Codex and Claude Code to query assets and execute commands.
- Added a Linux release.

### Fixed

- Fixed an issue where the app could not exit from the locked state on Windows.
- Fixed duplicate Electron instances.
- Fixed the maximize window control icon.

### Changed

- Improved AI interactive operations.

## v1.0.14

### Added

- Added automatic update support.
- Added app lock support.
- Added AI conversation history management.
- Added Claude Code AI Agent support.
- AI command execution now supports interactive operations.
- Added a paste selection action to the terminal context menu.
- NextTerminal now supports custom request headers.
- SFTP filenames now show a tooltip with the full name when truncated.

### Fixed

- Fixed AI chat state not being preserved after terminal reconnects.
- Fixed terminal theme and global UI theme sync.
- Fixed sync status messages that could be misleading before the first sync.
- Fixed overly long path titles in tabs.
- Fixed app lock state not refreshing when the window regains focus.

### Changed

- Improved the AI settings page.
- Improved ACP copy.
- Improved AI command execution output display.

## v1.0.13

### Added

- Added SSH keyboard-interactive authentication support.
- Added NextTerminal upstream proxy settings.
- Added an app mode switch to the sidebar.
- Added a terminal theme copy action.
- Added a copy IP action to context menus.
- Added Alpine logo support and OS auto-detection.
- Asset tree now supports Shift range selection and batch connection.
- Copied SSH sessions now automatically open in the same directory.

### Fixed

- Fixed RSA credential key type support.
- Fixed command snippet drag rectangle type guard handling.
- Fixed invalid AI test behavior.

### Changed

- Local terminal tab titles now update automatically.
- Local fonts are now excluded from sync.
- Improved AI settings.
- DeepSeek models now only allow disabled thinking.
- Adjusted the keyword highlight rules layout.
- Refactored the shortcuts settings layout.
- Refactored the appearance sections in settings.
- Global pages now follow the appearance terminal theme.
- Terminal theme switching now syncs the global theme.
- Aligned local asset toolbar buttons.

## v1.0.12

### Added

- Added Codex support to the AI features.
- Added support for deleting custom logos.
- Added an expand-group menu to the asset tree.
- Command snippets now support drag-and-drop sorting.
- Keyword highlight rules now support drag-and-drop sorting.
- Added log capture for backend startup failures.

### Fixed

- Fixed asset tree host icon alignment.
- Fixed custom logo deletion during sync.
- Fixed NextTerminal reconnecting after a normal exit.
- Fixed terminal text selection so it can cover keyword highlights.
- Fixed Chinese text encoding issues in some macOS environments.

### Changed

- Improved AI features.
- Improved the AI command whitelist.
- Confirmation dialogs now focus the confirm button by default.
- Terminal fonts now use real virtual terminal rendering.
- Disabled refresh to prevent accidental activation.
- Improved log formatting.

## v1.0.11

### Added

- Added upstream access authentication for NextTerminal, including Basic Auth and mTLS.
- Added support for switching AI models.
- Local terminals now recognize file paths when files are dragged into the terminal.
- Keyword highlight rules now support a remark field.
- SSH connections now support additional host key algorithms for compatibility with legacy servers.
- Added SSH pre-connect authentication and host key confirmation.

### Fixed

- Fixed automatic reconnect and normal-exit detection.
- Fixed sync time updates when a sync operation makes no changes.
- Fixed batch execution terminal layout so the number of terminals per row is limited.
- Fixed an issue where switching tabs could hide the "open editor" button in SFTP.
- Fixed an out-of-bounds issue when importing JSON keyword highlight rules.
- Fixed terminal copy and paste by using the Electron clipboard.

## v1.0.10

### Added

- Added iCloud and local directory sync.
- Added support for configuring multiple NextTerminal environments.
- NextTerminal login now supports access through WebSocket tunnels.
- Added AI actions to the terminal context menu.
- Added a recording status indicator in the terminal top-right corner.
- Added a confirmation dialog when enabling the AI assistant.

### Changed

- Backend browser opening now uses the official library.
- Improved reconnect messages.
- Improved AI interaction.

## v1.0.8

### Added

- Added license expiration time display.
- Added support for downloading session recordings.

### Fixed

- Fixed terminal tab title and focus handling after connection failures.
- Fixed SFTP workspace reconnection and transfer behavior.
- Fixed terminal tab bar scrolling when many tabs are open.

### Changed

- Temporary connections now focus the IP input by default.
- Moved the host remark field in the host dialog.
- Disabled spellcheck for remark fields.
- Terminal tabs now continue showing numbers above 9, use a single dropdown arrow when overflowed, and auto-scroll horizontally while dragging tabs near the edge.
- Improved command snippet asset selection.
- Improved the login flow and added login cancellation support.
- Improved license information display.
- Refactored the SFTP file browser.
- Improved search result rendering.
- Improved terminal keyword highlighting.
- Improved session recording.
- Local terminal paths and working directories no longer sync to other devices.

## v1.0.7

### Fixed

- Fixed terminal copy behavior so it only copies when text is selected.
- Fixed the terminal latency overlay covering the batch execution button.
- Fixed terminal cursor position after reconnecting.
- Kept the AI tab WebSocket connection active when switching tabs.

## v1.0.6

### Added

- Added support for opening the AI assistant in multiple sessions at the same time.
- Added collapsible command snippet groups.
- Added SFTP folder upload support.
- CSV asset import now supports asset group fields.
- Added ZMODEM file transfer support.
- Added SSH keepalive latency display.
- Added customizable terminal copy and paste shortcuts.

### Fixed

- Fixed an issue where Ctrl + Shift + V could paste twice on Windows.
- Fixed long filename overflow in the SFTP delete confirmation dialog.
- Fixed custom terminal theme JSON editor width constraints.
- Fixed terminal scrollbar alignment on the right edge.
- Fixed toast notifications overlapping the tab bar.
- Fixed terminal tab bar scrolling and drag-region behavior.
- Fixed terminal output preservation after reconnecting.

### Changed

- Improved the AI settings UI.
- Improved the terminal font picker.
- Optimized the default sidebar width.
- Tightened AI command confirmation behavior.
- Simplified AI command confirmation handling.
- Switched to the assisted Windows installer.

### Removed

- Removed Linux packaging.

## v1.0.5

### Added

- Added support for syncing custom logos incrementally.
- Added a host remark field.
- Added optional SSH keepalive configuration.
- Added terminal tab close options.
- Added regular expression support for terminal keyword highlights.
- Added SFTP copy path menu actions.
- Added support for pressing Enter in the batch command input to execute commands.
- Asset tree tooltips now show usernames.

### Fixed

- Fixed terminal copy and paste shortcuts.
- Fixed an issue where SFTP download renaming did not take effect.
- Fixed multi-select SFTP drag preview behavior.
- Fixed an issue where terminal panes could be unmounted when splitting.
- Fixed AI settings refresh before each prompt.
- Fixed unsupported locale handling.
- Fixed long-name overflow in the batch asset selection dialog.
- Fixed SFTP asset picker width constraints.
- Fixed dialog overlay clicks closing dialogs unexpectedly.

### Changed

- Moved AI into a resizable terminal sidebar.
- Improved terminal SFTP session isolation.
- Optimized the SFTP toolbar and reused SFTP file controls.
- Simplified API error type matching.
- Unified settings page configuration card styles.
- Improved settings page form alignment.
- Improved keyword highlight switch alignment and label text.

## v1.0.4

### Added

- Added session recording.
- Added a terminal context menu.
- Added cursor style configuration.
- Command snippets now support sorting and configurable automatic execution.

### Fixed

- Fixed an issue where split-screen shortcuts did not work.
- Fixed an issue where serial port resources were not released.

### Changed

- Improved shortcut text.
- Improved split-screen behavior.
- Improved the Windows/Linux exit confirmation UI.

## v1.0.3

### Added

- Added file size display to the update dialog.
- Added support for custom terminal themes.

### Fixed

- Fixed an issue where terminal reconnection could get stuck in mouse mode in special cases.
- Fixed an issue where private key credentials with passphrases could not be used.
- Fixed left-side alignment in fullscreen mode on Mac.

### Changed

- Unified file size formatting.
- Improved the private key credential creation flow.
- Improved AI settings.

## v1.0.2

### Fixed

- Fixed incorrect prompt when canceling a download.
- SFTP delete now succeeds silently when the target file does not exist.

### Changed

- Sidebar width is now stored on the frontend.

### Removed

- Removed trial limitations.

## v1.0.1

### Added

- AI assistant compatibility with DeepSeek V4.
- Custom prompts for the AI assistant.
- Custom User-Agent configuration for the AI assistant.
- Password or key reveal support for hosts, credentials, temporary connections, AI settings, and data sync.

### Changed

- Disabled online updates for the Windows portable edition.

## v1.0.0

- Initial release.
