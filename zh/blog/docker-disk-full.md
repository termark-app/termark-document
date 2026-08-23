---
title: Docker 把磁盘占满了？诊断、清理与彻底解决的方法
description: 一份实用指南，教你用 docker system df 诊断 Docker 磁盘占用，清理 json-file 日志、镜像、容器和数据卷，并通过日志轮转和定期清理防止问题复发。
date: 2026-08-23
updated: 2026-08-23
author: Termark Team
---

# Docker 把磁盘占满了？诊断、清理与彻底解决的方法

凌晨 2:30，告警群里弹出一条 `no space left on device`。你睡眼惺忪地爬起来连上服务器，`df -h` 显示 `/` 已经 100%，`docker ps` 卡了快十秒才出结果，日志写不进去，部署也卡在半路。

先别急着扩容磁盘。服务器磁盘写满这件事，很少是因为业务数据真的长这么大了。十次里有八次，是 Docker 自己攒出来的——日志没轮转、镜像没人清、容器停了但没删干净。它不会提前提醒你，只会在这种时间点、用这种方式让你发现。

这篇文章不讲“发生了什么”，讲怎么在十分钟内定位到底是谁占的空间、怎么在不误删数据的前提下清干净，以及怎么配置一次就不用再管。

## 别急着 prune，先查清楚是谁的问题

见过太多人磁盘一满就是一句 `docker system prune -a --volumes`，第二天在群里问“我的数据库呢”。这个命令确实好用，但它不分青红皂白——数据卷、镜像、容器，只要判定成“未使用”就一并清掉。先花两分钟确认现状，比事后找数据备份省事得多：

```bash
df -h
# 哪个挂载点占用超过 90%？通常是 /

docker system df
# Images       18.2GB   14.1GB reclaimable
# Containers   32GB     28GB reclaimable
# Build Cache  11.3GB   fully reclaimable

sudo du -sh /var/lib/docker/* | sort -rh | head -10
```

看 `docker system df` 里的 RECLAIMABLE 列——如果这一列的数字和 `df -h` 里用掉的空间对得上，问题基本可以确定出在 Docker 身上，而且大部分能安全清掉。如果是远程处理，用 [Termark](https://www.termark.app/zh-cn/?utm_source=docs&utm_medium=blog&utm_campaign=docker_disk_full) 这类 SSH 客户端跑这些命令、顺手把日志文件拉回本地看一眼也很方便。

排查优先级大致是：日志 > 镜像和构建缓存 > 停止但没删的容器 > overlay2 异常增长。按这个顺序查，基本不会走弯路。

## 元凶一：没人管的日志

Docker 默认的 json-file 驱动不会自动轮转。一个日志比较啰嗦的服务，几天内就能攒出一个几十 GB 的日志文件——而且 `docker system df` 根本不会把这部分算进去，得自己去翻。

### 揪出来

```bash
# 找出最大的日志文件
sudo find /var/lib/docker/containers -name "*-json.log" -type f -exec du -sh {} + | sort -rh | head -10

# 对应回容器名，看看是谁干的
docker ps -a --format '{{.ID}} {{.Names}}' | while read id name; do
  log=$(docker inspect --format='{{.LogPath}}' "$id" 2>/dev/null)
  [ -f "$log" ] && echo "$(du -h "$log" | cut -f1) $name"
done | sort -rh | head -10
```

如果这里跳出来一行 `28G my-app`，答案就有了。

### 先止血：truncate，不要 rm

很多人第一反应是 `rm` 掉这个日志文件，然后发现 `df -h` 里空间根本没变——只要 Docker 进程还握着这个文件的句柄，删了也不释放。正确做法是截断它：

```bash
# 截断某一个容器的日志
sudo truncate -s 0 /var/lib/docker/containers/<container-id>/*-json.log

# 一次性截断所有容器的日志
sudo sh -c 'truncate -s 0 /var/lib/docker/containers/*/*-json.log'

df -h
docker system df
```

这一步不需要重启容器，空间立刻就回来了。

### 再断根：让日志自己管住自己

止血只能撑到下一次。真正要做的是在 /etc/docker/daemon.json 里加上限制，让之后创建的每个容器都自带上限：

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

```bash
sudo systemctl restart docker
```

注意，这个配置只对**之后新建**的容器生效，已有的容器要重建才会应用。用 Compose 的话，直接写在服务定义里更清楚：

```yaml
services:
  app:
    image: my-app:latest
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

设置好之后，单个容器的日志总量被锁死在 30MB（3 个文件 × 10MB）以内，不会再出现几十 GB 的日志文件。如果业务需要更长的日志留存，该用 `journald`、Loki 或 ELK 去承接，而不是让 Docker 帮你当日志仓库——它本来就不是干这个的。相关做法可参考 [Data Storage Path](/zh/usage/data-storage-path)。

## 元凶二：镜像、构建缓存、没删干净的容器

日志清完还是不够？说明你在“攒东西”——旧镜像、旧构建缓存、停了但没删的容器，这些都会一直占着空间。`docker system df -v` 能给出逐项明细，下面这张表基本够用了：

| 想清理什么 | 命令 | 会删掉什么 | 会不会影响正在跑的容器 |
| --- | --- | --- | --- |
| 日常清理 | `docker system prune` | 已停止的容器、悬空镜像、没用的网络、构建缓存 | 不会 |
| 顺带清未用的镜像 | `docker system prune -a` | 以上 + 没有任何容器在用的镜像 | 不会，但下次跑这个镜像要重新拉取 |
| 顺带清未用的数据卷 | `docker system prune --volumes` | 以上 + 没挂载在任何容器上的数据卷 | 可能删数据**——这是最容易翻车的一步 |
| 只清构建缓存 | `docker builder prune -a` | BuildKit 缓存 | 不会，下次构建可能慢一点 |
| 只清悬空镜像 | `docker image prune` | 没打标签的 `<none>` 镜像 | 安全 |

三种常用场景：

```bash
# 日常巡检，放心用
docker system prune -f
docker builder prune -f

# 磁盘告急时的大扫除——动手前先确认数据卷情况
docker system prune -a --volumes -f

# 只想清掉旧的构建缓存
docker builder prune -a -f --filter until=72h
```

两个几乎人人都会踩一次的坑：

1. **停掉的容器不代表没占空间。** Exited 状态的容器仍然保留着自己的可写层和日志文件。确认不再需要了再删：`docker rm $(docker ps -aq -f status=exited)`。
2. **数据卷是最危险的一环。** `docker volume ls` 里可能就有你的数据库。在命令里加 --volumes 之前，先老老实实 `docker volume inspect <name>` 看一眼——这一步没做，出过事的人不止一个。

## 元凶三：overlay2 异常增长，别手动动它

跑一下 `sudo du -sh /var/lib/docker/overlay2/* | sort -rh | head`，会看到一堆哈希命名的目录，手很容易痒——但别删。这是分层文件系统本身，已经计入 `docker system df` 的统计里了，手动删除大概率会把正在跑的容器搞坏。

这里异常增长，通常说明某个容器把本该放数据卷的东西（上传文件、日志、缓存）直接写进了自己的可写层。找真正的源头：

```bash
docker ps -s --format '{{.Names}} {{.Size}}' | sort -rk2 -h | head -10
docker images --format '{{.Repository}}:{{.Tag}} {{.Size}}' | sort -rk2 -h | head -10
```

找到之后，把这部分数据挪到数据卷或对象存储，镜像本身偏大的话用多阶段构建瘦身——这才是长久的解法。

## 花五分钟，换一个不用半夜爬起来的以后

清理解决的是这一次，下面四件事解决的是“以后还会不会再来一次”。

1. 每个容器的日志都设上限。 daemon.json 里的 max-size 是这里投入产出比最高的一个配置，没有之一。

2. 清理这件事交给 cron，别指望自己记得住：

```bash
# /etc/cron.weekly/docker-prune
#!/bin/sh
docker system prune -f --filter "until=168h" >/dev/null 2>&1
docker builder prune -f --filter "until=168h" >/dev/null 2>&1
```

3. 在打满之前就该有告警。 / 和 /var/lib/docker 设 80% 预警、85% 严重告警，比等到 100% 才发现体面得多。日常巡检时顺手跑一下 `docker system df`，趋势提前就能看出来。

4. 别把容器当虚拟机长期养着。 `.dockerignore`、多阶段构建、把数据放数据卷而不是可写层——这几件事做到位，overlay2 的问题基本不会找上门。

## 一页纸清单，存起来备用

```bash
df -h; echo "---"; docker system df
sudo find /var/lib/docker/containers -name "*-json.log" -exec du -sh {} + | sort -rh | head -5
docker ps -s | head -10
docker images | head -10
docker volume ls
```

顺序是：先截断大日志，再清理没用的资源，清之前确认一遍数据卷是不是真有数据，最后把 `daemon.json` 和定期清理配好。下次告警响起的时候，你会是群里最不慌的那个。

---

磁盘告警一响，第一步永远是先登进机器看现状，而不是先猜。用 [Termark](https://www.termark.app/zh-cn/?utm_source=docs&utm_medium=blog&utm_campaign=docker_disk_full&audience=ops) 直接在终端里跑上面这些诊断命令，需要把日志拉下来细看时它的 SFTP 也用得上。日志轮转和定期清理配好这一次，这类半夜告警基本就不会再找上你了。

## 参考资料

- [Docker json-file 日志驱动](https://docs.docker.com/config/containers/logging/json-file/)
- [docker system df / prune](https://docs.docker.com/engine/reference/commandline/system_df/)
- [BuildKit 缓存与 builder prune](https://docs.docker.com/build/cache/)
