---
title: Docker Is Filling Up Your Disk? Clean Logs, Images, Containers, and Fix It for Good
description: Docker disk full? Learn how to diagnose disk usage with docker system df, json-file logs, overlay2, and build cache, then clean images, containers, volumes, and logs and prevent Docker from filling your disk again with log-opts.
date: 2026-08-23
updated: 2026-08-23
author: Termark Team
---

# Docker Is Filling Up Your Disk? Clean Logs, Images, Containers, and Fix It for Good

`No space left on device`. A `docker pull` that hangs. A container that cannot write logs. Even `docker ps` feels slow. In most cases the culprit is Docker. Before you rush to expand the disk, figure out what is filling `/var/lib/docker`. This guide follows one diagnostic path that covers the four most common categories of usage and gives you copy-paste cleanup and hardening steps.

## First, confirm Docker is the culprit

Do not start with `docker system prune -a`. Check whether the system disk is full or the Docker directory is full.

```bash
df -h
# Check which mount point is at 90%+ — usually /

docker system df
# TYPE            TOTAL   ACTIVE   SIZE      RECLAIMABLE
# Images          42      8        18.2GB    14.1GB (77%)
# Containers      12      3        32GB      28GB
# Local Volumes   6       2        4.1GB     2.8GB
# Build Cache     89      0        11.3GB    11.3GB

# High RECLAIMABLE means a lot can be reclaimed
sudo du -sh /var/lib/docker/* | sort -rh | head -20
sudo du -sh /var/log/* 2>/dev/null | sort -rh | head -10
```

If the `SIZE` column in `docker system df` is close to the used space in `df -h`, Docker is the prime suspect. Investigate in order of hit rate: logs > images and build cache > stopped containers and volumes > overlay2 anomalies.

Connect with an SSH client such as [Termark](https://www.termark.app/?utm_source=docs&utm_medium=blog&utm_campaign=docker_disk_full) and run the commands above directly in the terminal — no need to shuffle scripts back and forth.

## Step 1: Container logs — the top offender on 90% of hosts

Docker's default log driver is `json-file` with no rotation. A chatty container can produce tens of gigabytes in a single JSON file within a week.

### Find the large logs

```bash
# Top 10 container logs by size
sudo find /var/lib/docker/containers -name "*-json.log" -type f -exec du -sh {} + | sort -rh | head -10

# Grouped by container
docker ps -a --format '{{.ID}} {{.Names}} {{.Status}}' | while read id name rest; do
  log=$(docker inspect --format='{{.LogPath}}' $id 2>/dev/null)
  [ -f "$log" ] && echo "$(du -h $log | cut -f1) $name $log"
done | sort -rh | head -10
```

If one `*-json.log` is several gigabytes, you have found the offender.

### Emergency cleanup without removing containers

```bash
# Truncate a single log (no restart needed, space freed immediately)
sudo truncate -s 0 /var/lib/docker/containers/<container-id>/*-json.log

# Truncate all logs at once
sudo sh -c 'truncate -s 0 /var/lib/docker/containers/*/*-json.log'

# Verify
docker system df
df -h
```

Do not `rm` the log file while `json-file` still holds the handle — space may not be reclaimed. `truncate` is more reliable.

### Fix it permanently: add log rotation

Set global defaults in `/etc/docker/daemon.json`. New containers will inherit the policy:

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

Existing containers must be recreated to pick up the new policy. With Docker Compose it is clearer in `compose.yaml`:

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

Each container is then capped at `30MB` (3 × 10MB). No more single file growing to tens of gigabytes.

> For long-term retention or centralized analysis, switch to `journald` or `gelf` and ship to Loki or the ELK stack, keeping only a short local buffer in Docker. For related data management patterns, see [Data Storage Path](/usage/data-storage-path) and [Local Encryption and Data Recovery](/usage/local-encryption).

## Step 2: Images, containers, volumes, and build cache

If logs alone do not bring usage down, look at these categories.

### One command to see everything

```bash
docker system df -v | head -100
```

Pay attention to `RECLAIMABLE`:

| Target | Command | What it removes | Affects running containers? |
| --- | --- | --- | --- |
| Safe general cleanup | `docker system prune` | Stopped containers, unused networks, dangling images, build cache | No |
| Also unused images | `docker system prune -a` | Above plus images not referenced by any container | Removes unused images; next run needs a pull |
| Also volumes | `docker system prune --volumes` | Above plus unused local volumes | Removes data in volumes — confirm first |
| Only build cache | `docker builder prune -a` | BuildKit cache | No, but next build is slower |
| Only dangling images | `docker image prune` | `<none>` images | Safe |

Common combinations:

```bash
# Regular safe cleanup — weekly or monthly
docker system prune -f
docker builder prune -f

# Deep cleanup when disk is critical — ensure no important unbacked volumes
docker system prune -a --volumes -f

# Only the heaviest build cache
docker builder prune -a -f --filter until=72h
```

### Two easy-to-miss points

1. **Stopped containers still use disk**: `Exited` containers in `docker ps -a` still occupy their writable layer and logs. Remove them when no longer needed: `docker rm $(docker ps -aq -f status=exited)`.

2. **Volumes are the most dangerous**: volumes in `docker volume ls` may hold database data. Before `prune --volumes`, run `docker volume ls` and `docker volume inspect <name>` to confirm.

## Step 3: overlay2 is full — do not delete files by hand

`sudo du -sh /var/lib/docker/overlay2/* | sort -rh | head` shows many hash directories. This is the layered filesystem. Under normal conditions it is already accounted for in `docker system df` — no manual deletion needed.

Common causes of abnormal `overlay2` growth:

- A container writes many files to its writable layer instead of a volume — for example uploads or logs written to a path inside the container.
- A large file was `COPY`ed during build or cache was left in an image layer.

Rule: do not `rm` inside `overlay2`.

```bash
# Wrong: rm -rf /var/lib/docker/overlay2/xxx
# Right: find the container or image above

# Largest writable layers
docker ps -s --format '{{.Names}} {{.Size}}' | sort -rk2 -h | head -10

# Largest images
docker images --format '{{.Repository}}:{{.Tag}} {{.Size}}' | sort -rk2 -h | head -10
```

Move large files to a volume or object storage and slim images with multi-stage builds — that is the real fix.

## Harden and prevent: stop the 3 AM alert

Cleanup stops the bleeding. Prevention stops the recurrence. Do this once for a new host.

1. **Always enable log rotation**: `max-size` and `max-file` in `daemon.json` is the highest-ROI setting.
2. **Schedule regular pruning**: a weekly cron for build cache and dangling resources.

```bash
# /etc/cron.weekly/docker-prune
#!/bin/sh
docker system prune -f --filter "until=168h" >/dev/null 2>&1
docker builder prune -f --filter "until=168h" >/dev/null 2>&1
```

3. **Alert before the disk is full**: alert on `df` thresholds for `/` and `/var/lib/docker` (e.g. warn at 80%, critical at 85%). A quick `docker system df` during routine SSH inspection with Termark can reveal a trend early.

4. **Build and deploy hygiene**: use `.dockerignore`, multi-stage builds, and regular `docker image prune`; keep container data on volumes or external storage, never on the writable layer.

## One-page checklist (bookmark it)

```bash
df -h; echo "---"; docker system df
sudo find /var/lib/docker/containers -name "*-json.log" -exec du -sh {} + | sort -rh | head -5
docker ps -s | head -10
docker images | head -10
docker volume ls
docker builder du 2>/dev/null | head -20
```

In order: truncate large logs, prune unused resources, confirm business data in volumes and overlay2, then add `daemon.json` and scheduled pruning. The next disk alert will be contained within minutes.

---

When disk pressure hits, the first step is always to get onto the host and see the situation. Connect directly with [Termark](https://www.termark.app/?utm_source=docs&utm_medium=blog&utm_campaign=docker_disk_full&audience=ops) and run the diagnostic commands above in the terminal; use SFTP when you need to transfer a script or pull logs. Set `json-file` rotation and regular `prune` once, and Docker will stop eating your disk at night.

## References

- [Docker json-file logging driver](https://docs.docker.com/config/containers/logging/json-file/)
- [docker system df / prune](https://docs.docker.com/engine/reference/commandline/system_df/)
- [BuildKit cache and builder prune](https://docs.docker.com/build/cache/)
