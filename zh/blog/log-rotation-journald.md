---
title: 日志又把磁盘写爆了？journald 与 logrotate 正确姿势
description: journald 日志无限增长、/var/log 写满磁盘怎么处理？用 journalctl --disk-usage 定位、--vacuum 清理，再配置 SystemMaxUse 与 logrotate 轮转根治，附可复制的命令与配置模板。
date: 2026-09-01
updated: 2026-09-01
author: Termark Team
---

# 日志又把磁盘写爆了？journald 与 logrotate 正确姿势

磁盘被日志写满这件事，几乎没有哪个运维没经历过。它不像业务数据那样有明确的上限，也不像数据库那样有人盯着，只是安静地一行行写下去，直到 `df -h` 里 `/var/log` 占掉十几个 G、journald 的二进制日志在 `/var/log/journal` 里悄悄膨胀，最后服务开始写日志失败、报错连篇、系统出现各种说不清的怪问题。

这篇文章分三步：先定位到底是 journald 还是文本日志在吃空间，再安全清理腾出空间，最后把上限配好，让日志自己管住自己。

## 先定位：日志到底占了多少、谁在写

Linux 上的日志分两大类，排查路径完全不同：

- **journald 的二进制日志**：systemd 服务默认把 stdout/stderr 写进 journal（`StandardOutput=journal`），存在 `/var/log/journal`（持久化）或 `/run/log/journal`（易失，重启即清）。它不是纯文本，`du` 单个文件看不出名堂，得用 `journalctl` 查。
- **传统文本日志**：nginx、MySQL、各种应用自己写进 `/var/log/` 的 `.log` 文件，这类靠 `logrotate` 轮转。

先跑这几条，把现状摸清楚：

```bash
df -h /var/log

journalctl --disk-usage
# Journals take 3.4G on disk.

sudo du -sh /var/log/* 2>/dev/null | sort -rh | head -10
sudo du -sh /var/log/journal 2>/dev/null
```

如果 `journalctl --disk-usage` 的数字和 `df -h` 对得上，问题基本出在 journald；如果是 `/var/log/nginx` 这种目录占的大头，那就是文本日志没轮转。两种情况的解法不一样，别混着来。远程排查时，用 [Termark](https://www.termark.app/zh-cn/?utm_source=docs&utm_medium=blog&utm_campaign=log_rotation_journald) 这类 SSH 客户端跑这些命令、需要时把大日志文件拉回本地看也很方便。

## journald：二进制日志也要有上限

很多人以为 systemd 会自己管好 journal 的大小，其实默认并不严格：`SystemMaxUse` 默认是所在文件系统大小的 10%（上限 4G），`SystemKeepFree` 默认保留 15%（上限 4G）。在磁盘本来就紧张的小服务器上，10% 可能就是几个 G，足够把分区逼到危险线。

### 先止血：vacuum 只删旧的不动新的

`--vacuum` 系列命令按大小、时间或文件数清理归档的旧日志，正在写入的活动文件不受影响，安全：

```bash
sudo journalctl --vacuum-size=200M   # 把总量压到 200M
sudo journalctl --vacuum-time=2weeks # 只保留最近两周
sudo journalctl --vacuum-files=5     # 只保留 5 个日志文件
journalctl --disk-usage
```

空间立刻回来，服务也无需重启。

### 再断根：journald.conf 一劳永逸

止血只能撑到下一次。把上限写进 `/etc/systemd/journald.conf`，让 journal 从今以后自己约束自己：

```ini
[Journal]
SystemMaxUse=500M
SystemKeepFree=1G
SystemMaxFileSize=50M
MaxRetentionSec=2week
MaxFileSec=1week
```

```bash
sudo systemctl restart systemd-journald
```

各参数含义：

- `SystemMaxUse=`：journal 占用的磁盘上限，超过后自动清掉最旧的；
- `SystemKeepFree=`：给文件系统保留的可用空间，优先级高于 `SystemMaxUse`；
- `SystemMaxFileSize=`：单个 journal 文件的大小上限；
- `MaxRetentionSec=`：日志最长保留时间，配合 `SystemMaxUse` 双保险；
- `MaxFileSec=`：单个文件的最长生命周期，控制轮转节奏。

易失的运行时日志（`/run`）对应的是 `RuntimeMaxUse=`、`RuntimeKeepFree=`，默认同样是所在分区 10%、15%（上限 4G），`/run` 一般是 tmpfs，内存紧张时也值得调小。

改完记得 `systemctl restart systemd-journald` 才生效。这套配一次，journal 就再也不会无上限增长。

## logrotate：管好 /var/log 里的文本日志

journald 管的是 systemd 服务，但还有大量程序自己往 `/var/log` 写文本日志。它们靠 `logrotate` 轮转——每天由 cron（`/etc/cron.daily/logrotate`）或 systemd 定时器（`logrotate.timer`）跑一次。

系统自带的 `/etc/logrotate.conf` 只给了个很保守的默认，真正要管的是每个服务在 `/etc/logrotate.d/` 下的独立配置。一个典型的应用日志配置长这样：

```conf
/var/log/myapp/*.log {
    daily
    rotate 7
    size 100M
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

各参数含义：

- `daily` / `weekly` / `monthly`：轮转周期；`size 100M` 表示超过 100M 也轮转；
- `rotate 7`：保留 7 个历史文件，更早的删掉；
- `compress`：旧日志压缩成 `.gz`；`delaycompress` 让最近一个历史文件先不压缩，等下一次轮转再压，方便程序继续写；
- `missingok`：日志文件不存在也不报错；`notifempty`：空文件不轮转；
- `copytruncate`：复制一份再截断原文件（见下文说明）。

### copytruncate 还是 create + postrotate？

这是 logrotate 里最容易踩的坑，也是"轮转后日志不更新了"的常见原因。两种机制差别很大：

- **`copytruncate`**：把原文件复制成归档，再把原文件截断成 0。文件句柄、inode 都不变，程序不用做任何事就能继续写。代价是截断那一刻到下一次写入之间有极小的数据丢失窗口，而且大文件复制有额外 IO。
- **`create` + `postrotate` 发信号**：把原文件改名成归档，新建一个同名空文件，再通过 `postrotate` 里的命令（比如 `kill -USR1`）通知程序重新打开日志。没有数据丢失，但要求程序支持"收到信号后重开日志文件"。

nginx 就是典型的后者用法：

```conf
/var/log/nginx/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        if [ -f /var/run/nginx.pid ]; then
            kill -USR1 `cat /var/run/nginx.pid`
        fi
    endscript
}
```

判断标准很简单：程序能响应信号重开日志（nginx 的 `-USR1`、很多守护进程的 `SIGHUP`），就用 `create + postrotate`；如果程序不响应、只会一直握着原文件句柄写（很多自写日志的小程序），就用 `copytruncate` 兜底。

### 改完先验证，再手动触发

```bash
sudo logrotate -d /etc/logrotate.conf   # 调试模式，只打印会做什么，不真正执行
sudo logrotate -f /etc/logrotate.conf   # 强制执行一次，立即生效
```

`-d` 一定要先跑一遍看输出，确认没有"跳过某条配置"或语法错误，再 `-f` 强制执行。

## 花五分钟，换一个日志不再半夜报警的以后

清理解决的是这一次，下面三件事解决的是"以后还会不会再来一次"。

1. **journald 和 logrotate 都设上限**。`SystemMaxUse` + `SystemKeepFree` 是 journald 这边投入产出比最高的配置，`/etc/logrotate.d/` 里给每个会写文件的日志补一条轮转规则，是文本日志那边最该做的一件事。

2. **在打满之前就该有告警**。`/var/log` 所在分区设 80% 预警、85% 严重告警；日常巡检顺手跑一下 `journalctl --disk-usage` 和 `du -sh /var/log`，趋势提前就能看出来。

3. **该集中采集就集中采集，别让单机一直存历史**。日志的最终归宿是能被检索、能告警的地方（Loki、ELK 或远程 journald），本地只保留最近一段时间用于应急排查就够了。这跟 Docker 别把日志当日志仓库是一个道理。日志与数据该存哪、存多久，本质上是一条存储策略，相关做法可参考 [数据存储路径](/zh/usage/data-storage-path)。

## 一页纸清单，存起来备用

```bash
journalctl --disk-usage
sudo journalctl --vacuum-size=200M
sudo du -sh /var/log/* | sort -rh | head
sudo logrotate -d /etc/logrotate.conf
sudo systemctl restart systemd-journald
```

顺序是：先 `--disk-usage` 和 `du` 定位，再用 `--vacuum` 或 `logrotate -f` 清理，最后把 `journald.conf` 和 `/etc/logrotate.d/` 的上限配好。下次日志再想偷偷写满磁盘，它自己会先拦下来。

---

日志问题，第一步永远是先登进机器看清楚是谁在写，而不是直接删文件。远程排查时用 [Termark](https://www.termark.app/zh-cn/?utm_source=docs&utm_medium=blog&utm_campaign=log_rotation_journald&audience=ops) 连上服务器，`journalctl` 和 `du` 直接在终端里跑，需要把大日志拉回本地细看时它的 SFTP 也用得上。把上限配好这一次，日志写满磁盘这种事基本就不会再来烦你了。

## 参考资料

- [systemd-journald.conf 手册](https://www.freedesktop.org/software/systemd/man/systemd-journald.conf.html)
- [journalctl 手册](https://www.freedesktop.org/software/systemd/man/journalctl.html)
- [logrotate 手册](https://linux.die.net/man/8/logrotate)
- [systemd 日志文件格式](https://systemd.io/JOURNAL_FILE_FORMAT/)
