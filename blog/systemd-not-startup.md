---
title: "Why Your Service Dies on Reboot: 3 Systemd Pitfalls"
description: "Your service runs when started manually but fails after reboot — often due to systemd autostart and keepalive misconfiguration. This guide covers 3 common pitfalls: enabled not ready, environment and permission gaps, and restart policy failures, with unit examples and journalctl diagnostics."
date: 2026-08-28
updated: 2026-08-28
author: Termark Team
---

# Why Your Service Dies on Reboot: 3 Systemd Pitfalls

`systemctl start myapp` runs fine, then one reboot it won't come back up. You ran `systemctl enable` too, yet the service still reports dependency or readiness errors at boot. The sneakier variant: the process gets OOM-killed or crashes and is never restarted — you don't even know when it went down, until a colleague asks "is your service down?" Once you've hit these a few times, you learn that a restart never fixes any of them, because the root cause is almost always the same: your systemd unit's autostart and keepalive configuration is not as complete as you assumed.

systemd is declarative and unforgiving about details: `enable` only decides whether a unit gets pulled in, `After`/`Requires`/`Wants` govern ordering and dependency strength, `Type` decides how startup completion is judged, and `Restart`/`StartLimit` decide whether a failure is retried. A missing line or a wrong value makes the service fail silently at the worst moment — a reboot, a delayed dependency, or a crash — while `systemctl status` usually hands you a terse `failed` and forces you to dig the real cause out of `journalctl`.

This post breaks down these three pitfalls one by one, each with the typical symptom, the root cause, a copy-paste fix, and the commands to verify it. The examples target systemd 249+ on Ubuntu 22.04 / Debian 12; paths and commands are largely portable. On CentOS/RHEL, Arch, or openSUSE, just mind the unit-file path precedence and the `systemctl --version` difference — the diagnostic approach is the same.

## Quick Baseline: Check Logs Before Changing Config

Before editing any unit file, establish a baseline with three commands to avoid masking issues with blind restarts:

```bash
systemctl status myapp.service -l --no-pager
journalctl -u myapp.service --since "1 hour ago" --no-pager | tail -n 100
systemd-analyze verify /etc/systemd/system/myapp.service
```

`systemctl status` shows current state and recent logs, `journalctl -u` shows the full timeline, and `systemd-analyze verify` checks syntax and dependency references without starting the service. Errors like `Service has no ExecStart=` or `Unknown key name` mean the unit will not take effect even after `daemon-reload`. Another useful command is `systemd-analyze critical-chain myapp.service`, which visualizes the startup chain and timing. Make it a habit: verify before editing, daemon-reload after editing, and status plus journalctl after reboot.

## Pitfall 1: Enabled Does Not Mean Ready — WantedBy, Dependencies, and Type

### Symptoms

`systemctl enable myapp` succeeds and `systemctl is-enabled myapp` shows `enabled`, but after reboot `systemctl status myapp` shows inactive or failed.

### Cause 1: WantedBy and the enable target mismatch

`enable` creates a symlink under the target specified by `WantedBy`:

```bash
systemctl cat myapp.service
systemctl is-enabled myapp.service
systemctl status myapp.service
ls -l /etc/systemd/system/multi-user.target.wants/myapp.service
```

If `Install` is set to `WantedBy=graphical.target` while the server boots to `multi-user.target`, the service will not be started. This is common on container and minimal cloud images.

Fix: long-running server services should use `WantedBy=multi-user.target`. After changing it, run `daemon-reload` and re-enable:

```ini
[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl reenable myapp.service
systemctl is-enabled myapp.service
```

### Cause 2: Confusing After / Wants / Requires

- `After=` only defines ordering, not a dependency. `After=network.target` alone does not guarantee the network is usable.
- `Wants=` is a weak dependency; failure of the wanted unit does not fail this unit.
- `Requires=` is a strong dependency; failure of the required unit fails this unit as well.

Services that need a usable network should use `After=network-online.target` with `Wants=network-online.target`, and ensure `systemd-networkd-wait-online` or `NetworkManager-wait-online` is enabled. Services that need a database should use `Requires=` plus `After=` on the database unit.

### Cause 3: Type mismatched to the process model

`Type=simple` fits foreground processes (most Go, Node, and Python services); `Type=forking` is only for programs that daemonize themselves and need a `PIDFile`; `Type=notify` requires the process to call `sd_notify`.

A non-forking program configured as `forking` will hit a start timeout because the parent never exits; a service that needs `notify` configured as `simple` will miss readiness detection. Prefer `Type=simple` unless you know the program forks.

Verify:

```bash
sudo systemd-analyze verify /etc/systemd/system/myapp.service
sudo systemctl daemon-reload
sudo systemctl restart myapp.service
systemctl show myapp.service -p Type -p ActiveState -p SubState
```

If `verify` produces no output and `ActiveState=active` with `SubState=running`, the type and dependencies are likely correct. Confirm reboot behavior with an actual `sudo reboot` and `systemctl status`, not just `restart`.

## Pitfall 2: Environment and Permissions — WorkingDirectory, Environment, User, and Paths

### Symptoms

Running `node app.js` or `./myapp` in a shell works, but starting via systemd reports `No such file or directory`, `Permission denied`, or missing config files.

### Cause

systemd starts with a clean environment — it does not inherit `PATH`, `PWD`, `env`, or `ulimit` from a login shell. Common omissions:

- Missing `WorkingDirectory`, so relative config or asset paths fail to resolve.
- Missing `Environment` or `EnvironmentFile`, leaving `DATABASE_URL` or `NODE_ENV` empty.
- Incorrect `User=`: the service worked as `root` during debugging but lacks file or port permissions as `app`.
- `ExecStart` uses a relative path or `~` expansion, which systemd does not expand via a shell.

### Fixed example

```ini
[Unit]
Description=MyApp Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=app
Group=app
WorkingDirectory=/opt/myapp
Environment=NODE_ENV=production
EnvironmentFile=-/etc/myapp/env
ExecStart=/usr/bin/node /opt/myapp/app.js
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Key points:

- `ExecStart` must use absolute paths; if shell features are needed, wrap with `/bin/bash -c '...'`.
- A leading `-` in `EnvironmentFile` means systemd will not fail if the file is absent.
- A non-existent `WorkingDirectory` makes the start fail immediately — create it in advance with `mkdir -p` and set ownership.

Verify:

```bash
sudo systemctl daemon-reload
sudo systemctl restart myapp.service
journalctl -u myapp.service --since "5 min ago" --no-pager
systemctl show myapp.service -p WorkingDirectory -p User -p Group -p Environment -p ExecStart
# Compare with manual environment
env | sort
pwd; id
ls -ld /opt/myapp /etc/myapp
```

If `journalctl` still shows path or permission errors, compare `systemctl cat` against the manual `env`, `pwd`, and `id` outputs and fill in the missing variables and directory permissions.

## Pitfall 3: Keepalive and Restart Policy — Restart, RestartSec, and StartLimit

### Symptoms

After an OOM kill, port conflict, or crash, systemd does not bring the service back; or repeated crashes put the unit into `failed` where it stops retrying.

### Cause

The default is `Restart=no` — systemd will not restart an exited process. Even with `Restart=on-failure`, `StartLimit*` throttling applies: if failures exceed the threshold within a short window, systemd stops retrying.

Reference:

| Field | Purpose | Common values |
| --- | --- | --- |
| `Restart` | Which exits trigger a restart | `no` / `on-failure` / `always` / `on-abnormal` |
| `RestartSec` | Wait before restarting | `5s` / `10s` — avoid tight loops |
| `StartLimitIntervalSec` | Window for counting | `60s` / `120s` |
| `StartLimitBurst` | Max attempts in window | `5` / `10` |
| `TimeoutStartSec` | Startup timeout | `30s` / `60s` |

On newer systemd (240+), `StartLimitIntervalSec` and `StartLimitBurst` belong under `[Unit]`; on older releases they belong under `[Service]` as `StartLimitInterval` / `StartLimitBurst`. Using the new names on an old system silently disables throttling. Check with `systemctl --version` and support both if needed.

`Restart=always` also restarts after a clean `systemctl stop`, which suits always-on services but needs careful use with `ExecStop`; `on-failure` restarts only on non-zero exits, signals, or timeouts and matches most workloads. Keep `RestartSec` at 5 seconds or higher to avoid log spam and contention.

### Fix and diagnostics

Recommended keepalive combination:

```ini
[Service]
Restart=on-failure
RestartSec=5s
StartLimitIntervalSec=60s
StartLimitBurst=5
TimeoutStartSec=30s
```

Diagnostic flow:

```bash
journalctl -u myapp.service -n 100 --no-pager
journalctl -u myapp.service -o cat --since "10 min ago" | tail -n 50
systemctl status myapp.service -l --no-pager
systemctl show myapp.service -p Restart -p RestartUSec -p StartLimitIntervalSec -p StartLimitBurst -p NRestarts
```

Look for three log patterns: `Main process exited, code=exited, status=1/FAILURE` for abnormal exits; `Killed` or `Out of memory` for OOM; `Start request repeated too quickly` for `StartLimit` throttling. For OOM, tune `Restart` but also check `MemoryMax`/`MemoryHigh` and host memory pressure; for port conflicts, fix `After` ordering or service startup sequence.

Verify keepalive:

```bash
sudo systemctl daemon-reload
sudo systemctl restart myapp.service
# Simulate a crash
sudo kill -9 $(systemctl show myapp.service -p MainPID --value)
sleep 6
systemctl status myapp.service
journalctl -u myapp.service --since "1 min ago" --no-pager
```

If `ActiveState` remains `active` and `NRestarts` increments, the restart policy is working. When throttling kicks in due to frequent crashes, fix the crash first, then clear the counter with `systemctl reset-failed myapp.service`.

## Put This Checklist into Your Daily Routine

The three pitfalls map to three verifications: autostart after reboot, environment parity with manual runs, and self-healing after crashes. Check them in order, running `daemon-reload` after each fix and re-verifying:

1. `systemctl cat` for `WantedBy`, `After`, `Type`; `daemon-reload` + `reenable`, then verify after a real reboot.
2. `systemctl show` and `journalctl -u` compared with manual `env`/`pwd`/`id`; fill in `WorkingDirectory`, `Environment`, `User`, and fix absolute `ExecStart` paths.
3. Configure `Restart`/`RestartSec`/`StartLimit`, simulate a failure with `kill -9 $MainPID`, and confirm `systemctl status` and `journalctl` recover automatically.

`systemctl enable --now` creates the autostart symlink and starts the service immediately — handy on first deployment, but you still need `daemon-reload` after editing the unit. Use `PartOf=` when you want linked restarts, and break database migrations into their own `Type=oneshot` unit that the main service declares `After=` on, instead of piling complex logic into `ExecStartPre`.

Also watch journal storage. By default systemd may write logs only to memory: if `Storage` is `auto` and `/var/log/journal` does not exist, the evidence from an overnight incident is lost on reboot. Enable `Storage=persistent` for critical services, then `journalctl --list-boots` and `journalctl -u myapp.service -b -1` let you review the previous boot. Skim `journalctl -u <service> --since today` instead of hammering `restart`; it gets you to the root cause faster.

In daily work, [Keyword Highlight](/usage/terminal-keyword-highlight) and [Local Encryption and Data Recovery](/usage/local-encryption) can make `journalctl` output easier to scan in remote sessions, and if a service must survive SSH disconnects, see [After SSH Disconnects: Is Your Program Still Running?](/blog/ssh-session-persistence) for the `systemd` vs `tmux` trade-offs. On boot-time and keepalive issues, though, reliability comes from the unit file itself — write it correctly, set up dependencies and restart policy, and you do not need any external keepalive tool.

## References

- systemd.service(5) — `man systemd.service`
- systemd.unit(5) — `man systemd.unit`
- systemd.exec(5) — `WorkingDirectory` / `Environment` / `User`
- `journalctl` / `systemctl` manual pages
