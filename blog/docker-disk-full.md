---
title: Docker Filled Up Your Disk? How to Diagnose, Clean, and Fix It for Good
description: A practical guide to diagnosing Docker disk usage with docker system df, cleaning json-file logs, images, containers, and volumes, and preventing it from happening again with log rotation and scheduled cleanup.
date: 2026-08-23
updated: 2026-08-23
author: Termark Team
---

# Docker Filled Up Your Disk? How to Diagnose, Clean, and Fix It for Good

2:30 AM. Your alert channel pings: `no space left on device`. You drag yourself out of bed, SSH into the server, and see `/` at 100%. `docker ps` takes ten seconds to respond. Logs stop writing. Deploys hang halfway.

Do not rush to resize the disk. A full disk is rarely because your business data actually grew that large. Eight times out of ten, Docker did it to itself — logs without rotation, images nobody cleaned up, containers that stopped but were never removed. It never warns you in advance. It just picks this moment, in this way, to let you know.

This guide is not about "what happened." It is about how to pinpoint who is using the space within ten minutes, clean it up without deleting the wrong data, and configure it once so you never have to deal with it again.

## Do not prune yet. Figure out who is responsible.

Too many people run `docker system prune -a --volumes` the moment the disk hits 100%, and ask in the group chat the next day where their database went. The command is powerful, but it is indiscriminate — volumes, images, containers, anything it considers "unused" goes. Spending two minutes to confirm the situation is far cheaper than hunting for a backup later:

```bash
df -h
# Which mount is over 90%? Usually /

docker system df
# Images       18.2GB   14.1GB reclaimable
# Containers   32GB     28GB reclaimable
# Build Cache  11.3GB   fully reclaimable

sudo du -sh /var/lib/docker/* | sort -rh | head -10
```

Look at the RECLAIMABLE column in `docker system df`. If that number lines up with the used space in `df -h`, Docker is almost certainly the cause — and most of it can be reclaimed safely. If you are troubleshooting remotely, running these commands over SSH with a client like [Termark](https://www.termark.app/?utm_source=docs&utm_medium=blog&utm_campaign=docker_disk_full) and pulling a log file back over SFTP is the fastest way to get oriented.

Rough priority for investigation: logs > images and build cache > stopped-but-not-removed containers > abnormal overlay2 growth. Follow this order and you will not go in circles.

## Culprit #1: Unmanaged logs

Docker's default `json-file` driver does not rotate. A verbose service can accumulate a log file tens of gigabytes in size within days — and `docker system df` will not even count it. You have to dig for it yourself.

### Find it

```bash
# Largest log files
sudo find /var/lib/docker/containers -name "*-json.log" -type f -exec du -sh {} + | sort -rh | head -10

# Map back to container names
docker ps -a --format '{{.ID}} {{.Names}}' | while read id name; do
  log=$(docker inspect --format='{{.LogPath}}' "$id" 2>/dev/null)
  [ -f "$log" ] && echo "$(du -h "$log" | cut -f1) $name"
done | sort -rh | head -10
```

If you see a line like `28G my-app`, you have your answer.

### Stop the bleeding: truncate, do not rm

The instinct is to `rm` the log file, only to find that `df -h` does not change at all. As long as the Docker daemon still holds a handle to the file, deleting it does not free the space. The correct fix is to truncate it:

```bash
# Truncate one container's log
sudo truncate -s 0 /var/lib/docker/containers/<container-id>/*-json.log

# Truncate all container logs at once
sudo sh -c 'truncate -s 0 /var/lib/docker/containers/*/*-json.log'

df -h
docker system df
```

No restart needed. Space returns immediately.

### Fix the root cause: make logs cap themselves

Stopping the bleeding only buys time until the next incident. Add limits in /etc/docker/daemon.json so every container created afterward comes with a ceiling:

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

This only applies to **newly created** containers — existing ones must be recreated to pick it up. With Compose, it is clearer to declare it per service:

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

After this, each container is capped at 30 MB (3 files × 10 MB). No more multi-gigabyte log files. If you need longer retention, ship to `journald`, Loki, or ELK instead of letting Docker act as a log warehouse — that was never its job. See [Data Storage Path](/usage/data-storage-path) for related patterns.

## Culprit #2: Images, build cache, and containers that were never cleaned up

Logs alone not enough? You are hoarding — old images, old build cache, containers that stopped but were never removed all keep occupying space. `docker system df -v` gives an itemized breakdown. This table covers most cases:

| What you want to clean | Command | What it deletes | Affects running containers? |
| --- | --- | --- | --- |
| Routine cleanup | `docker system prune` | Stopped containers, dangling images, unused networks, build cache | No |
| Also unused images | `docker system prune -a` | Above plus images not used by any container | No, but you will need to pull the image again next time |
| Also unused volumes | `docker system prune --volumes` | Above plus volumes not mounted to any container | May delete data — the most dangerous step |
| Only build cache | `docker builder prune -a` | BuildKit cache | No, next build may be slower |
| Only dangling images | `docker image prune` | Untagged `<none>` images | Safe |

Three common scenarios:

```bash
# Routine check — safe
docker system prune -f
docker builder prune -f

# Deep clean when disk is critical — verify volumes first
docker system prune -a --volumes -f

# Only old build cache
docker builder prune -a -f --filter until=72h
```

Two pitfalls almost everyone hits at least once:

1. **A stopped container still occupies space.** A container in `Exited` state still keeps its writable layer and log file. Once you confirm it is no longer needed, remove it: `docker rm $(docker ps -aq -f status=exited)`.
2. **Volumes are the most dangerous part.** `docker volume ls` may already contain your database. Before adding --volumes to any command, run `docker volume inspect <name>` and confirm — too many people have learned this the hard way.

## Culprit #3: Abnormal overlay2 growth — do not touch it by hand

Running `sudo du -sh /var/lib/docker/overlay2/* | sort -rh | head` shows a pile of hash-named directories and the temptation to delete them is strong. Do not. This is the layered filesystem itself, already included in the `docker system df` accounting. Deleting by hand is likely to break running containers.

Abnormal growth here usually means a container wrote what belongs in a volume — uploads, logs, caches — directly into its own writable layer. Find the real source:

```bash
docker ps -s --format '{{.Names}} {{.Size}}' | sort -rk2 -h | head -10
docker images --format '{{.Repository}}:{{.Tag}} {{.Size}}' | sort -rk2 -h | head -10
```

Then move that data to a volume or object storage, and slim oversized images with multi-stage builds. That is the durable fix.

## Five minutes now for a future without midnight wake-ups

Cleanup fixes this incident. The four items below fix "will this happen again?"

1. Cap logs for every container. The `max-size` in daemon.json is the single highest-ROI setting here.

2. Hand cleanup to cron. Do not rely on memory:

```bash
# /etc/cron.weekly/docker-prune
#!/bin/sh
docker system prune -f --filter "until=168h" >/dev/null 2>&1
docker builder prune -f --filter "until=168h" >/dev/null 2>&1
```

3. Alert before the disk is full. Set warnings at 80% and critical at 85% for `/` and `/var/lib/docker`. A quick `docker system df` during routine checks trends the problem early.

4. Stop treating containers as long-lived VMs. `.dockerignore`, multi-stage builds, and keeping data on volumes rather than the writable layer address most overlay2 issues at the source.

## One-page checklist — save it

```bash
df -h; echo "---"; docker system df
sudo find /var/lib/docker/containers -name "*-json.log" -exec du -sh {} + | sort -rh | head -5
docker ps -s | head -10
docker images | head -10
docker volume ls
```

Order: truncate large logs first, then clean unused resources (confirm volumes hold no important data), finally set `daemon.json` and scheduled cleanup. Next time the alert fires, you will be the calmest person in the channel.

---

When disk pressure hits, the first step is always to get on the machine and look, not to guess. Connect directly with [Termark](https://www.termark.app/?utm_source=docs&utm_medium=blog&utm_campaign=docker_disk_full&audience=ops) and run the diagnostics above in the terminal; SFTP is there when you need to pull a log for closer inspection. Configure log rotation and regular pruning once, and these midnight alerts will largely stop coming for you.

## References

- [Docker json-file logging driver](https://docs.docker.com/config/containers/logging/json-file/)
- [docker system df / prune](https://docs.docker.com/engine/reference/commandline/system_df/)
- [BuildKit cache and builder prune](https://docs.docker.com/build/cache/)
