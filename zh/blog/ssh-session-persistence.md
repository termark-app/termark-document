---
title: SSH 断开后，程序还在跑吗？nohup、tmux、systemd 的区别
description: SSH 断开后程序是否继续运行，取决于终端、Shell 会话和管理方式。本文解释 nohup、tmux、systemd 的职责、适用场景和断线重连后的检查方法。
date: 2026-08-20
updated: 2026-08-20
author: Termark Team
---

# SSH 断开后，程序还在跑吗？

很多人都遇到过这种情况：在服务器上跑了个脚本，SSH 窗口一关，心里就开始打鼓——这东西是不是已经没了？

答案没那么简单，也不是“服务器还开着就没事”这么粗暴。真正决定结果的，是这个程序有没有还依赖着已经关闭的终端和 Shell 会话，以及它有没有交给更合适的工具去管。三个常见的候选是 `nohup`、`tmux`、`systemd`，但它们解决的根本不是同一个问题——`nohup` 处理的是挂断信号和输出去向，`tmux` 给你一个能随时接回的终端会话，`systemd` 管的是服务的整个生命周期。把这三者当成同一类“保活咒语”混着用，很容易在 SSH 断开之后得到一个哭笑不得的结果：进程确实还活着，但任务已经彻底失控，日志找不到，退出状态也没人知道。

先给个粗略的选择方向，后面再展开细节：

| 场景 | 更合适的工具 |
| --- | --- |
| 跑一次性命令，不需要再接回交互界面 | `nohup`，或者干脆用任务队列 |
| 需要随时断开、随时接回同一个终端 | `tmux` |
| 长期运行的服务，要求开机自启、失败重启、有日志可查 | `systemd` |
| 构建、迁移、批处理这类一次性长任务 | 大多数时候是 `tmux`；只有完全无人值守时才考虑任务管理器 |

## 一次 SSH 登录里，其实叠了好几层东西

SSH 连接、终端、Shell、进程，这几个词经常被混着说，但它们其实是分开的几层：

```text
本地 SSH 客户端
        │
        │ 加密连接
        ▼
sshd ── 登录 Shell ── 终端/PTY ── 你的程序
```

OpenSSH 的 `ssh` 命令负责连上远端的 `sshd`，如果请求了伪终端，就会申请一个 PTY，在里面跑 Shell 或指定的命令，标准输入输出通过加密通道转发回来。[1] 你敲的每条命令，通常都是由这个登录 Shell 创建子进程，再把子进程接到终端的标准输入输出上。

所以下面这几件事其实是可以分开判断的：SSH 连接断没断、PTY 关没关、登录 Shell 退没退出、具体那个进程还在不在跑，以及如果是被服务管理器管着的服务，它现在处于什么状态。SSH 断开不代表内核会立刻把所有子进程杀光，但也不能反过来说 SSH 一断，程序就一定能继续正常工作——这取决于程序怎么处理信号、要不要终端，以及父进程和会话又是怎么被清理的。

## 为什么有些程序一断开就退出了

交互式 Shell 结束的时候，挂在它下面的进程往往会收到一个 `SIGHUP`（挂断信号）。程序对这个信号的反应因人而异：可以什么都不做直接退出，可以捕获之后自己处理，也可以压根不依赖这个终端所以毫无影响。[5]

就算程序没有因为 `SIGHUP` 立刻退出，终端一关也常常会牵出别的麻烦：程序还在往一个已经不存在的终端写东西；程序卡在等待标准输入，结果输入端没了直接报错；作业控制的父子关系断掉；日志本来就只打在终端上，现在也没地方看了；任务其实已经跑完，却没留下一个明确的退出状态。

所以“SSH 断开后进程还在吗”其实不是最该问的问题。更实际的问法是：这个任务除了这次 SSH 连接之外，还有没有自己独立的输入输出、生命周期和结果记录？

## `nohup`：让命令不再怕挂断信号

`nohup` 这个名字就是 “no hangup” 的缩写。它让命令忽略挂断信号；如果标准输出这时候还连着终端，GNU 版的 `nohup` 会把输出追加写到 `nohup.out`，标准错误也会做类似处理。[2]

```bash
nohup ./backup.sh > backup.log 2>&1 &
pid=$!
printf 'pid=%s\n' "$pid"
```

这条命令做了三件不同的事：`nohup` 让脚本不理会挂断信号，`> backup.log 2>&1` 把标准输出和错误都写进日志文件，末尾的 `&` 则是让当前 Shell 不等它跑完就返回。重新连上服务器之后，可以这样检查：

```bash
ps -p "$pid" -o pid=,stat=,etime=,cmd=
tail -n 50 backup.log
```

但 `nohup` 说到底不是一个完整的服务管理器。它不会告诉你任务到底成不成功，崩溃了也不会帮你重启，更不会给你一个能重新接回去的交互终端。PID 还在，不代表任务一切正常——它可能卡死了、反复报错，也可能早就跑完了只是没人记录退出状态。如果任务需要交互、需要实时输入，或者你希望回来后还能接着用同一个终端，`nohup` 通常不是趁手的选择。

## `tmux`：把终端会话从 SSH 连接里剥离出来

`tmux` 是一个终端复用器，它会在服务器上开一个独立的会话，在里面跑 Shell。SSH 客户端只是接入这个会话的一个终端而已——就算 SSH 断了，这个会话依然留在服务器上，随时可以重新接进去。[3]

```bash
tmux new -s deploy
cd /srv/example
./deploy.sh
```

想暂时离开又不结束会话，按 `Ctrl-b` 再按 `d` 就行。重新连上 SSH 后：

```bash
tmux ls
tmux attach -t deploy
```

编译部署要盯着实时输出、数据迁移过程中可能得手动确认、临时起个开发服务器、或者只是网络不稳但任务还得继续跑——这些场景用 `tmux` 都挺合适，核心原因是它能让当前的 Shell 状态、工作目录和正在跑的前台程序都留在原地。不过要说清楚，`tmux` 解决的问题始终是“会话保留”，不是“程序保证不出错”。程序自己该崩还是会崩，该因为业务逻辑退出还是会退出，重新接回去之后，输出和退出状态还是得自己看：

```bash
tmux ls
ps -ef --forest
```

## `systemd`：把长期服务的生命周期管起来

Web 服务、后台 worker、消息消费者这类要一直跑着的程序，更适合交给 `systemd`。它用 service unit 描述一个程序怎么启动、怎么停止、失败了要不要重启，以及在什么条件下运行。[4]

```ini
[Unit]
Description=Example worker
After=network-online.target

[Service]
Type=simple
WorkingDirectory=/srv/example
ExecStart=/srv/example/bin/worker
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

存成 `/etc/systemd/system/example-worker.service` 之后：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now example-worker.service
systemctl status example-worker.service
journalctl -u example-worker.service -f
```

`systemd` 之所以适合长期服务，是因为它把一堆原本靠人记的东西固定了下来：谁来启动、工作目录和启动命令是什么、失败了重不重启、日志去哪查、开不开机自启、现在到底是什么状态、上一次失败的原因是什么。这跟 `tmux` 要解决的问题完全不是一回事——正常不会有人把生产环境的 Web 服务塞进自己的 `tmux` 窗口里，也不会指望 `nohup` 替代失败重启、依赖管理和权限配置这些事情。

## 把三者放在一起看

| 能力 | `nohup` | `tmux` | `systemd` |
| --- | --- | --- | --- |
| SSH 断开后继续运行 | 一般可以 | 可以 | 可以 |
| 能重新接回原来的交互终端 | 不行 | 可以 | 不适用 |
| 实时输出去哪了 | 重定向到文件 | 留在会话里 | 走 journal |
| 失败自动重启 | 不管 | 不管 | 可配置 |
| 开机自启 | 不管 | 不管 | 可配置 |
| 查状态的方式 | 自己查 PID、翻日志 | 看会话和进程 | `systemctl status` |
| 适不适合长期服务 | 不建议单独用 | 不建议单独用 | 适合 |
| 适不适合临时交互任务 | 一般 | 适合 | 通常不适合 |

能在 SSH 断开后继续跑，和适合放到生产环境里跑，是两码事。一个命令暂时脱离了当前连接不代表什么都好了——可观测、可恢复、可审计的服务生命周期，是另一个层次的问题。

## 断线重连之后，到底该看什么

重新连上服务器，别光跑一句 `ps` 看进程在不在就完事了。按任务类型分别看：

```bash
# 临时任务
ps -ef | grep '[j]ob.sh'
tail -n 100 job.log

# tmux 任务
tmux ls
tmux attach -t maintenance

# systemd 服务
systemctl is-active example-worker.service
systemctl status example-worker.service
journalctl -u example-worker.service --since '30 minutes ago'
```

顺带确认一下：进程是不是还在跑、CPU 内存磁盘有没有异常、日志是不是还在正常增长、任务到底跑完没有、跑完之后有没有留下能验证的结果、中途有没有发生过重启或者重复执行。“进程还活着”只是清单里的一项，不是任务成功的证明。

## 几个常被误解的说法

**加了 `&` 命令就不会因为 SSH 断开而退出？**不一定，`&` 只是让 Shell 不等前台命令跑完就返回，跟挂断信号、标准输入输出、服务重启完全没关系。

**用了 `nohup` 是不是就能“恢复现场”？**也不行，`nohup` 解决的是命令对挂断信号的依赖，顺带处理一下终端输出，它从来没打算保留一个可以重新接入的交互终端。

**`tmux` 里的程序是不是就永远不会退出？**当然会，程序照样可能崩溃、主动退出，或者被 OOM killer 干掉，`tmux` 唯一保证的是这个会话本身可以被重新接进去。

**`systemd` 是不是只用来配开机启动？**远不止，它同时管着服务状态、停止方式、失败重启、依赖关系和日志集成，开机自启只是其中一个选项而已。

**看到 PID 存在就说明任务成功了？**不能这么下结论，得结合退出状态、日志、输出文件、服务状态和实际的业务结果一起判断。

## 写在最后

SSH 连接只是访问服务器的一条通道，它本身管不了任务的生命周期。如果只是担心网络说断就断，不妨先问自己几个问题：这个任务需不需要交互？回来以后要不要接着看？该不该自动重启？需不需要开机自启和统一日志？想清楚这几点，往往比纠结“用哪条保活命令”更能决定该怎么做。

本文作者是 Termark 开发者。至于像 [Termark](https://www.termark.app/zh-cn/) 这样的 SSH/SFTP 客户端，它不是要取代 `tmux`、`systemd` 或者任务队列——它能做的是让你连上服务器，然后用服务器上这些工具去管好任务：通过 SSH 连接目标主机，在终端里创建或重新接入 `tmux` 会话，查看日志、进程和 `systemd` 状态，需要的时候通过 SFTP 传脚本、下日志，断开之后再连回来接着看结果。客户端负责远程访问，任务生命周期还是交给服务器上的这些工具——分清楚这条边界，出问题的时候才知道该查连接、查会话，还是查服务配置。

## 参考资料

[1] [OpenSSH ssh 手册](https://man7.org/linux/man-pages/man1/ssh.1.html)

[2] [GNU Coreutils nohup](https://www.gnu.org/software/coreutils/manual/html_node/nohup-invocation.html)

[3] [tmux 手册](https://man7.org/linux/man-pages/man1/tmux.1.html)

[4] [systemd.service 手册](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html)

[5] [GNU Bash Signals](https://www.gnu.org/software/bash/manual/html_node/Signals.html)
