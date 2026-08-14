---
title: "Termark Data Storage Paths on Windows and macOS"
description: "Find where Termark stores session settings, logs, and portable-edition data on Windows and macOS."
outline: deep
---

# Data Storage Path

Termark stores its data (session configurations, logs, etc.) in the following locations by default:

| Platform | Path |
|----------|------|
| Windows | `%AppData%\Termark\backend` |
| macOS | `~/Library/Application Support/Termark/backend` |
| Windows Portable | `data` directory under the current folder |

## Portable Edition

The Windows portable edition stores data in the `data` folder next to the application executable. This avoids writing to the system AppData directory and makes it easy to carry on a USB drive or run from a custom location.
