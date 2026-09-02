---
title: Changelog
description: Termark release notes and product updates.
---

# Changelog

This page records Termark product updates, bug fixes, and behavior changes.

For earlier releases, see the [changelog archive (v1.0.47 and earlier)](/changelog-archive).

## v1.6.5 (2026-09-02)

### Added

- Added sorting for the SFTP file list in workspaces.
- Added a one-click reconnect for detached terminals on the batch-execution page.
- Added a terminal password-credential hint, with focus-restore fix.

### Fixed

- Fixed inconsistent terminal background transparency in batch execution.
- Fixed corrupted data being persisted when a size-based resume was interrupted by an error.
- Fixed transparent background rendering in the SFTP workspace.
- Fixed the transfer list still showing a spinner after small-file uploads complete, and canceling incorrectly reporting "task already done".

### Changed

- Windows updates now install silently and auto-relaunch the new version after restart.
- Renamed the AI assistant back to "AI 助手" and removed duplicate compactHint copy.
- Optimized the terminal password-credential overlay styling and transparency.
- File transfers no longer sync file permissions; both overwrite and create use the target's default semantics.

## v1.6.2 (2026-08-30)

### Added

- Added local toolset to Global AI (local_execute, local_file_read/write/edit, local_skill_read) reusing the existing approval pipeline and supporting `~/.agents/skills` indexing, with a configurable local working directory.
- Added working-directory switching, local file attachments, project convention injection (`AGENTS.md` / `CLAUDE.md`, 64KB cap), manual compaction trigger, and background long-task execution (`background` + `local_task_status`) to Global AI.

### Fixed

- Fixed stale compaction checkpoint persisting in memory session history after message rewrites or truncation.
- Fixed manual compaction using an empty session ID and improved the error message for too-short conversations.

### Changed

- Reworked context compaction with tiered truncation of older tool outputs (last 3 kept, older truncated to 2000 runes), tightened summary budget from 16384 to 4096 with stricter length constraints, moved the checkpoint to the conversation start for stable system prompt caching, and merged consecutive same-role messages for Anthropic.
- Improved AI context statistics and compaction state persistence, with token-usage display and compaction status in the header.
- Made manual compaction a traceable `conversation_compact` event (running/failed/succeeded) with optimistic UI and before/after token display.
- Redesigned AI input toolbar and layout: new plus menu for attachments/context/compaction, model selector next to send, compact send/stop buttons, transparent dialog styling, and optimized top/header layout.

## v1.6.1 (2026-08-28)

### Added

- Added history clearing for AI Shell.

### Fixed

- Fixed repeated password prompts when configuring cloud sync.
- Fixed service detail query failure on older systemd versions.
- Fixed RDP window not visible when connecting to a Next Terminal RDP asset on Windows.

### Changed

- Restricted switching execution mode while an AI task is running.
- Allowed editing AI and SFTP capabilities for restricted Shell hosts.

## v1.6.0 (2026-08-27)

### Added

- Added multi-select and batch connect to the quick connect dialog.
- Added sudo support for non-root users and Podman support in the Docker panel, with backend-assembled terminal commands.
- Added user-level systemd services in the system services panel.
- Added copy AI message as image and simplified bubble styling.
- Added force-overwrite cloud data after forgetting the sync password.
- Added an entry to open the log folder.
- Added prompt caching for Anthropic conversations.
- Added a dedicated RouterOS restricted Shell adapter.
- Added hourly automatic update checks.
- Added support for passwordless SSH connections with persisted authentication method.
- Added folder accelerated download with tar.gz staged transfer.
- Added tab double-click behavior setting and unified copy session wording.
- Added synced SFTP favorite paths with quick jump.
- Added account license purchase and management entry.
- Added SSH idle connection pooling for CLI and Global AI with configurable idle timeout.

### Fixed

- Fixed the terminal password prompt not appearing and restructured its detection logic.
- Fixed the Windows RDP file launch method.
- Fixed compatibility for viewing service logs on older systemd versions.
- Fixed process detail showing "process not found" on older procps (e.g. CentOS 7).
- Fixed terminal keyword highlighting not matching across soft-wrapped lines.

### Changed

- Refactored AI conversation compression to a single Markdown checkpoint and increased the model output budget (disabled thinking mode for DeepSeek compression).
- Improved the AI auto-approval resubmit flow and surfaced specific failure reasons.
- Streamlined backend AI execution and safety checks and removed the SSH timeout extension.
- Migrated the AI terminal executor into the SDK and reused the RouterOS Shell; unified output truncation and improved RouterOS execution reliability.
- Upgraded to Go 1.27 and dependencies.
- Optimized terminal sidebar feature guidance.
- Optimized PRO feature entry points and restricted quick delete.
- Reworked accelerated upload to tar.gz staged transfer.
- Moved SSH connection settings into the general settings page and removed the standalone menu.

## v1.5.1 (2026-08-22)

### Added

- Added affiliate sharing dialog with referral link, tier badges and three-level commission rates, plus a backend proxy for the store affiliate overview.

### Fixed

- Fixed confirmation dialog being unclickable while the app was locked.
- Fixed incomplete AI tool-call arguments causing persistent 400 errors and unrecoverable sessions (invalid JSON truncated to \"null\" instead of \"{}\").

### Changed

- Improved AI auto-approval context handling and retry logic for failed reviews.
- Fixed approval review background evidence budget propagation so long assistant context is truncated within budget instead of being dropped.

## v1.5.0 (2026-08-21)

### Added

- Added AI web page reading tool with HTML parsing, enabled by default and backed by the SDK.
- Added AI file editing capabilities via SFTP with lifecycle management and diff preview support.
- Added combined host query tools for Global AI with multi-condition filtering.
- Added AI approval configuration (approval model, timeout, and API environment) and dedicated "Always Approve" action with session-scoped memory.
- Added per-host SFTP default directory configuration.
- Added generic Agent Skills installation support.
- Added Armbian logo and automatic system detection.
- Added asset tree connection info and "Connect All Hosts" for groups, with improved grouping menus.
- Added split-view asset picker support for Telnet and Serial connections.
- Added Windows Acrylic background option persisted as a local setting.
- Added AI approval system notifications with click-to-locate.

### Fixed

- Fixed blank assistant bubbles when restoring conversation history.
- Fixed multibyte truncation errors in command output by centralizing truncation in the SDK.
- Fixed re-review of approved commands, including session memory, "always" semantics, and system path fallbacks.
- Fixed incomplete approval state handling in balanced mode and single-file deletion.
- Fixed NextTerminal key login with OTP interactive authentication.
- Fixed WebAssembly CSP error in terminal playback.
- Fixed application window state loss after update and startup loading page theme flicker.
- Fixed serial port resource release on close.
- Fixed browser authorization not bringing the app to the foreground.
- Fixed built-in AI configuration save crash and development warnings.
- Fixed long-lived transfer event connections blocking graceful shutdown.
- Fixed Global AI host query and history content recovery.

### Changed

- Relaxed and simplified approval logic and improved `su` command confirmation.
- Moved approval memory, AI web reading, and command truncation into the SDK for zero-config reuse across desktop and mobile.
- Refactored synchronized data into an envelope and integrated the official object storage API, improving WebDAV compatibility and support for stores without remote rename.
- Reused SSH connection pooling and idle recycling for Global AI.
- Improved port forwarding disconnect detection and auto-reconnect, and optimized host editor SSH layout.
- Streamlined AI base tools and merged host query tools, with updated tool display.

## v1.4.0 (2026-08-13)

### Added

- Added a metrics monitoring status bar at the bottom of the terminal, with support for viewing and filtering network connections.
- Added automatic interactive OTP authentication for hosts and improved authentication retries for multi-hop connections.
- AI conversations now support queuing input while a response is in progress, sending queued messages immediately, and editing a previous message to restart the conversation from that point.
- Added automatic context compression for AI conversations and on-demand access to SSH runtime context.
- Added a diff preview before AI writes changes to files.
- Added support for editing remote SFTP files with local applications.
- Added multi-window support with isolated instances for different development environments.
- Added manual Touch ID unlocking to the macOS application lock while retaining password-based unlocking.
- Added a setting to remember local window size and position.

### Fixed

- Fixed focus switching in the terminal search box.
- Fixed authentication tokens being refreshed unexpectedly when reading account status.
- Fixed incomplete DeepSeek reasoning history being sent back to the model and ensured that complete conversation messages are preserved.
- Fixed duplicate messages being appended when retrying a failed AI response.
- Fixed the settings dialog not scrolling in small windows.
- Fixed S3 object access tests failing when `HeadBucket` permission is unavailable.
- Fixed SVG images not being accepted when uploading asset logos.
- Fixed flickering in CLI file transfer progress and blocking during some connection shutdowns.

### Changed

- Redesigned the settings sidebar, account area, and AI Assistant page, and unified the layout and visual hierarchy across Appearance, Terminal, Keyword Highlighting, NextTerminal, Data Management, and other preference pages.
- Improved the main interface and terminal sidebar layouts, and simplified the selected and empty states in the asset tree.
- Reorganized cloud sync settings and actions, unified the official sync data and metadata formats, and improved WebDAV compatibility by adopting a standard SDK.
- Improved lifecycle management for CLI file transfers and SSH connections.
- Newly added hosts now appear at the top of the asset list by default; switching the active tab now clears the asset tree selection.
- Authorization IDs are now displayed in the account status bar by default.

## v1.3.0 (2026-08-09)

### Added

- Added support for configuring local bind addresses and IPv6 addresses for port forwarding.
- Added support for viewing active port-forwarding connections.

### Fixed

- Fixed SSH Agent authentication when multiple keys are available.
- Fixed attaching to and switching tmux sessions on older tmux versions, and improved session exit handling and current-client detection.
- Fixed authentication token rotation failures and improved automatic recovery from invalid sessions.
- Fixed some requests to the official AI service failing.
- Fixed the SFTP file list not refreshing when an upload completed while the panel was hidden.
- Fixed several SFTP transfer progress and status display issues.
- Fixed incorrect host ordering in the local asset tree.

### Changed

- Improved data collection and refresh performance for large process lists.
- Improved scrolling while AI responses are streamed.
- Added indicators to paid feature entry points and adjusted how professional operations and session history features are allocated between plans.

## v1.2.0 (2026-08-05)

### Added

- Added configuration sync through generic HTTPS Git repositories.
- Added systemd service management, including service lists and details.
- Added cross-platform SSH Agent authentication and authorization checks before connecting.
- Added terminal rendering engine settings with runtime switching support.
- Added terminal process management.
- Improved session history with directory organization, export, and archiving support.
- Added team authorization information display in the desktop application.

### Fixed

- Fixed tmux session connection compatibility across different shells.
- Fixed possible timeouts during the SSH interactive authentication handshake.
- Fixed a race condition in automatic polling after cloud sync was paused.
- Fixed focus not being restored after closing terminal search.
- Fixed SSH Agent environment detection when launching from the macOS Dock.

### Changed

- Migrated terminal metrics collection and improved cross-platform Docker and tmux compatibility.
- Improved the systemd service list and details styling.
- Unified the destructive styling of Stop actions.
- Improved process list presentation and start time formatting.
- Unified session recording exports and improved history action buttons.
- Added client-side sorting to SFTP file lists.

## v1.1.6 (2026-07-28)

### Changed

- Removed automatic terminal tab title updates.

## v1.1.5 (2026-07-28)

### Added

- Added support for viewing SFTP file information.
- Added GitHub-based configuration sync with HTTP and SOCKS5 proxy support.
- Added descriptions for commands executed by AI.
- Added terminal latency display and a toggle to control it.

### Fixed

- Fixed terminal rendering artifacts caused by a shared WebGL texture atlas.
- Fixed the source used to cache host names in Global AI.
- Fixed the update window appearing when the latest version was already installed.
- Fixed incorrect cancellation states while AI tools were running.
- Fixed the application freezing when a mouse side button triggered Back.
- Fixed cloud sync overriding the appearance mode.
- Fixed the macOS local network permission declaration and its localization.

### Changed

- Improved host name display in Global AI and removed duplicate host names from tool details.
- Unified terminal OSC status and notification handling.
- Refactored AI tool execution and confirmation state management, and improved tool call parameters and output styling.
- Distinguished base SSH titles from temporary Agent status titles.
- Improved custom tab titles and task status display, and added support for renaming tabs by double-clicking.
- Migrated sync configuration to a directory structure while preserving migration support for the legacy path.
- Changed anonymous statistics reporting to once every four hours.
- Improved the background styling of the terminal latency indicator.

## v1.1.4 (2026-07-20)

### Fixed

- Switched to a fixed application protocol and fixed shortcut listener initialization.
- Fixed text overlapping when the AI input box begins with spaces.
- Fixed Starship icons not displaying correctly in Windows terminals.
- Separated regular and batch terminal renderers and fixed the WebGL lifecycle.
- Fixed custom host logos not being displayed.

## v1.1.2 (2026-07-18)

### Added

- Added manual refresh for authorization information.
- Added AI retry status display and support for retrying failed requests.
- Asset tree host tooltips now display host notes.

### Fixed

- Restored the create-folder action in SFTP and improved toolbar callback handling.
- Fixed flickering when adjusting transparency while the language follows the system setting.
- Fixed Option+Arrow word navigation on macOS.

### Changed

- Updated the login and authorization flow for the new authentication scheme, using a single-session token and authorization expiration to determine local feature availability.
- Refactored frontend and backend asset loading to use the same origin and improved the Electron startup page.
- Improved natural sorting in SFTP file lists.
- Improved command snippet group expansion behavior.
- Added a scrollbar to the AI input box.
- Port forwarding and history action buttons are now always visible.

## v1.1.1 (2026-07-12)

### Added

- Added a copy button to AI Markdown code blocks.
- Added a clear button to the asset tree search box.
- Added an AI context toggle for host notes.
- Added automatic detection and connection support for WSL distributions.

### Fixed

- Fixed the directory being reset after switching SFTP tabs.
- Fixed styling issues in the AI settings section.
- Fixed NextTerminal RemoteApp configurations being lost.

## v1.1.0 (2026-07-07)

### Added

- Added the Beta update channel.
- Added support for Windows and Linux arm64.

### Changed

- Optimized the logo.
