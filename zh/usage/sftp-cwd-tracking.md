---
title: "让 SFTP 自动跟随 SSH 终端当前目录"
description: "配置 Bash、Zsh 或 Fish，使 Termark 的 SFTP 面板自动跟随 SSH 终端当前工作目录。"
outline: deep
---

# SFTP 目录跟随配置

Termark 的 SFTP 面板支持自动跟随终端当前工作目录，需要在远程主机的 shell 配置文件中添加以下内容。

原理：shell 每次切换目录后，向终端发送 `OSC 1337` 序列报告当前路径，Termark 检测到后自动同步 SFTP 面板的目录。

### Bash

编辑 `~/.bashrc` 或 `~/.bash_profile`：

```bash
PROMPT_COMMAND='printf "\e]1337;CurrentDir=%s\a" "$PWD"'
```

### Zsh

编辑 `~/.zshrc`：

```zsh
precmd() { printf "\e]1337;CurrentDir=%s\a" "$PWD" }
```

### Fish

编辑 `~/.config/fish/config.fish`：

```fish
function __termark_cwd --on-event fish_prompt
    printf "\e]1337;CurrentDir=%s\a" $PWD
end
```

## 生效方式

添加配置后重新登录，或执行 `source` 加载对应配置文件即可。

## 注意事项

如果你已经在 Bash 中使用了 `PROMPT_COMMAND`，或在 Zsh 中定义了 `precmd()`，需要把上面的逻辑合并到现有配置里，避免覆盖原有提示符行为。

## 相关页面

- [端口转发](/zh/usage/port-forwarding)
- [OpenWrt 无法使用 SFTP](/zh/usage/openwrt-sftp)
