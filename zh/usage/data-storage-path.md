---
title: "Termark 数据存储路径：Windows、macOS 与便携版"
description: "查看 Termark 在 Windows、macOS 和 Windows 便携版中保存会话配置、日志与本地数据的默认路径。"
outline: deep
---

# 数据存储路径

Termark 的数据（会话配置、日志等）默认存储在以下位置：

| 平台 | 路径 |
|------|------|
| Windows | `%AppData%\Termark\backend` |
| macOS | `~/Library/Application Support/Termark/backend` |
| Windows 便携版 | 当前文件夹下的 `data` 目录 |

## 便携版说明

Windows 便携版将数据存储在程序所在目录的 `data` 文件夹中，无需写入系统 AppData 目录，方便放在 U 盘或自定义路径下随身携带。
