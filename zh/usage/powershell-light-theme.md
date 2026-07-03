---
outline: deep
---

# PowerShell 在浅色模式下显示异常

如果在 Termark 中把终端背景设置为浅色，同时使用 PowerShell，可能会看到补全提示、命令高亮或部分输出文字颜色很浅，甚至接近不可读。

这是 PowerShell 和 PSReadLine 默认配色在浅色背景下的常见表现。PowerShell 默认选择的多数组件颜色更适合深色背景终端；但有些用户会选择浅色背景和深色文本。由于大多数默认颜色只设置了前景色，没有显式设置背景色，当浅色前景色显示在浅色背景上时，就会出现对比度不足、文字难以辨认的问题。

这个现象不是 Termark 单独导致的渲染问题，而是 PowerShell 主题颜色与终端背景颜色组合后的结果。

可以参考 Microsoft 官方文档：[在 PowerShell 中使用浅色主题](https://learn.microsoft.com/zh-cn/powershell/scripting/learn/shell/using-light-theme)。

