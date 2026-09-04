---
title: Mobile Changelog
description: Termark mobile release notes and product updates.
---

# Mobile Changelog

This page records updates, bug fixes, and behavior changes for Termark mobile.

## v0.2.2 (2026-09-04)

### Added

- Added the Termius Dark terminal theme preset.

### Fixed

- Fixed tmux touch scrolling on iOS.
- Fixed the reconnect backoff continuing after auto-reconnect is disabled.
- Fixed transient background SSH failures dropping the session; sessions now reconnect with backoff.
- Clarified the cloud sync credential migration prompt.

### Changed

- Updated the default AI assistant endpoint.

## v0.2.1 (2026-09-03)

### Fixed

- Fixed an Android crash when SSH credentials are missing.
- Aligned libtermux.so with Android's 16 KB page size requirement.

### Changed

- Completed store release readiness preparations.

## v0.2.0 (2026-08-31)

### Added

- Added haptic feedback for terminal custom keys.
- Added pinch-to-zoom font sizing in the terminal.

### Changed

- Removed SecureStore encryption from storage.

## v0.1.23 (2026-08-30)

### Added

- Added clickable links in the terminal.
- Added a password visibility toggle for inline fields.
- Modernized the SFTP file browser UI.

### Fixed

- Fixed the terminal scroll view not fully syncing.
- Fixed the NextTerminal port forwarding target compatibility issue.
- Fixed the Go SDK systemd interface adaptation after the SDK update.
- Fixed sync password field styling.
- Fixed navigation header accessory interactions.
- Fixed the diagnostics page layout and themed navigation / Pro badges.
- Fixed iOS compact live activity content insets.

### Changed

- Aligned mobile AI chat capabilities and UX with desktop.
- Refined host and SFTP action menus.

## v0.1.22 (2026-08-22)

### Added

- Added an "always approve" option for AI command approval.
- Host actions are now available from the row menu.

### Fixed

- Fixed AI streaming to render markdown throughout playback.
- Contained native panics at process boundaries to avoid crashing the app.
- Restricted controlled shell access to the terminal only.
- Prevented accidental host connection after a long press.

### Changed

- Reused SDK command output truncation and shared connection capabilities.

## v0.1.21 (2026-08-20)

### Added

- AI chat adapts to new SDK tools; refined conversation content design.
- Mobile AI settings and web fetch aligned with desktop.

### Fixed

- Fixed keyboard overlap in terminal AI chat.
- Stabilized the streaming conversation timeline.
- Improved the AI command confirmation picker.
- Polished the Docker manager UI.

## v0.1.20 (2026-08-19)

### Added

- Added a terminal AI assistant with a history side panel.
- Exposed the AI assistant from host lists.
- Opened the Docker manager as a terminal modal.
- Added Armbian logo and automatic system detection.

### Fixed

- Fixed background NextTerminal authorization prompts.
- Refined port forwarding rows and the native forwarding switch.

### Changed

- Adopted native iOS interactions, modal workflows, and host context menus.
- Redesigned the PRO upgrade sheet; moved host connection settings into a sheet.

## v0.1.19 (2026-08-17)

### Added

- Added SSH latency display in the terminal.
- Host form now supports OTP.
- Upgraded the SFTP text editor.
- Restored long-lived private key support for Next Terminal.

## v0.1.18 (2026-08-16)

### Added

- Added port forwarding support, including Next Terminal targets, with an independent tab.
- Next Terminal mobile connection flow aligned with desktop.
- AI supports the latest SDK and @-mentions of references.
- Added animated modal entrances and improved jump host connection settings.

### Fixed

- Enabled automatic host OS logo detection.
- Fixed official account token refresh for sync.
- Refined terminal gesture arbitration.

## v0.1.17 (2026-08-12)

- Internal release; no user-visible changes.

## v0.1.16 (2026-08-12)

### Added

- Added a full-screen AI task workspace; refined chat messages and editing.
- Cloud sync setup flow redesigned with recovery and conflict-safety fixes.

### Fixed

- Fixed mobile S3 configuration flow and Android source switcher restoration.
- Fixed AI runtime adaptation to the updated SDK.
- Aligned page search headers and PRO upgrade modal styling.

### Changed

- Refactored host assets, SFTP transfers, AI chat screen modules, and sync settings modules.
- Removed the AI history task list icon.

## v0.1.15 (2026-08-10)

### Added

- SSH sessions now stay alive in the Android background.

### Fixed

- Fixed the Android update flow dialog.
- Balanced navigation action spacing, insets, and divider; centered settings switches.

### Changed

- Aligned dark and light themes with the Telegram palette.
- Adopted a native host source switcher and streamlined appearance settings.
- Refined hosts layout, core screens, PRO upgrade modal, and AI host picker; compacted the settings menu.

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
