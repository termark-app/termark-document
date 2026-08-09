---
title: Changelog
description: Termark release notes and product updates.
---

# Changelog

This page records Termark product updates, bug fixes, and behavior changes.

For earlier releases, see the [changelog archive (v1.0.47 and earlier)](/changelog-archive).

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
