---
title: Docker Is Filling Up Your Disk? Clean Logs, Images, Containers, and Fix It for Good
description: Docker disk full? Learn how to diagnose disk usage with docker system df, json-file logs, overlay2, and build cache, then clean images, containers, volumes, and logs and prevent Docker from filling your disk again with log-opts.
date: 2026-08-23
updated: 2026-08-23
author: Termark Team
---

# Docker Is Filling Up Your Disk? Clean Logs, Images, Containers, and Fix It for Good

2:30 AM. Your monitoring channel pings: `No space left on device`.

You SSH in half-asleep. `df -h` says `/` is at 100%. `docker ps` takes forever. Logs stop writing. Pulls fail. Do not rush to resize the disk — eight times out of ten, Docker is the roommate who never takes out the trash, and it never warns you.

Think of your server as a rental apartment. Docker is the roommate who stacks takeout boxes (logs) to the ceiling, leaves delivery cartons (images) in the corner, and never throws away instant noodle cups (stopped containers). Ignore it and it fills the place.

This is not a manual recital. It is one copy-paste path that catches the four usual suspects and leaves you with a fix that actually sticks.

## Do not prune first. Do an autopsy.

The person who runs `docker system prune -a` on sight is the same person asking in the group chat tomorrow: where did my database go?

Figure out whose fault it is:

```bash
df -h
# Which mount is at 90%+? Usually /

docker system df
# Images     18.2GB   14.1GB reclaimable
# Containers 32GB     28GB reclaimable
# Build Cache 11.3GB fully reclaimable

sudo du -sh /var/lib/docker/* | sort -rh | head -10
```

If `RECLAIMABLE` in `docker system df` is close to the used space in `df -h`, Docker owns your disk — and most of it can be reclaimed safely. SSH in with a client like [Termark](https://www.termark.app/?utm_source=docs&utm_medium=blog&utm_campaign=docker_disk_full) and run it right in the terminal.

Order of likelihood: logs > images and cache > ghost containers and volumes > overlay2 weirdness.

## Culprit #1: Logs — a single 30 GB time bomb

Docker's default driver is `json-file` with no rotation. A chatty Java service can create a single 30 GB JSON log in a week. The fun part: `docker system df` does not even break it out. You have to dig.

### Hunt it down

```bash
# Top 10 log files by size
sudo find /var/lib/docker/containers -name "*-json.log" -type f -exec du -sh {} + | sort -rh | head -10

# By container name — who did it?
docker ps -a --format '{{.ID}} {{.Names}}' | while read id name; do
  log=$(docker inspect --format='{{.LogPath}}' $id 2>/dev/null)
  [ -f "$log" ] && echo "$(du -h $log | cut -f1) $name"
done | sort -rh | head -10
```

If you see `28G my-app`, that is your perpetrator.

### First aid: do not rm, truncate

The instinct is to `rm`. You delete it, check `df -h`, and nothing changes — the daemon still holds the file handle. You burned the trash can while the trash floats in mid-air.

Truncate it. Space returns instantly, no restart needed:

```bash
# Just the biggest offender
sudo truncate -s 0 /var/lib/docker/containers/<container-id>/*-json.log

# Nuke all logs at once
sudo sh -c 'truncate -s 0 /var/lib/docker/containers/*/*-json.log'

docker system df && df -h
# Watching Use% drop from 100% to 60% is more satisfying than bubble tea
```

### Cure it: give logs an auto-rotation

First aid without a cure means you will be back next week. Set rotation in `/etc/docker/daemon.json` so every new container is capped:

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

Existing containers must be recreated. With Compose it is explicit:

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

Each container is now capped at 30 MB (3 × 10 MB). No more 30 GB monsters. Need long-term retention? Ship to `journald`, Loki, or ELK — do not let Docker be your log warehouse. See [Data Storage Path](/usage/data-storage-path) for related patterns.

## Culprit #2: Images, cache, ghost containers — you are hoarding

Logs did not free enough? You are hoarding.

`docker system df -v` tells you what can go. This table is all you need:

| What you want to toss | Command | What happens | Hurts running containers? |
| --- | --- | --- | --- |
| Routine sweep | `docker system prune` | Stopped containers, dangling images, unused networks, build cache | No |
| Also idle images | `docker system prune -a` | Above plus images not used by any container | Removes images; next run needs a pull |
| Also volumes | `docker system prune --volumes` | Above plus unused volumes | **Deletes data** — this is how you lose a database |
| Only build cache | `docker builder prune -a` | BuildKit cache | No, next build is slower |
| Only dangling images | `docker image prune` | `<none>` images | Safe |

Three presets:

```bash
# Weekly housekeeping — safe
docker system prune -f
docker builder prune -f

# Deep clean when disk is critical
docker system prune -a --volumes -f  # Check volumes first!

# Only the fattest build cache
docker builder prune -a -f --filter until=72h
```

Two traps everyone hits once:

1. **Ghost containers still occupy space**: `Exited` containers in `docker ps -a` still hold their writable layer and logs. If you no longer need them: `docker rm $(docker ps -aq -f status=exited)`.
2. **Volumes are the most dangerous**: `docker volume ls` may list your database. Before `prune --volumes`, run `docker volume inspect <name>`. I know this the hard way.

## Culprit #3: overlay2 — do not touch it by hand

`sudo du -sh /var/lib/docker/overlay2/* | sort -rh | head` shows hash directories and the urge to `rm -rf` kicks in. Resist.

That is the layered filesystem. It is already counted in `docker system df`. Abnormal growth usually means you wrote what belongs in a volume into the writable layer — uploads or app logs inside the container.

```bash
# Wrong:
# rm -rf /var/lib/docker/overlay2/xxx  # Then Docker dies

# Right: find the owner
docker ps -s --format '{{.Names}} {{.Size}}' | sort -rk2 -h | head -10
docker images --format '{{.Repository}}:{{.Tag}} {{.Size}}' | sort -rk2 -h | head -10
```

Move large files to a volume or object storage and slim images with multi-stage builds. That is the grown-up fix.

## Fix it for good: five minutes now saves a 3 AM wake-up

Cleanup stops the bleeding. Prevention stops the recurrence.

1. **Always cap logs**: `max-size` in `daemon.json` is the highest-ROI knob.
2. **Prune on a schedule**: let cron remember for you.

```bash
# /etc/cron.weekly/docker-prune
#!/bin/sh
docker system prune -f --filter "until=168h" >/dev/null 2>&1
docker builder prune -f --filter "until=168h" >/dev/null 2>&1
```

3. **Alert before full**: threshold alerts for `/` and `/var/lib/docker` at 80% warning, 85% critical. A quick `docker system df` during a routine SSH check with Termark reveals the trend early.

4. **Stop using containers as VMs**: `.dockerignore`, multi-stage builds, keep data on volumes. Never pile data on the writable layer.

## One-page checklist — bookmark it

```bash
df -h; echo "---"; docker system df
sudo find /var/lib/docker/containers -name "*-json.log" -exec du -sh {} + | sort -rh | head -5
docker ps -s | head -10
docker images | head -10
docker volume ls
```

Order: truncate large logs, prune unused resources, confirm whether volumes hold real data, then add `daemon.json` and scheduled pruning. Next alert, you will be the calmest person in the group.

---

When disk pressure hits, the first step is always to get on the box. Connect directly with [Termark](https://www.termark.app/?utm_source=docs&utm_medium=blog&utm_campaign=docker_disk_full&audience=ops) and run the diagnostics above in the terminal; use SFTP when you need to move a script or pull logs. Set rotation and regular pruning once, and Docker will stop waking you at night.

## References

- [Docker json-file logging driver](https://docs.docker.com/config/containers/logging/json-file/)
- [docker system df / prune](https://docs.docker.com/engine/reference/commandline/system_df/)
- [BuildKit cache and builder prune](https://docs.docker.com/build/cache/)
