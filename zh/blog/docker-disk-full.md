---
title: Docker 把磁盘吃满了？日志、镜像、容器三步清理与根治
description: Docker 磁盘满了怎么清理？本文从 docker system df、json-file 日志、overlay2 与构建缓存出发，手把手排查镜像、容器、卷和日志占用，用 docker system prune 与 log-opts 彻底根治 Docker 磁盘占用问题。
date: 2026-08-23
updated: 2026-08-23
author: Termark Team
---

# Docker 把磁盘吃满了？日志、镜像、容器三步清理与根治

`No space left on device`，`docker pull` 卡住，容器写不进日志，连 `docker ps` 都变慢——十次有八次，罪魁祸首是 Docker。磁盘告警一响，第一反应别急着扩容，先搞清楚是谁把 `/var/lib/docker` 吃满了。本文用一条排查路径，把最常见的四类占用一次性讲清，并给出可直接复制的清理与根治配置。

## 先确认：是不是 Docker 占满的

别一上来就 `docker system prune -a`。先分清是系统盘满，还是 Docker 目录满。

```bash
df -h
# 看哪个挂载点  Use% 到 90%+，通常是 /

docker system df
# TYPE            TOTAL   ACTIVE   SIZE      RECLAIMABLE
# Images          42      8        18.2GB    14.1GB (77%)
# Containers      12      3        32GB      28GB
# Local Volumes   6       2        4.1GB     2.8GB
# Build Cache     89      0        11.3GB    11.3GB

# 如果 docker system df 显示 RECLAIMABLE 很高，说明可回收空间很多
# 再看真实占用
sudo du -sh /var/lib/docker/* | sort -rh | head -20
sudo du -sh /var/log/* 2>/dev/null | sort -rh | head -10
```

如果 `docker system df` 的 `SIZE` 接近 `df -h` 的已用空间，基本可以锁定 Docker。接下来按命中率排序排查：日志 > 镜像/构建缓存 > 已停止容器与卷 > overlay2 异常。

用 [Termark](https://www.termark.app/zh-cn/?utm_source=docs&utm_medium=blog&utm_campaign=docker_disk_full) 这类 SSH 客户端连上服务器后，直接在终端里跑上面几条就能定位，不用来回传脚本。

## 第一步：容器日志，90% 机器的头号元凶

Docker 默认的日志驱动是 `json-file`，默认不做轮转。一个打日志很勤的容器，一周就能写出几十 GB 的单个 JSON 文件。

### 怎么找到大日志

```bash
# 找出最大的 10 个容器日志
sudo find /var/lib/docker/containers -name "*-json.log" -type f -exec du -sh {} + | sort -rh | head -10

# 或按容器维度统计
docker ps -a --format '{{.ID}} {{.Names}} {{.Status}}' | while read id name rest; do
  log=$(docker inspect --format='{{.LogPath}}' $id 2>/dev/null)
  [ -f "$log" ] && echo "$(du -h $log | cut -f1) $name $log"
done | sort -rh | head -10
```

看到某个容器的 `*-json.log` 几 GB 甚至几十 GB，基本就是它。

### 应急清理（不删容器）

```bash
# 方式一：截断日志文件（无需重启容器，立即释放）
sudo truncate -s 0 /var/lib/docker/containers/<container-id>/*-json.log

# 方式二：批量截断所有日志
sudo sh -c 'truncate -s 0 /var/lib/docker/containers/*/*-json.log'

# 验证
docker system df
df -h
```

注意不要直接 `rm` 日志文件，`json-file` 驱动持有句柄时 `rm` 后空间不一定释放，`truncate` 更可靠。

### 根治：给日志加上轮转

在 `/etc/docker/daemon.json` 中配置全局默认，之后新建的容器都生效：

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

已运行的容器需要重建才生效，`docker compose` 项目改 `compose.yaml` 更直观：

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

这样单个容器日志最多 `30MB`（3 × 10MB），彻底告别单文件几十 GB。

> 进阶：日志要长期保留或集中分析，换 `journald` 或 `gelf` 并接入 Loki/ELK，让 Docker 只保留短期缓冲。详见 [数据存储路径](/zh/usage/data-storage-path) 与 [本地加密与数据恢复说明](/zh/usage/local-encryption) 的日志与数据管理思路。

## 第二步：镜像、容器、卷与构建缓存

日志清理完如果还没降下来，就看这几类。

### 一条命令看全貌

```bash
docker system df -v | head -100
```

重点看 `RECLAIMABLE`。下面这张表对应日常最常用的清理命令：

| 目标 | 命令 | 会删什么 | 是否影响运行中容器 |
| --- | --- | --- | --- |
| 无用数据一键清理 | `docker system prune` | 已停止容器、无用网络、悬空镜像、构建缓存 | 不影响运行中容器 |
| 连未使用的镜像也清 | `docker system prune -a` | 上一条 + 未被任何容器引用的镜像 | 会删未使用的镜像，下次需重新拉取 |
| 连卷也清 | `docker system prune --volumes` | 上述 + 未被使用的本地卷 | 会删卷内数据，务必确认 |
| 仅清构建缓存 | `docker builder prune -a` | BuildKit 构建缓存 | 不影响容器，但下次构建变慢 |
| 仅清悬空镜像 | `docker image prune` | `<none>` 悬空镜像 | 安全 |

常用组合：

```bash
# 日常安全清理（推荐每周或每月跑一次）
docker system prune -f
docker builder prune -f

# 磁盘告急时的深度清理（先确认没有重要未备份的卷）
docker system prune -a --volumes -f

# 只想清最占空间的构建缓存
docker builder prune -a -f --filter until=72h
```

### 容易被忽略的两个点

1. **已停止的容器还在占空间**：`docker ps -a` 看到的 `Exited` 容器，其可写层和日志仍在磁盘上。确认不再需要就 `docker rm $(docker ps -aq -f status=exited)`。

2. **卷（volume）最危险**：`docker volume ls` 看到的卷可能存着数据库数据。`prune --volumes` 前务必 `docker volume ls` 并用 `docker volume inspect <name>` 确认挂载关系。

## 第三步：overlay2 占满，别直接删文件

`sudo du -sh /var/lib/docker/overlay2/* | sort -rh | head` 看到很多哈希目录，这是容器的分层文件系统。正常情况下 `docker system df` 已统计在内，不需要手动删。

出现 `overlay2` 异常大的常见原因：

- 容器内写了大量文件到可写层而非卷，例如把上传文件、日志写进了容器内部路径
- 构建时 `COPY` 了大文件或在镜像层里留下了缓存

处理原则：

```bash
# 错误做法：直接 rm /var/lib/docker/overlay2/xxx
# 正确做法：找到对应的容器或镜像，从上层清理

# 查哪个容器可写层最大
docker ps -s --format '{{.Names}} {{.Size}}' | sort -rk2 -h | head -10

# 查哪个镜像最大
docker images --format '{{.Repository}}:{{.Tag}} {{.Size}}' | sort -rk2 -h | head -10
```

把容器内的大文件改写到卷或对象存储，镜像用多阶段构建瘦身，才是治本。

## 根治与预防：让磁盘不再半夜告警

清理是止血，预防是治本。给新机器做一次，后面省无数次半夜爬起来。

1. **日志轮转必开**：`daemon.json` 的 `max-size` 与 `max-file` 是性价比最高的配置。
2. **定期 prune**：加一条 cron，每周清理一次构建缓存与悬空资源。

```bash
# /etc/cron.weekly/docker-prune
#!/bin/sh
docker system prune -f --filter "until=168h" >/dev/null 2>&1
docker builder prune -f --filter "until=168h" >/dev/null 2>&1
```

3. **监控告警先于满盘**：对 `/` 和 `/var/lib/docker` 做 `df` 阈值告警（如 80% 告警、85% 严重），比满盘后再查要从容得多。平时用 Termark 连上服务器巡检时，顺手 `docker system df` 就能提前发现趋势。

4. **构建与部署习惯**：镜像用 `.dockerignore`、多阶段构建、定期 `docker image prune`；容器数据一律走卷或外部存储，别写在可写层。

## 一键排查清单（收藏）

```bash
df -h; echo "---"; docker system df
sudo find /var/lib/docker/containers -name "*-json.log" -exec du -sh {} + | sort -rh | head -5
docker ps -s | head -10
docker images | head -10
docker volume ls
docker builder du 2>/dev/null | head -20
```

按顺序做：截断大日志 → `prune` 清理无用资源 → 确认卷与 overlay2 的业务数据 → 补上 `daemon.json` 与定时清理。下次再收到磁盘告警，十分钟内就能收敛。

---

遇到磁盘问题，第一步永远是连上服务器看现场。通过 [Termark](https://www.termark.app/zh-cn/?utm_source=docs&utm_medium=blog&utm_campaign=docker_disk_full&audience=ops) 直连目标主机，在终端里跑通上面的排查命令，需要传脚本或拉日志时用 SFTP 一步完成。把 `json-file` 轮转和定期 `prune` 配好，Docker 就不会再半夜把磁盘吃满。

## 参考

- [Docker 日志与 json-file 驱动](https://docs.docker.com/config/containers/logging/json-file/)
- [docker system df / prune](https://docs.docker.com/engine/reference/commandline/system_df/)
- [BuildKit 缓存与 builder prune](https://docs.docker.com/build/cache/)

