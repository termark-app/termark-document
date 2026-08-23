---
title: Docker 把磁盘吃满了？日志、镜像、容器三步清理与根治
description: Docker 磁盘满了怎么清理？本文从 docker system df、json-file 日志、overlay2 与构建缓存出发，手把手排查镜像、容器、卷和日志占用，用 docker system prune 与 log-opts 彻底根治 Docker 磁盘占用问题。
date: 2026-08-23
updated: 2026-08-23
author: Termark Team
---

# Docker 把磁盘吃满了？日志、镜像、容器三步清理与根治

凌晨两点半，监控群弹出一条：`No space left on device`。

你迷迷糊糊连上服务器，`df -h` 一看，`/` 直接 100%。`docker ps` 卡半天才出来，日志写不进去，新镜像也拉不下来。别慌，也别急着给磁盘扩容——十次有八次，是 Docker 把你的盘当成了垃圾场，而且它一声不吭。

如果把服务器比作一间出租屋，Docker 就是那个从不丢垃圾的室友：外卖盒（日志）堆到天花板，快递箱（镜像）拆完就扔角落，吃完的泡面桶（已停止的容器）也不扔。你不收拾，它就替你把屋子塞满。

今天不念手册，用一条能复制粘贴的路径，把 Docker 占盘的四宗罪一次性收拾干净。

## 先别急着 prune，先验尸

上来就 `docker system prune -a` 的人，第二天往往在群里问：我的数据库数据呢？

先分清是谁的锅：

```bash
df -h
# 看哪个挂载点 Use% 飙到 90%+，大概率是 /

docker system df
# Images     18.2GB   14.1GB 可回收
# Containers 32GB     28GB 可回收
# Build Cache 11.3GB 全部可回收

sudo du -sh /var/lib/docker/* | sort -rh | head -10
```

如果 `docker system df` 的 `RECLAIMABLE` 很高，恭喜，空间都在 Docker 手里，而且大多能安全回收。用 [Termark](https://www.termark.app/zh-cn/?utm_source=docs&utm_medium=blog&utm_campaign=docker_disk_full) 连上服务器就能直接跑，不用来回拷脚本。

接下来按“作案频率”排序：日志 > 镜像/缓存 > 幽灵容器与卷 > overlay2。

## 真凶一：日志，一个文件 30GB 的隐形炸弹

Docker 默认日志驱动 `json-file`，默认不轮转。你跑一个爱打日志的 Java 服务，一周就能给你整出一个 30GB 的单文件。最骚的是，`docker system df` 甚至不会把它单独列出来，你得自己去挖。

### 怎么揪出来

```bash
# 按文件大小揪出前 10 个
sudo find /var/lib/docker/containers -name "*-json.log" -type f -exec du -sh {} + | sort -rh | head -10

# 按容器名看，谁是罪魁祸首
docker ps -a --format '{{.ID}} {{.Names}}' | while read id name; do
  log=$(docker inspect --format='{{.LogPath}}' $id 2>/dev/null)
  [ -f "$log" ] && echo "$(du -h $log | cut -f1) $name"
done | sort -rh | head -10
```

看到某行 `28G my-app`，别怀疑，就是它。

### 急救：别 rm，用 truncate

很多人的第一反应是 `rm`。删完发现 `df -h` 一点没变——因为进程还握着句柄，文件删了，空间没释放。就像你把垃圾桶烧了，垃圾还在空中飘着。

正确姿势是直接把文件截断，空间立马回来，容器都不用重启：

```bash
# 只截断最大的那个
sudo truncate -s 0 /var/lib/docker/containers/<container-id>/*-json.log

# 全体截断，一键清场
sudo sh -c 'truncate -s 0 /var/lib/docker/containers/*/*-json.log'

docker system df && df -h
# 看着 Use% 从 100% 掉到 60%，比奶茶还解压
```

### 根治：给日志加个“自动倒垃圾”

急救完不治本，下周还会满。在 `/etc/docker/daemon.json` 加上轮转，以后新容器自动限流：

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

已跑着的容器要重建才生效。用 Compose 更直观：

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

单容器最多 30MB（3 × 10MB），再也不会出现 30GB 的怪物日志。想长期留日志？换 `journald` 或接 Loki/ELK，别让 Docker 当日志仓库。相关思路可参考 [数据存储路径](/zh/usage/data-storage-path)。

## 真凶二：镜像、缓存、幽灵容器——你的囤积癖

日志清完还没降？那就是你在囤东西。

`docker system df -v` 会告诉你谁能扔。别被吓到，这张表看懂就够了：

| 你想扔什么 | 命令 | 会发生什么 | 会影响线上吗 |
| --- | --- | --- | --- |
| 日常扫垃圾 | `docker system prune` | 清掉已停止的容器、悬空镜像、无效网络、构建缓存 | 不影响运行中的容器 |
| 连闲置镜像也扔 | `docker system prune -a` | 上面 + 所有没被容器用的镜像 | 会删镜像，下次要重新拉 |
| 连卷也扔 | `docker system prune --volumes` | 上面 + 没人用的卷 | **会删数据**，删库跑路就是这么来的 |
| 只清构建缓存 | `docker builder prune -a` | BuildKit 缓存 | 不影响容器，下次构建慢点 |

给你三档套餐：

```bash
# 日常保洁，每周跑一次，安全
docker system prune -f
docker builder prune -f

# 深度大扫除，磁盘告急时用
docker system prune -a --volumes -f  # 删卷前先看下一段！

# 只想清最肥的构建缓存
docker builder prune -a -f --filter until=72h
```

两个坑，踩过的人都后悔：

1.  **幽灵容器还在占坑**：`docker ps -a` 里一堆 `Exited` 的容器，可写层和日志还在。确认不要了就 `docker rm $(docker ps -aq -f status=exited)`。
2.  **卷是最危险的**：`docker volume ls` 里可能躺着你的数据库。`prune --volumes` 前务必 `docker volume inspect <name>` 看清楚挂载关系。别问我怎么知道的。

## 真凶三：overlay2，求你别手贱

`sudo du -sh /var/lib/docker/overlay2/* | sort -rh | head` 看到一堆哈希目录，手痒想 `rm -rf`？打住。

那是容器的分层文件系统，`docker system df` 已经算进去了。`overlay2` 异常大的真正原因，往往是：你在容器可写层里写了本该放进卷的东西——比如把用户上传、应用日志写进了容器内部。

```bash
# 错误做法
# rm -rf /var/lib/docker/overlay2/xxx  # 然后 Docker 直接去世

# 正确做法：找到是谁
docker ps -s --format '{{.Names}} {{.Size}}' | sort -rk2 -h | head -10
docker images --format '{{.Repository}}:{{.Tag}} {{.Size}}' | sort -rk2 -h | head -10
```

把大文件迁到卷或对象存储，镜像用多阶段构建瘦身，这才是正经事。

## 根治：花 5 分钟配好，以后再也不用半夜起床

清理是止血，预防是手术。给新机器做一次，以后告警群里再也 @不到你。

1.  **日志轮转必开**：`daemon.json` 的 `max-size` 是性价比之王。
2.  **每周自动扫一次**：丢个 cron，比你记性靠谱。

```bash
# /etc/cron.weekly/docker-prune
#!/bin/sh
docker system prune -f --filter "until=168h" >/dev/null 2>&1
docker builder prune -f --filter "until=168h" >/dev/null 2>&1
```

3.  **告警要比满盘早**：给 `/` 和 `/var/lib/docker` 设 80% 告警、85% 严重。平时用 Termark 巡检时顺手 `docker system df` 瞄一眼，趋势比数字更重要。

4.  **别把容器当虚拟机用**：`.dockerignore`、多阶段构建、数据一律走卷。别在可写层里堆东西。

## 收藏这一页，下次直接复制

```bash
df -h; echo "---"; docker system df
sudo find /var/lib/docker/containers -name "*-json.log" -exec du -sh {} + | sort -rh | head -5
docker ps -s | head -10
docker images | head -10
docker volume ls
```

按顺序来：截断大日志 → `prune` 清无用资源 → 确认卷里是不是真数据 → 补上 `daemon.json` 和定时清理。十分钟收敛，下次告警你就是群里最淡定的那个。

---

磁盘满了，第一步永远是连上服务器看现场。通过 [Termark](https://www.termark.app/zh-cn/?utm_source=docs&utm_medium=blog&utm_campaign=docker_disk_full&audience=ops) 直连主机，在终端里跑通上面的命令，需要传脚本或拉日志就用 SFTP 一步完成。把轮转和定时清理配好，Docker 就不会再半夜把你叫醒。

## 参考

- [Docker json-file 日志驱动](https://docs.docker.com/config/containers/logging/json-file/)
- [docker system df / prune](https://docs.docker.com/engine/reference/commandline/system_df/)
- [BuildKit 缓存与 builder prune](https://docs.docker.com/build/cache/)
