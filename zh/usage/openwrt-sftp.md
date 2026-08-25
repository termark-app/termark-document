---
title: "为什么在 OpenWrt 默认 SSH 下无法使用 SFTP"
description: "Termark 在 OpenWrt 上 SSH 正常但 SFTP 提示子系统失败？OpenWrt 默认的 Dropbear 不带 SFTP，需安装 openssh-sftp-server 或换用 OpenSSH。"
outline: deep
---

# 为什么在 OpenWrt 默认 SSH 下无法使用 SFTP

如果 Termark 连接 OpenWrt 设备的 SSH 终端正常，但 SFTP 面板提示以下错误，不是 Termark 的问题——OpenWrt 默认使用 **Dropbear**，它本身不包含 SFTP 服务：

> **加载文件失败: session not found: create SFTP client failed: error receiving version packet from server: server unexpectedly closed connection: unexpected EOF**

这是 Dropbear 收到 `sftp` 子系统请求时找不到 `sftp-server` 可执行文件，直接关闭通道，客户端收不到版本包而报 `unexpected EOF`。其他等价提示包括 `subsystem request failed` / `sftp-server not found` / `unable to initialize SFTP`。

## 现象

- SSH 终端正常连接、命令可执行。
- SFTP 面板打不开，或传文件时提示 `unable to initialize SFTP` / `subsystem not found`。
- 同样的 Termark 配置在 Debian / Ubuntu / CentOS 上完全正常。

## 原因：Dropbear 与 OpenSSH 的区别

|  | Dropbear（OpenWrt 默认） | OpenSSH |
|---|---|---|
| 体积 | 约 300 KB，面向嵌入式 | 约 6 MB |
| 定位 | 轻量 SSH Shell + SCP | 完整 SSH 套件 |
| SFTP 支持 | **无**——未打包 `sftp-server` | 有——自带 `/usr/lib/openssh/sftp-server` |

OpenWrt 为节省闪存选用 Dropbear，SFTP 是一个独立子系统（`sftp-server` 可执行文件），Dropbear 不自带。没有它，SSH 服务器无法处理客户端的 `sftp` 子系统请求，直接拒绝通道。

## 如何确认

在 OpenWrt 设备上执行：

```bash
# 1. 看当前跑的是哪个 SSH 服务
ps | grep -E 'dropbear|sshd'

# 2. 看 sftp-server 是否存在
ls -l /usr/libexec/sftp-server /usr/lib/sftp-server 2>&1

# 3. Dropbear 没有 Subsystem 配置
cat /etc/config/dropbear 2>&1 | head -20
```

如果 `sftp-server` 不存在且 `dropbear` 在运行，即可确认原因。

## 解决办法（三选一）

### 方案一：安装 `openssh-sftp-server`（推荐，约 1 MB）

保留 Dropbear，只补上 SFTP 子系统：

```bash
opkg update
opkg install openssh-sftp-server

# 验证
ls -l /usr/libexec/sftp-server
# 应显示：-rwxr-xr-x 1 root root ... /usr/libexec/sftp-server
```

无需重启或改配置，下一次 SFTP 连接时 Dropbear 会自动找到 `sftp-server`。在 Termark 中重新打开 SFTP 面板验证即可。

如果仍失败，确认 OpenWrt 版本为 21.02 及以上。旧版本路径不同，需补软链：

```bash
mkdir -p /usr/libexec
ln -sf /usr/lib/sftp-server /usr/libexec/sftp-server 2>/dev/null
```

### 方案二：改用 SCP

如果闪存极度紧张、无法安装任何包，可在 Termark 之外用 SCP 单文件传输作为临时绕开办法（Termark 的 SFTP 面板依赖 SFTP，无法用此方式替代）：

```bash
scp file.bin root@openwrt:/tmp/
```

### 方案三：把 Dropbear 换成 OpenSSH（较重）

仅当你需要 OpenSSH 的完整能力（密钥限制、更丰富的 `sshd_config`）时再考虑：

```bash
opkg update
opkg install openssh-server openssh-sftp-server
/etc/init.d/dropbear disable
/etc/init.d/sshd enable
/etc/init.d/sshd start
```

代价：多占约 5–6 MB 闪存，内存占用更高。多数用户应优先选方案一。

## 仍不通？

1. **装了仍失败**——安装后重连 SSH 再试，部分 Dropbear 版本按连接缓存子系统。
2. **提示空间不足**——执行 `df -h` 和 `opkg list-installed | wc -l` 检查闪存占用，先卸载无用包。
3. **SFTP 已连上但无权限**——说明 SFTP 已通，只是登录用户对目标路径无读写权限，检查 `ls -ld /path`。

## 给 Termark 用户的建议

对于 OpenWrt 路由器 / NAS / 软路由，**方案一是最佳平衡**：一条 `opkg install`（约 1 MB）即可让 Termark 及其他 SFTP 客户端恢复文件管理能力，无需替换轻量 SSH 服务。

