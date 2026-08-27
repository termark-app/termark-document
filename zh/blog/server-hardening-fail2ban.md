---
title: 服务器总被暴力破解？改端口、禁密码、fail2ban 5 步加固
description: SSH 每天被上万次暴力破解？仅改端口治标不治本。本文用 5 步完成加固：改非标准端口、禁用密码仅保留密钥、fail2ban 自动封禁、可验证的 sshd 加固流程与日志告警闭环，附可复制配置与排错命令。
date: 2026-08-27
updated: 2026-08-27
author: Termark Team
---

# 服务器总被暴力破解？改端口、禁密码、fail2ban 5 步加固

凌晨 2:17，手机连震三下。不是业务告警，是你那台跑在云上的小服务器：`sshd: Failed password for root from 43.154.x.x port 48271`，一分钟刷了 40 多行，紧接着又换了两个新 IP 继续撞。早上再看 `/var/log/auth.log`，昨晚累计了 18000 多次失败登录，来源 IP 遍布全球，字典里 `admin`、`ubuntu`、`postgres`、`oracle`、`root` 轮番上阵，`journalctl` 里全是 `Disconnected from authenticating user`。

如果你第一次遇到，大概率会想：先把 22 端口改掉，眼不见心不烦。改完确实清净了几天，日志从每小时上千行降到几十行，然后某天凌晨又开始出现新的扫描——只不过这次是针对你新开的那个“隐蔽”端口。这就是大多数人加固 SSH 的起点，也是误区最多的地方：以为改端口就是加固，做完就以为万事大吉。

本文不讲空话，给你一条在 Ubuntu/Debian 生产机上可直接执行的 5 步路径：从端口、认证方式、自动封禁、配置验证到日志闭环，每一步都可回滚、可验证。操作全程通过 SSH 完成，用 Termark 这类带会话保持和 SFTP 的终端会更省心，但不依赖任何特定工具；所有命令都可复制执行。

## 为什么“只改端口”不够

改端口的本质是降低噪音，不是提高安全性。

全网扫描器默认先扫 22，但稍微像样的扫描器都会做全端口探测或从 Shodan、Censys、ZoomEye 拉历史端口记录。你把 `Port 22` 改成 `2222` 或 `48222`，能把 90% 的脚本小子挡在日志之外，告警也少了，却挡不住定向扫描和全端口爆破。实测把端口改到 5 万以上，依然能在 Shodan 上被标记为 `ssh`，新一轮扫描几天内就会跟上来。

更关键的是：只要 `PasswordAuthentication yes` 还开着、允许 `root` 直接登录，攻击者一旦猜中端口，就可以用无限次的密码尝试去撞。弱口令、泄露过的密码、甚至云厂商初始化时设过的通用密码，都在字典里。你看到的“被扫几万次”不是针对你，而是全网无差别爆破——改端口只是让你看不见，不代表攻击停止。

真正的安全来自两件事：**让密码不可撞**（禁用密码、只用密钥），以及**让撞库有代价**（失败几次就封 IP）。改端口只是让这两件事的日志更干净、告警更可信、资源消耗更低。下面 5 步按顺序做，别跳步，也别只做第一步就停。

## 第 1 步：改端口，但别把自己锁在门外

选一个 1024 以上的非标准端口，避开 2222、22222 这类“次热门”端口，也避开已被其他服务占用的端口。端口本身没有“更安全”的说法，选一个你记得住、团队好同步、且不在常用服务列表里的即可。

```bash
# 1. 确认新端口未被占用
sudo ss -lntp | grep -E ':22 |:2222 |:48222'
# 选一个空闲端口，例如 48222
sudo semanage port -a -t ssh_port_t -p tcp 48222  # 仅 SELinux 系统（CentOS/RHEL）需要

# 2. 修改 sshd 配置（不要直接改原文件，先加 drop-in）
sudo mkdir -p /etc/ssh/sshd_config.d
cat <<'EOF' | sudo tee /etc/ssh/sshd_config.d/99-custom-port.conf
Port 48222
EOF

# 3. 放行防火墙与安全组
sudo ufw allow 48222/tcp
# 或 firewalld
# sudo firewall-cmd --permanent --add-port=48222/tcp && sudo firewall-cmd --reload
# 云厂商安全组/ACL 也要同步放行，否则你会被自己挡住

# 4. 语法检查并重载（不要 restart，先 reload）
sudo sshd -T | grep -i port
sudo systemctl reload sshd
# 5. 新开一个终端窗口，用新端口测试连通性，旧会话保持不动
ssh -p 48222 user@your-server -v
```

**注意事项：**

1.  **不要关闭 22 直到验证完成。** 建议过渡期同时监听 `Port 22` 和 `Port 48222`，确认新端口可登录后再移除 22。否则一次手误就会失联——这是新人最常见的翻车现场。
2.  **客户端要记住端口。** `~/.ssh/config` 里固定下来，避免每次手输，也避免脚本和 CI 环境因端口不一致而失败：

    ```ssh-config
    Host myprod
      HostName your-server.example.com
      Port 48222
      User deploy
      IdentityFile ~/.ssh/id_ed25519
    ```
3.  **防火墙要双向放行。** 本机 `ufw`/`iptables` 只是第一层，阿里云/腾讯云/ AWS 的安全组是第二层。只放行一层，另一层仍会把你挡在外面；改端口后第一时间用新端口做一次完整登录，而不是只 `telnet` 看端口通不通。
4.  **Termark 等图形化终端**可以直接在主机配置里改端口并做连接测试，比命令行反复 `ssh -p` 更不容易输错；关键是任何工具都要保留一个已连上的会话作为“救生舱”，直到新端口验证通过再关闭旧会话。

## 第 2 步：禁密码、禁 root，只认密钥

这是性价比最高的加固。密码再复杂也扛不住泄露、复用和社工，密钥对则把认证从“记得住”变成“拿得出”——私钥在你手里，不在网络上裸奔。即便攻击者扫到端口、知道用户名，没有私钥也只能得到 `Permission denied (publickey)`。

先确保你已有一对可用的密钥，并且**当前账号已能用密钥登录**，再动服务端配置。顺序不能反，否则就是主动把自己锁死。

```bash
# 本地生成密钥（已有可跳过，推荐 ed25519，短、快、安全性好）
ssh-keygen -t ed25519 -C "deploy@myprod"

# 上传公钥到服务器（会追加到 ~/.ssh/authorized_keys）
ssh-copy-id -p 48222 deploy@your-server
# 或手动追加
cat ~/.ssh/id_ed25519.pub | ssh -p 48222 deploy@your-server 'mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'

# 验证密钥登录已生效（应无需输入密码）
ssh -p 48222 deploy@your-server 'echo ok'
```

确认无误后，再禁用密码与 root 登录：

```bash
cat <<'EOF' | sudo tee /etc/ssh/sshd_config.d/99-hardening.conf
# 禁用密码与键盘交互认证
PasswordAuthentication no
ChallengeResponseAuthentication no
UsePAM no
# 禁止 root 直接登录（需要 root 时用普通用户 sudo -i）
PermitRootLogin no
# 可选：禁止空密码、限制允许登录的用户/组
PermitEmptyPasswords no
AllowUsers deploy ops
# 保持密钥认证开启
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
EOF

# 检查合并后的最终生效配置
sudo sshd -T | grep -E 'passwordauthentication|permitrootlogin|pubkeyauthentication|allowusers|port'

# 重载生效
sudo systemctl reload sshd
```

**回滚预案：** 如果你不小心把自己锁住，且云厂商提供 VNC/串行控制台，进去把 `PasswordAuthentication` 临时改回 `yes` 并 `systemctl reload sshd` 即可。没有控制台的机器，务必在改之前确保至少有一个可用会话未断开，且已验证密钥登录。团队协作时，建议把 `AllowUsers` 写成明确名单，避免新人账号默认就能 SSH。

> 经验：`PasswordAuthentication` 与 `ChallengeResponseAuthentication` 在不同发行版的默认值不同，`UsePAM no` 会同时影响键盘交互式登录。改完务必用 `sshd -T` 看最终值，而不是只看你写的那几行；`sshd -T` 输出的是所有配置文件合并后的结果，最可信。

## 第 3 步：用 fail2ban 让暴力破解有代价

密钥已经让“撞对密码”几乎不可能，fail2ban 则让“一直撞”的行为付出被封 IP 的代价，并大幅降低日志噪音与资源消耗。它的原理很简单：监控 `auth.log` 或 `journal`，对匹配到 `Failed password` 的 IP 计数，超过阈值就通过 `iptables` 封禁一段时间。

```bash
# 安装（Debian/Ubuntu）
sudo apt update && sudo apt install -y fail2ban

# 不要直接改 jail.conf，用 jail.local 覆盖，便于升级时不冲突
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local
```

推荐的 `jail.local` 关键段（按你的端口与策略调整）：

```ini
[DEFAULT]
# 封禁时长：1 小时起步，重复触发可递增（见 recidive）
bantime  = 1h
# 检测窗口：10 分钟内
findtime = 10m
# 允许失败次数：5 次就封
maxretry = 5
# 封禁动作：iptables + 写入日志
banaction = iptables-multiport
# 忽略白名单：你的办公 IP、跳板机、自家监控
ignoreip = 127.0.0.1/8 ::1 203.0.113.10 198.51.100.0/24

[sshd]
enabled  = true
port     = 48222
filter   = sshd
logpath  = /var/log/auth.log
# systemd 系统也可用 journal
backend  = systemd
maxretry = 5
bantime  = 1h

# 对反复解封又来撞的 IP，加重处罚
[recidive]
enabled  = true
logpath  = /var/log/fail2ban.log
banaction = iptables-allports
bantime  = 1w
findtime = 1d
maxretry = 3
```

启用并验证：

```bash
sudo systemctl enable --now fail2ban
sudo fail2ban-client status
sudo fail2ban-client status sshd
sudo fail2ban-client get sshd bantime
# 查看是否已正确读取新端口
sudo fail2ban-client get sshd port
# 看一次封禁日志
sudo tail -n 30 /var/log/fail2ban.log
```

**调优建议：**

- `maxretry` 不要设为 1 或 2，误伤率会飙升；5 是兼顾体验与防护的常用值，配合 `findtime 10m` 刚好卡住自动化脚本。
- `ignoreip` 必须包含你的固定出口 IP、办公网段和跳板机，否则一次输错密钥或脚本重试就把自己封了，且很难第一时间发现。
- 如果你用非 `auth.log` 而是 `journal`，把 `backend = systemd` 显式写上，否则部分系统会因日志路径不对而“看似运行但一条也不封”，`fail2ban-regex` 可以帮你验证正则是否命中。
- 云上建议把 `banaction` 保持为 `iptables-multiport`，别一上来就用 `route` 或云 API 封禁，容易与安全组规则冲突；`recidive` 监狱专治“封了又来”的顽固 IP，直接封一周更省心。

## 第 4 步：SSH 加固细节与可验证的发布流程

前两步改了端口和认证，这一层把容易被遗漏的细节补齐，并建立一个不会把自己锁死的发布习惯。很多加固文章只给配置不给验证流程，结果一改就失联。

```bash
cat <<'EOF' | sudo tee /etc/ssh/sshd_config.d/99-extra.conf
# 协议与算法：禁用过时算法（按你的 OpenSSH 版本取舍）
Protocol 2
# 登录宽限与并发控制
LoginGraceTime 30s
MaxAuthTries 3
MaxSessions 3
MaxStartups 3:50:10
# 空闲超时：5 分钟无操作自动断开（可选，按团队习惯）
ClientAliveInterval 300
ClientAliveCountMax 2
# 禁用 X11 与隧道（不需要就关掉，减少攻击面）
X11Forwarding no
AllowTcpForwarding no
PermitTunnel no
# 更少信息泄露
Banner /etc/issue.net
EOF
```

发布流程请固定为三件套，缺一不可：

```bash
# 1. 语法与有效配置检查（sshd -T 会合并所有 drop-in 后输出最终值）
sudo sshd -t && echo "syntax ok"
sudo sshd -T | grep -E 'port|passwordauthentication|permitrootlogin|maxauthtries|clientaliveinterval'

# 2. 重载而非重启
sudo systemctl reload sshd
# reload 失败会自动保持旧进程运行，比 restart 安全得多

# 3. 新开窗口验证，旧窗口不退出
ssh -p 48222 deploy@your-server 'whoami; echo connected'
# 再试一次密码登录应被拒绝（预期失败）
ssh -p 48222 -o PreferredAuthentications=password -o PubkeyAuthentication=no deploy@your-server
```

如果 `sshd -T` 报错，说明有指令拼写或版本不兼容，先修正再 reload。有一个常见坑：`ChallengeResponseAuthentication` 在新版 OpenSSH 已被 `KbdInteractiveAuthentication` 取代，旧指令仍兼容但会告警，看到告警就改成新名字；`Protocol 2` 在新版也已默认且无需显式声明，但保留无害。

用 Termark 管理多台机器时，建议把这三条命令做成批量执行的模板，对所有主机先做 `sshd -t` 巡检，通过后再统一 reload，比一台台手工敲更不容易遗漏；SFTP 则可用来复核 `/etc/ssh/sshd_config.d/` 下的多个 drop-in 是否都已同步。

## 第 5 步：日志、告警与误封处理闭环

加固不是改完就结束，要让“被打”和“被封”都看得见，并能在误封时 30 秒内自救。否则要么封了不知道、要么误封了半天才发现。

**看日志：**

```bash
# 实时看 SSH 登录与 fail2ban 动作
sudo tail -F /var/log/auth.log | grep -E 'sshd.*Failed|sshd.*Accepted|sshd.*Disconnected'
sudo tail -F /var/log/fail2ban.log

# systemd 体系
sudo journalctl -u sshd -f
sudo journalctl -u fail2ban -f --since '1 hour ago'

# 统计近 1 小时失败来源 Top 10
sudo grep 'Failed password' /var/log/auth.log | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | sort | uniq -c | sort -nr | head

# 看哪些 IP 已被封、封了多久
sudo fail2ban-client status sshd
sudo iptables -L f2b-sshd --line-numbers -n
```

**查封禁与解封：**

```bash
# 查看总体与 sshd 监狱状态
sudo fail2ban-client status
sudo fail2ban-client status sshd
# 查看被封 IP 的 iptables 规则
sudo iptables -L f2b-sshd --line-numbers -n

# 误封时解封单个 IP（把 IP 换成实际被封的）
sudo fail2ban-client set sshd unbanip 203.0.113.45
# 解封后建议把该 IP 加入 ignoreip 并重载
# echo 'ignoreip = 127.0.0.1/8 203.0.113.45' | sudo tee -a /etc/fail2ban/jail.local && sudo systemctl reload fail2ban

# 手动封禁测试（验证链路是否生效）
sudo fail2ban-client set sshd banip 198.51.100.99
sudo fail2ban-client status sshd | grep 198.51.100.99
sudo fail2ban-client set sshd unbanip 198.51.100.99
```

**加告警：** fail2ban 自带 `action_mw`、`action_mwl` 等邮件告警，或通过 webhook 推送到企业微信、飞书、Telegram。最轻量的做法是让日志接入你已有的监控（如 Grafana Loki、ELK、云日志服务），对 `fail2ban.actions.* Ban` 做阈值告警；不要为 SSH 单独造一套告警系统，否则告警一多就会被忽略。建议先从“每小時封禁数突增 3 倍”这类异常告警做起，比每封一个 IP 就告警要安静得多。

**误封自救清单：**

1.  被封后不要反复重试，会触发 `recidive` 导致封更久，从 1 小时变成 1 周。
2.  换一个白名单 IP 登录，执行 `unbanip`，这是最快的自救路径。
3.  若彻底失联，走云控制台的 VNC/串口执行解封，或让同事从白名单网段操作。
4.  事后把办公网段写入 `ignoreip`，并把 `maxretry`/`findtime` 调得更宽容一点，避免脚本误触。
5.  定期 `sudo logrotate -f /etc/logrotate.d/fail2ban` 检查日志轮转，避免 `auth.log` 被轮转后 fail2ban 找不到新文件。

## 结语：把“被扫”变成“可控”

暴力破解不会消失，但可以被控制到“看得见、拦得住、误伤可恢复”的水平。改端口降低噪音、密钥让密码不可撞、fail2ban 让撞库有代价、最后用日志和解封能力把闭环封上。这四层缺一不可，顺序也不能乱——跳过密钥只靠封禁，遇到慢速低频爆破依然可能被撞；只改端口不做封禁，日志迟早会被刷爆。

下次再收到凌晨告警，你看到的应该是 `fail2ban` 的封禁记录，而不是 18000 行 `Failed password`。如果还想更进一步，再考虑：用跳板机收敛入口、用 WireGuard/Tailscale 把 SSH 藏进内网、或在安全组层面只放行跳板与办公网，让 SSH 根本不对公网暴露。

### 上线前检查清单（复制即用）

```bash
# 1. 端口与防火墙
sudo sshd -T | grep port
sudo ss -lntp | grep sshd
sudo ufw status | grep 48222

# 2. 认证方式
sudo sshd -T | grep -E 'passwordauthentication|pubkeyauthentication|permitrootlogin'
ssh -p 48222 deploy@your-server 'echo key-auth ok'
ssh -p 48222 -o PreferredAuthentications=password -o PubkeyAuthentication=no deploy@your-server  # 应被拒绝

# 3. fail2ban
sudo systemctl is-active fail2ban
sudo fail2ban-client status sshd
sudo fail2ban-client get sshd maxretry
sudo fail2ban-client get sshd bantime

# 4. 日志与自救
sudo grep -c 'Failed password' /var/log/auth.log
sudo tail -n 20 /var/log/fail2ban.log
sudo fail2ban-client status sshd | grep -i 'banned'
```

按这个清单走一遍，截图或保存输出，下次做等保自查或团队交接都能直接复用。工具只是提高效率，判断和验证仍在你手上——这也是 Termark 这类终端工具的定位：把连接、密钥、批量执行和文件查看做得顺手，让你把精力留在决策本身。

## 参考资料

- [OpenSSH sshd_config 官方手册](https://man.openbsd.org/sshd_config)
- [OpenSSH 安全加固指南（ssh-audit）](https://www.ssh-audit.com/hardening_guides.html)
- [fail2ban 官方文档 - jail 配置与常用命令](https://fail2ban.readthedocs.io/en/stable/)
- [fail2ban Filters 与 Actions 列表](https://github.com/fail2ban/fail2ban/wiki)
- [Ubuntu Server Guide - OpenSSH](https://ubuntu.com/server/docs/service-openssh)
- [Termark 数据存储与运维相关使用文档](/zh/usage/data-storage-path)
