---
outline: deep
---

# PowerShell Looks Strange in Light Mode

If you use PowerShell in Termark with a light terminal background, completion hints, syntax highlighting, or some output text may appear too light and become hard to read.

This is a common result of the default PowerShell and PSReadLine colors on light backgrounds. The default colors chosen for dark-background terminals work well for PowerShell and PSReadLine, but some users choose a light background with dark text. Because most default colors do not set a background color, light foreground colors on a light terminal background can produce unreadable text.

This is not a rendering issue caused only by Termark. It is the result of how PowerShell theme colors combine with the terminal background color.

See the Microsoft documentation: [Using a light theme in PowerShell](https://learn.microsoft.com/powershell/scripting/learn/shell/using-light-theme).

