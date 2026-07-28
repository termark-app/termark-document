---
title: Changelog
description: Termark release notes and product updates.
---

# Changelog

This page records Termark product updates, bug fixes, and behavior changes.

For earlier releases, see the [changelog archive (v1.0.47 and earlier)](/changelog-archive).

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
