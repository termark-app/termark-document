---
title: SSH 跳板机怎么配置？ProxyJump、多跳认证与 SFTP 指南
description: SSH 跳板机和多跳连接怎么配置？本文说明 ProxyJump、不同节点凭据、主机指纹、Agent Forwarding 风险、代理与 SFTP 穿越跳板链路。
date: 2026-08-15
updated: 2026-08-15
author: Termark Team
---

# SSH 跳板机怎么配置？

跳板机（bastion host）让客户端先连接一个可达入口，再从入口访问内网目标。它解决的是网络路径问题，不会自动解决身份、主机验证和权限隔离。

## OpenSSH ProxyJump

```sshconfig
Host bastion
  HostName bastion.example.com
  User gateway
  IdentityFile ~/.ssh/bastion_ed25519

Host internal-app
  HostName 192.0.2.25
  User deploy
  IdentityFile ~/.ssh/internal_ed25519
  ProxyJump bastion
```

示例使用 `example.com` 和 RFC 文档地址，不是真实设施。连接时：

```bash
ssh internal-app
sftp internal-app
```

OpenSSH 会为每一层按配置选择账号、密钥和主机指纹。多跳可写成 `ProxyJump hop1,hop2`，但链路越长，排障和权限管理越复杂。

## 每一跳都应独立认证

跳板机账号不应默认等于目标服务器账号。分别保存：

- 主机名与端口；
- 用户名；
- 私钥与口令；
- 主机指纹；
- 允许访问的目标范围。

不要为了省事把同一把高权限私钥复制到所有节点。

## Agent Forwarding 风险

Agent Forwarding 不会直接复制私钥，但被攻陷的中间主机可能在转发有效期间请求 Agent 签名。只在明确需要、信任链路并限制密钥用途时启用。多数场景可以让客户端直接为目标主机完成认证，而不把 Agent 暴露给跳板环境。

## 跳板机、HTTP/SOCKS 代理不是一回事

- SSH 跳板：通过 SSH 连接建立到目标 SSH 服务的路径；
- HTTP/SOCKS 代理：代理 TCP/HTTP 流量，认证与 DNS 行为不同；
- 动态转发：在本机建立 SOCKS 代理，通过 SSH 主机访问不同目标。

配置时应明确链路类型，避免把“能走代理”误解为“能完成多跳 SSH 认证”。

## 图形化配置要检查什么

下面复用已有的 Termark 主机创建截图。连接方式区域可选择直接连接、SSH 跳板或代理：

![Termark 创建 SSH 主机窗口，包含认证方式和 SSH 跳板或代理连接配置](./images6/termark-new-ssh-host.png)

*图形界面应让用户看清每一跳的目标和凭据，而不是隐藏实际连接路径。*

测试步骤：

1. 先单独连接跳板机；
2. 再验证目标主机指纹；
3. 为两层选择不同凭据；
4. 打开 SFTP，确认文件操作发生在目标主机；
5. 断开跳板，确认目标会话与转发的状态；
6. 检查日志是否能定位失败发生在哪一跳。

## SFTP 穿越跳板链路

SFTP 是 SSH 子系统，通常可复用同一跳板配置。客户端应确保终端和 SFTP 指向同一个最终目标，并明确上传、覆盖、权限修改发生在哪台机器。复杂链路中不要仅凭标签名称判断目标。

## 常见故障

- 跳板可达但目标超时：检查跳板到目标的路由和防火墙；
- 认证次数过多：限制每层候选密钥并明确 `IdentityFile`；
- 主机指纹变化：先查明重装、地址复用或中间人风险；
- SFTP 打开错误主机：核对最终目标和连接上下文；
- 多跳后端口转发失败：确认监听端和目标是从哪一层视角解释。

**用 Termark 试试跳板机连接：**<a href="https://www.termark.app/zh-cn/ssh-client/?utm_source=docs&utm_medium=blog&utm_campaign=ssh_jump_host_guide&utm_content=article_cta" data-umami-event="blog-cta-click" data-umami-event-campaign="ssh_jump_host_guide" data-umami-event-destination="ssh-client">查看跨平台 SSH 客户端</a>。
