---
title: SSH 连不上、卡住、超时？从网络到服务端 6 步排查
description: SSH 出现 Connection refused、Connection timed out 或认证卡住时，按报错归类、客户端探测、网络路径、sshd 服务端、认证阶段、连接保持 6 步定位，避免盲目重启路由或改配置。
date: 2026-09-04
updated: 2026-09-04
author: Termark Team
---

# SSH 连不上、卡住、超时？从网络到服务端 6 步排查

凌晨两点，你被告警叫醒，急着登服务器看负载。结果 SSH 卡住了——不是报错，是光标停在那里一动不动。你 Ctrl+C 重试，这次直接 `Connection timed out`。再试一次，变成了 `Permission denied (publickey)`。三种症状轮流出现，你开始怀疑是不是自己网络坏了，重启路由器、换手机热点、改端口，折腾半小时，服务器那边什么变化都没有。

这三种症状经常搅在一起，是因为它们各自指向不同的层次：`timed out` 多半在网络，`refused` 多半在服务端端口，`permission denied` 在认证，而「卡住不报错」则常常藏在服务端或客户端某个不起眼的选项里。SSH 连接是分阶段的——DNS 解析、TCP 三次握手、协议协商、身份认证、打开会话。卡在哪个阶段，答案就埋在哪个阶段。这篇文章给一条可以在任何机器上顺序执行的 6 步路径：先把「卡在哪」定位出来，再决定改什么。盲目的重启和改配置，只会把一次故障变成三次。

## 第 1 步：先把报错归类，确定卡在哪一层

报错的字面意思就是第一手线索。把客户端给出的信息分类，能少走一半弯路：

- `Connection refused`：TCP 包到达了目标，但目标端口没有人监听。方向指向服务端——sshd 没起、监听端口改了、或者防火墙用 REJECT 主动拒绝。
- `Connection timed out`：包发出去没有任何回应。方向指向网络路径——防火墙 DROP 静默丢弃、路由不通、IP 或端口写错、运营商屏蔽。
- `Connection reset by peer`：对方在握手过程中主动发送了 RST。常见于 fail2ban、TCP wrappers、负载均衡把这条连接踢掉。
- `No route to host`：路由层面就找不到主机，通常在本机路由表、VPN 隧道或网关配置。
- `Permission denied (publickey)` / `Permission denied, please try again`：TCP 和握手都通了，卡在认证。公钥没被接受、密码错、或者服务端只允许某种认证方式。
- 卡住不报错，光标一直不动：TCP 已经建立（或正在建立），但后续迟迟没有进展。常见的元凶是 DNS 反查、GSSAPI 协商、认证方法等待输入。

先别急着动手。同一台服务器，`refused` 和 `timed out` 的排查方向完全不同：前者你只需要看服务端端口，后者你要顺着网络逐跳查。把报错归对类，等于把「未知的断点」缩小成「某一层的断点」。

## 第 2 步：用 `ssh -vvv` 看它到底停在哪

`-vvv` 是 SSH 自带的探针。它会把连接过程每一步都打出来，你只需要看它停在最后一行：

```bash
ssh -vvv user@example.com
```

读输出时盯住几个关键行：

- `debug1: Connecting to example.com [1.2.3.4] port 22` 之后没有下文——TCP 握手没完成，回到第 3 步查网络。
- `debug1: Connection established` 已经出现，但后续长时间无输出——TCP 通了，卡在协议协商或认证，跳到第 4、5 步。
- 反复出现 `Authentications that can continue: publickey,password` 或 `Permission denied`——认证失败，见第 5 步。
- 出现 `Connection established` 之后要等很久才到认证——服务端在握手前做了耗时操作，典型是反向 DNS 查询或 GSSAPI。

同一个命令还能顺手把 DNS 和端口这两件事单独验证掉：

```bash
# DNS 是否解析、解析到哪个 IP
getent hosts example.com
dig +short example.com

# 22 端口是否可达，注意 refused 与 timed out 的区别
nc -vz -w 5 example.com 22
```

如果 DNS 解析特别慢，或者解析到了一个你已经废弃的旧 IP，问题可能根本不在 SSH。用 `ssh -o ConnectTimeout=10` 给连接阶段设一个明确的超时，避免默认值下「卡住不报错」被误判成服务端问题。排除了 DNS 和端口之后还卡，再往网络深处走。

## 第 3 步：顺网络路径逐跳排查

先确认自己是从哪台机器测的。「本机能连」不等于「生产机能连」：你在办公网用笔记本测通，不说明云服务器上的安全组放行了这条来源。

逐层确认：

```bash
# 目标 IP 是否可达（先测 ICMP，再测 TCP 22）
ping -c 3 1.2.3.4
nc -vz -w 5 1.2.3.4 22

# 如果是云主机，确认安全组入站规则有没有放行 22
# 如果中间有跳板，确认跳板到目标这一段通不通
ssh -J jump.example.com user@target.example.com
```

防火墙的 DROP 和 REJECT 会产生两种不同的症状，这本身就是线索：REJECT 通常表现为 `Connection refused` 或 `Connection reset`，DROP 表现为 `Connection timed out`。看到 `timed out` 时，优先怀疑防火墙静默丢弃或路由黑洞，而不是先怀疑 sshd。

两个容易被忽略、但造成大量「能 ping 通却 SSH 卡住」的情况：

- **MTU / 分片问题**：大包过不去，小包正常。ping 通是因为 ICMP 包小，SSH 协商阶段交换的大包被丢。用带 `do not fragment` 标志的探测确认：

```bash
ping -M do -s 1472 1.2.3.4
```

如果 1472 字节发不出去而 1400 字节正常，隧道或链路 MTU 偏小，调低接口 MTU 或修正 PMTUD。

- **运营商 / 网络策略屏蔽 22 端口**：部分移动网络、酒店或企业网对 22 端口做限制，表现为随机 `timed out`。如果确定是端口被封，换一个高位端口，或者走 VPN / SSH 隧道。

走隧道连接时，超时行为会和直连不同——隧道建立、保持与中断的边界，参考[端口转发配置](/zh/usage/port-forwarding)里关于本地/远程转发的说明，先确认隧道本身是否存活，再排查内层 SSH。

## 第 4 步：上服务器查 sshd 本身

如果网络这一层排查干净了，或者你怀疑问题在服务端，直接在目标机器上确认 sshd 的状态：

```bash
sudo systemctl status sshd --no-pager
sudo ss -lntp | grep sshd
```

重点核对四件事：

1. **sshd 是否在运行**：进程退出了自然没人接连接。
2. **监听在哪个端口、哪些地址**：`ss -lntp` 会显示 `*:22`、`127.0.0.1:22` 还是只监听 IPv6 的 `[::]:22`。端口改过、只监听本机回环、只监听某个网卡，都会造成外部 `refused` 或 `timed out`。
3. **配置是否与你以为的一致**：`/etc/ssh/sshd_config` 里的 `Port`、`ListenAddress`、`AllowUsers`、`DenyUsers`、`PasswordAuthentication`。改完要看的是 `sshd -T` 输出的生效值，而不是编辑前那个文件：

```bash
sudo sshd -T | grep -E '^(port|listenaddress|passwordauthentication|allowusers|maxstartups)'
```

4. **是不是被安全策略挡了**：fail2ban、denyhosts 这类工具会在多次失败后封 IP，症状正是 `Connection reset by peer`。查服务端日志：

```bash
sudo journalctl -u sshd --since '15 minutes ago' --no-pager
# Debian/Ubuntu 也可以看
sudo tail -n 100 /var/log/auth.log
```

日志里如果出现你的 IP 被 `Refused`、`banned`、`Disconnecting`，就去看 fail2ban 的 jail 而不是继续试密码。

还有一类「能连但被拒」的隐蔽原因：`MaxStartups`。它限制同一时间还没完成认证的连接数，超过后新连接直接返回 `ssh_exchange_identification: Connection closed by remote host`。被攻击或并发突发时，这个阈值会先耗尽。资源层面也别漏：内存打满导致 sshd fork 子进程失败，或文件描述符耗尽，都可能让连接在认证前就断掉——`free -h` 和 `sudo ss -s` 各看一眼。

## 第 5 步：认证阶段卡住或反复失败

TCP 通了、`Connection established` 也打出来了，却卡在认证——这一层的问题一半在配置，一半在等待。

**握手慢**的典型来源是服务端反向 DNS 查询。`UseDNS yes`（一些发行版默认值）会让 sshd 在认证前反查客户端 IP，DNS 服务器响应慢时，每次连接都白等几秒到几十秒：

```bash
sudo sshd -T | grep usedns
```

客户端侧的 `GSSAPIAuthentication` 也会拖慢连接——在没有 Kerberos 的环境里，客户端默认尝试 GSSAPI 协商，失败才回退。不想被它拖时间，在客户端 `~/.ssh/config` 里关掉：

```text
Host example.com
    GSSAPIAuthentication no
```

**认证失败**则要分开看：

- 密码方式被禁，而你只带了密码：`Permission denied, please try again` 多次后 `Permission denied (publickey)`。确认服务端 `PasswordAuthentication` 的值。
- 公钥没被接受：先看本地 agent 有没有加载对应的私钥，再看服务端那对文件的权限。

```bash
ssh-add -l
# 服务端：~/.ssh 应为 700，authorized_keys 应为 600
ls -ld ~/.ssh
ls -l ~/.ssh/authorized_keys
```

- 二次验证卡住：服务端配置了 OTP、键盘交互或 `AuthenticationMethods` 强制多因素时，客户端弹不出输入提示，或者提示出现但你的 token 不同步。这类交互认证的流程，可参考[自动 OTP 交互认证](/zh/usage/otp-interactive-auth)里对验证码输入时机的说明——它解决的是「验证码该在哪个环节填」的问题。

用 `ssh -v` 看服务端最后返回的 `Authentications that can continue`，它会明确告诉你还剩哪些认证方式可用。按它列的清单逐项满足，比反复盲试密码快得多。

## 第 6 步：连上之后掉线、卡死

连接能建立，也认证成功了，但用着用着断掉，或者终端突然卡死没反应——这已经脱离了「连不上」，进入「保不住」的范畴，但排查路径同样有章可循。

空闲断线的头号原因是 NAT 或防火墙的空闲连接回收：中间设备会在一段时间无流量后悄悄清掉这条连接，SSH 自己并不知道，直到你下一次敲键盘才发现已经断了。解决方式是让连接周期性地发心跳，客户端和服务端各有一套参数：

```text
# 客户端 ~/.ssh/config
Host *
    ServerAliveInterval 30
    ServerAliveCountMax 3
```

`ServerAliveInterval` 是客户端每隔多少秒主动探活，`ServerAliveCountMax` 是连续几次无响应才判定断开。服务端对应的是 `ClientAliveInterval` 和 `ClientAliveCountMax`。注意 `TCPKeepAlive` 和 `ServerAlive` 不是一回事：前者是 TCP 层的 keepalive，默认间隔很长（通常两小时），对「几十秒就被 NAT 回收」的场景几乎没用，别指望它救急。

终端卡死但连接还在，多半不是网络问题，而是远端进程把会话拖住了——比如输出刷屏、磁盘写满、某个命令在等一个永远不来的输入。这种「连接活着、交互死了」的情况，靠心跳救不回来，正确做法是让远程会话独立于这条 SSH 连接之外，用终端复用工具（tmux、screen）把会话挂在服务端，掉线或卡死后重连即可找回现场。

排查过程里，把命令、日志、配置检查集中在一个可复现的会话中会省很多事；用 Termark 连服务器时，终端和 SFTP 在同一工作台里，查看日志、拉配置文件不用来回切。它解决的是操作路径，不会替你判断断点在哪一层。

## 一份按顺序执行的排查清单

```bash
# 1. 归类报错：refused / timed out / reset / permission denied / 卡住
ssh -vvv user@example.com

# 2. 单独验证 DNS 与端口
getent hosts example.com
nc -vz -w 5 example.com 22

# 3. 网络路径：ping、MTU、跳板
ping -M do -s 1472 1.2.3.4

# 4. 服务端 sshd 状态与生效配置
sudo systemctl status sshd --no-pager
sudo ss -lntp | grep sshd
sudo sshd -T | grep -E '^(port|listenaddress|passwordauthentication|maxstartups|usedns)'

# 5. 服务端日志，确认是否被封或握手卡顿
sudo journalctl -u sshd --since '15 minutes ago' --no-pager

# 6. 认证与保活
ssh-add -l
# 客户端配置加 ServerAliveInterval / ServerAliveCountMax
```

顺序本身就是答案的一部分：先归类报错，再用 `-vvv` 定位到具体阶段，然后网络、服务端、认证、保活逐层推进。每次只改一件事，改完用同一条 `ssh -vvv` 命令复测，记录前后差异。SSH 连不上从来不是一种病，而是一连串「哪个环节没响应」的叠加——找到那一个环节，比把它当成一个整体去重启要有用得多。

## 参考资料

- [OpenSSH 客户端手册：ssh_config 中的连接与保活选项](https://man.openbsd.org/ssh_config)
- [OpenSSH 服务端手册：sshd_config 中的认证与限制](https://man.openbsd.org/sshd_config)
- [OpenSSH 手册：ssh 命令的详细输出选项](https://man.openbsd.org/ssh)
- [Termark 端口转发配置](/zh/usage/port-forwarding)
- [Termark 自动 OTP 交互认证](/zh/usage/otp-interactive-auth)
