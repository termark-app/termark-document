---
title: Mobile Changelog
description: Termark mobile release notes and product updates.
---

# Mobile Changelog

This page records updates, bug fixes, and behavior changes for Termark mobile.

## v0.1.14 (2026-08-09)

### Added

- Added process management and systemd service management tools.
- Completed Telnet host support.
- Added support for purchasing PRO through Apple In-App Purchase.

### Fixed

- Fixed the terminal status bar display in dark themes.
- Fixed configuration and permission issues with temporary directories used for Git sync on mobile.
- Fixed tmux session switching and status detection.
- Fixed scrolling in the multiline editor.
- Fixed possible content overlap in the PRO plan display.
- Fixed action layout and product diagnostics issues in the PRO upgrade dialog.

### Changed

- Updated mobile to support SSH credential management.
- Redesigned the PRO upgrade page and unified account and PRO settings.
- Made the professional operations toolbox a PRO feature.
- PRO cloud sync now requires a linked account.
- PRO purchases on Android now redirect to the official website.
- Improved settings summaries and added an official website link to the About page.

## v0.1.12 (2026-08-04)

### Added

- Added native management of terminal background connection state.

### Fixed

- Fixed mobile session reliability and lifecycle issues.
- Fixed adaptive layout and navigation issues.
- Fixed the Android status bar not matching the application theme.
- Fixed an existing terminal not being reused when opening the application from an iOS Live Activity.

### Changed

- Improved the host source switcher interface and interactions.
- Improved the AI context host selector.
- Reduced the visual prominence of the divider in the AI chat page header.

## v0.1.11 (2026-08-04)

### Added

- Terminal press-and-hold directional gestures now adjust movement speed based on swipe distance.

### Fixed

- Restored native text selection in the terminal.

### Changed

- Improved the styling of terminal dock controls.
- Removed the option to control terminal font size with the volume buttons.

## v0.1.10 (2026-07-31)

### Added

- Added terminal font management.
- Added support for collapsing and expanding host groups.
- Added jump host support for SSH connections.
- Added a host credential selection page.
- Added support for adjusting terminal font size with the volume buttons.
- Added terminal press-and-hold directional gestures, double-tap to send Tab, and haptic feedback for gestures.
- Added Docker container and systemd service management in the terminal.
- Added Git as a cloud sync storage provider.

### Fixed

- Fixed interaction issues in the AI context selector.
- Fixed terminal connection regressions.
- Fixed inconsistent behavior between official cloud sync and S3 sync.
- Fixed scrolling issues in dialogs and bottom sheets.
- Fixed navigation issues on the Docker details page.
- Fixed media volume changing when opening a terminal.
- Fixed double-tap gestures triggering text selection in the iOS terminal.
- Fixed terminal Live Activities not ending after the iOS application exited.
- Unified the version number displayed throughout the application.

### Changed

- Updated mobile for the OIDC dual-token authentication scheme.
- Refactored terminal interfaces and integrated the shared SDK, improving native terminal view management across multiple sessions.
- Migrated cloud sync to the shared SDK.
- Improved forms, settings pages, navigation bars, empty states, and loading states.
- Hid drag indicators in bottom sheets that cannot be dragged.
- Added external-link indicators to links on the version settings page.
