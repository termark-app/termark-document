---
title: AI SSH 客户端应该自动执行命令吗？Termark 的安全边界
description: AI 可以读取终端上下文、解释日志和生成排查命令，但生产服务器需要明确的执行边界。本文说明 Termark 内置 Agent、命令确认和外部 CLI 的设计取舍。
date: 2026-05-17
updated: 2026-08-15
author: Termark Team
---

# AI SSH 客户端应该自动执行命令吗？Termark 的安全边界

在我另一款产品 NextTerminal 里，我很早就做过一个 AI 助手。

那时候做得很简单：用户在后台配置 API、模型和提示词，打开终端后可以在旁边问一句"这个命令怎么写"。AI 给出命令，用户看一眼再决定要不要执行。

![next-terminal-ai.png](images3/next-terminal-ai.png)

功能不复杂，但当时反馈还不错。它解决的问题很具体：人在终端里工作，往往不是完全不会，而是需要一个能快速给出方向的助手，比如查日志、看进程、写一条 `grep`、解释一段报错、补一个一时想不起来的参数。

但我一直没把它再往前推、做成更激进的"自动运维 Agent"。原因很直白，服务器和代码仓库不是一回事。

代码仓库里 AI 删错文件，多数时候还能从 git 里找回来；Linux 机器上跑错一条命令，掉的可能是日志、配置、数据库文件，甚至直接把一台正在跑业务的机器搞坏。

后来做 Termark，AI 这块本来可以从头选型，上下文怎么给、Agent 形态怎么做、要不要支持外部 Agent，全都可以重来一遍。但 NextTerminal 上那个判断我没改。服务器场景的 AI，目标不是让它做得更多，而是让它在能控制的范围里把效率提上去。

---

## 会话 AI 与全局 AI，不是同一种上下文

Termark 现在提供两种 AI 使用范围。会话 AI 绑定一条终端会话，可以附带最近 N 行终端输出和准确的会话 ID；全局 AI 不会自动读取当前终端输出，而是通过用户明确选择的主机或分组工作。两类对话历史也分别保存，避免把不同现场混在一起。

![ai-overview.png](images3/ai-overview.png)

命令执行也有两种模式。默认的**后台执行**会复用当前 SSH 连接创建独立的后台 exec channel，不写入可见终端，也不共享当前终端 Shell 的 cwd、别名或临时环境变量。它适合大多数非交互命令，输出与状态更容易由 Agent 处理。

如果命令必须依赖当前目录、别名、`su` 后的身份或临时环境变量，可以切换到**终端 Shell 执行**。这个模式会把命令写入当前可见终端 Shell，因此能共享现场状态；代价是可能污染 Shell 历史，对复杂命令也不如后台模式稳定。网络设备或受限 Shell 则由后端使用独立 SSH Shell 执行，不能在会话内切换。

![ai-context.png](images3/ai-context.png)

这不是“可见执行安全、后台执行危险”的二选一。执行通道决定命令在哪里运行；审批策略决定是否需要用户授权，两者是独立设置。

## 自动、平衡和严格模式

服务器可能是个人 VPS，也可能是生产环境。为了让不同风险偏好的用户自行选择，Termark 目前提供三档审批策略：

- **自动模式**：AI 执行命令和写文件时不请求确认，适合用户信任所选模型并希望连续自动完成任务的场景。
- **平衡模式（默认）**：仅明确只读的观察命令自动执行；改文件、改配置、安装软件、移动文件、变更服务以及无法确认只读的命令都需要确认。
- **严格模式**：AI 拟执行的每条命令都需要用户明确批准。

平衡模式依赖命令风险判断逻辑：解析 Shell token，并识别管道、重定向、子命令、反引号和命令替换。写入、删除、移动、安装、重启、权限变更以及无法明确分类的操作会进入确认流程。

![ai-confirm.png](images3/ai-confirm.png)

自动模式确实降低了交互阻力，也把更多判断交给模型。Termark 支持 OpenAI 兼容接口，用户接入的模型能力和工具调用质量可能差异很大，因此自动模式不应被理解为产品对每条命令安全性的保证。无论使用哪档策略，生成的命令及其目标都应保持可检查。

## 内置 Agent

Termark 内置了一条 OpenAI 兼容的 Agent 路径，给"我想用自己挑的模型，但又不想自己搭一套工具链"的人用。

可以配置不同的 API Profile，OpenAI、DeepSeek、OpenRouter、Qwen、Kimi、Ollama 或自定义接口都行。每个 Profile 单独配置 API 地址、Key、模型列表、当前模型、reasoning 参数、最大重试次数和自定义 User-Agent。

![ai-profile1.png](images3/ai-profile1.png)
![ai-profile2.png](images3/ai-profile2.png)

我自己测试时偏向用响应快、成本可控的模型做高频终端辅助。会话 AI 的上下文比较克制：最近若干行终端输出、当前会话 ID、必要的系统提示词和用户问题。最近输出行数可以在设置中调整。全局 AI 则不会自动附带当前终端输出；它根据用户明确 mention 的主机或分组加载目标，适合跨资产工作。

这样刚执行完：

```bash
systemctl status nginx
```

然后问：

```text
帮我看一下为什么没启动
```

AI 就能直接结合刚才的输出来分析，不会反问一句"请提供错误日志"。

![ai-recent-output.png](images3/ai-recent-output.png)

日常解释日志、生成排查命令、看配置片段、搜索文件，这点上下文基本够用。

轻量模型当然有它的能力上限。所以内置 Agent 我没把定位拔得太高，它的角色是终端旁边一个能看现场、能有限执行命令的助手，不负责替你跑完整套运维流程。查磁盘、看端口、分析报错都合适；不经确认改生产配置，我并不鼓励。

---

## 外部 CLI：给你本地已有的 Agent 用

还有一类场景反过来。

有些人已经在本地终端里重度用 Codex、Claude Code 或 OpenCode，不愿意切到 Termark 的 AI 面板。问题是这些本地 Agent 默认拿不到用户的 SSH 资产，它不知道密码、私钥、跳板机配置，从安全角度看也不该知道。

Termark 在这里的处理是给一条外部 CLI。

设置页里点几下就能把 `termark` 命令装到 PATH，并且把 Termark skill 装到 Codex、Claude、OpenCode 的 skills 目录里。之后在本地 Agent 里就可以让它去用 termark：

```bash
termark assets list -q <keyword> --json
termark assets show <asset-id> --json
termark exec <asset-id> "<command>"
termark upload <asset-id> <local-path> <remote-path>
termark download <asset-id> <remote-path> <local-path>
termark sync <asset-id> <local-dir> <remote-dir>
```

复杂 PowerShell 命令可以通过 `termark exec <asset-id> --stdin` 从标准输入传入。当前 CLI 还提供主机和凭据记录的 JSON 增删改查命令；这些属于显式管理操作，不应与一次性远程命令混为一谈。

![ai-cli-settings.png](images3/ai-cli-settings.png)
![ai-cli-codex.jpg](images3/ai-cli-codex.jpg)
![ai-cli-claude.jpg](images3/ai-cli-claude.jpg)


外部 CLI 不直接持有凭证。它通过正在跑的 Termark 桌面端访问受控能力，凭证、跳板、连接细节这些都还留在 Termark 里。Agent 拿到的只是一个"对指定资产做点事"的入口。

外部 CLI 通过本机 HTTP API 与正在运行、且已启用外部 CLI 的 Termark 桌面端通信。`exec` 会使用已保存凭据建立临时 SSH 连接，执行一条命令后关闭；它不会附着到当前可见终端 Shell。长任务应在远端用 `tmux`、`nohup` 或 `systemd` 接住。上传、下载和 `sync` 支持文件夹；主机与凭据管理命令使用 JSON 输入输出。

它不是要做一个万能 remote agent，只是给已有的 Agent 加一个能安全访问服务器的入口。

---

## 两条路解决两类人

到这里，Termark 在 AI 这块其实给了两个入口。

一个是内置的 OpenAI 兼容 Agent。用户挑自己想用的模型，让 AI 在 SSH 终端旁边看现场、分析问题、执行受控命令，安全靠 Termark 的确认策略兜着。

另一个是外部 CLI。本地 Agent 工作流不变，只是多了一个能安全访问 Termark 资产的命令；凭证不交给 Agent，留在 Termark 这边就行。

我没想强迫用户只用其中一种。有人在乎接入门槛和模型选择，有人在乎已有工作流。两个入口都通过 Termark 使用已保存的资产与凭据，但执行路径并不相同：内置 AI 使用会话或全局 AI 工具，外部 CLI 的 `exec` 使用临时 SSH 连接；不能把它们描述成共享同一个终端会话或同一套审批流程。

## 哪些场景适合 AI SSH 助手

比较适合交给 AI 辅助的任务包括：解释最近的错误输出、生成只读排查命令、搜索配置、总结日志和给出下一步检查方向。涉及删除、写入、安装、权限变更或服务重启时，完整命令和目标服务器应该先对用户可见。

如果你正在评估这类工作流，可以查看 [Termark AI SSH 客户端](https://www.termark.app/zh-cn/#download)；关于本地凭据和同步数据的边界，可继续阅读 [SSH 客户端保存密码和私钥安全吗？](./ssh-credential-security)。

**查看受控 AI SSH 工作流：**<a href="https://www.termark.app/zh-cn/?utm_source=docs&utm_medium=blog&utm_campaign=ai_ssh_safety&utm_content=article_cta#download" data-umami-event="blog-cta-click" data-umami-event-campaign="ai_ssh_safety" data-umami-event-destination="ai-ssh-client">了解 Termark AI SSH 客户端</a>。
