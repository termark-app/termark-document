---
title: Logs Filling Up Your Disk? Tame journald and logrotate for Good
description: journald logs growing without limit and /var/log filling your disk? Use journalctl --disk-usage to diagnose, --vacuum to clean, then configure SystemMaxUse and logrotate to fix it for good — with copy-paste commands and config templates.
date: 2026-09-01
updated: 2026-09-01
author: Termark Team
---

# Logs Filling Up Your Disk? Tame journald and logrotate for Good

Few ops people have not watched logs eat a disk alive. Unlike business data, logs have no clear ceiling. Unlike a database, nobody babysits them. They just keep writing, line after line, until `/var/log` has swallowed a dozen gigabytes, journald's binary logs are quietly ballooning in `/var/log/journal`, and services start failing to write, throwing errors, and misbehaving in ways that are hard to explain.

This article works in three steps: locate whether journald or plain-text logs are the culprit, clean up safely, then set the caps so logs manage themselves from now on.

## Diagnose first: how much is it, and who is writing

Linux logs fall into two families with completely different investigation paths:

- **journald binary logs**: systemd services write stdout/stderr to the journal by default (`StandardOutput=journal`), stored under `/var/log/journal` (persistent) or `/run/log/journal` (volatile, wiped on reboot). They are not plain text, so `du` on individual files tells you nothing — use `journalctl` instead.
- **Traditional text logs**: nginx, MySQL, and countless applications write their own `.log` files under `/var/log/`, handled by `logrotate`.

Run these to establish the current state:

```bash
df -h /var/log

journalctl --disk-usage
# Journals take 3.4G on disk.

sudo du -sh /var/log/* 2>/dev/null | sort -rh | head -10
sudo du -sh /var/log/journal 2>/dev/null
```

If `journalctl --disk-usage` matches the used space in `df -h`, journald is almost certainly the cause. If a directory like `/var/log/nginx` is the big consumer, it is unrotated text logs. The fixes differ — do not mix them up. When troubleshooting remotely, running these commands over SSH with a client like [Termark](https://www.termark.app/?utm_source=docs&utm_medium=blog&utm_campaign=log_rotation_journald) and pulling a large log file back locally is the fastest way to get oriented.

## journald: binary logs need a ceiling too

Many people assume systemd manages journal size on its own. It does not, strictly speaking: `SystemMaxUse` defaults to 10% of the underlying filesystem size (capped at 4G), and `SystemKeepFree` defaults to 15% (capped at 4G). On a small server where disk is already tight, 10% can be several gigabytes — plenty to push a partition into the danger zone.

### Stop the bleeding: vacuum removes only the old

The `--vacuum` family cleans up archived old entries by size, time, or file count. Active files still being written are untouched, so it is safe:

```bash
sudo journalctl --vacuum-size=200M   # shrink the total to 200M
sudo journalctl --vacuum-time=2weeks # keep only the last two weeks
sudo journalctl --vacuum-files=5     # keep only 5 journal files
journalctl --disk-usage
```

Space returns immediately, and no service needs a restart.

### Fix the root cause: journald.conf, once

Stopping the bleeding only buys time until next time. Put the caps in `/etc/systemd/journald.conf` so the journal constrains itself from here on:

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

What each directive does:

- `SystemMaxUse=` — the disk ceiling for the journal; the oldest entries are dropped first once exceeded;
- `SystemKeepFree=` — free space to reserve on the filesystem; takes priority over `SystemMaxUse`;
- `SystemMaxFileSize=` — the size limit for a single journal file;
- `MaxRetentionSec=` — how long entries are kept at most, a second guard alongside `SystemMaxUse`;
- `MaxFileSec=` — the maximum lifetime of a single file, controlling rotation cadence.

The volatile runtime journal (`/run`) is governed by `RuntimeMaxUse=` and `RuntimeKeepFree=` instead, with the same 10%/15% defaults (capped at 4G). Since `/run` is usually tmpfs, it is worth shrinking these too when memory is tight.

After editing, run `systemctl restart systemd-journald` for the changes to take effect. Configure this once, and the journal will never grow without limit again.

## logrotate: keep the text logs under /var/log in check

journald handles systemd services, but plenty of programs still write their own text logs to `/var/log`. Those rely on `logrotate`, which runs once a day via cron (`/etc/cron.daily/logrotate`) or the systemd timer (`logrotate.timer`).

The system default in `/etc/logrotate.conf` is conservative. What actually matters is the per-service configuration under `/etc/logrotate.d/`. A typical application-log config looks like this:

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

What each directive does:

- `daily` / `weekly` / `monthly` — rotation period; `size 100M` also rotates once the file exceeds 100M;
- `rotate 7` — keep 7 historical files, then delete older ones;
- `compress` — gzip old logs; `delaycompress` leaves the most recent historical file uncompressed until the next rotation, so the app can keep writing;
- `missingok` — do not error if the log file is absent; `notifempty` — do not rotate empty files;
- `copytruncate` — copy then truncate the original in place (explained below).

### copytruncate, or create + postrotate?

This is the most common logrotate trap, and the usual reason for "logs stopped updating after rotation." The two mechanisms differ fundamentally:

- **`copytruncate`**: copies the original into an archive, then truncates the original to zero. File handles and inodes stay the same, so the program keeps writing with no changes needed. The trade-off is a tiny data-loss window between the truncate and the next write, plus extra IO for copying large files.
- **`create` + a `postrotate` signal**: renames the original into an archive, creates a fresh file with the same name, then uses a `postrotate` command (like `kill -USR1`) to tell the program to reopen its log. No data loss, but the program must support "reopen the log on signal."

nginx is the canonical example of the latter:

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

The rule of thumb is simple: if the program can reopen its log on a signal (nginx's `-USR1`, `SIGHUP` for many daemons), use `create + postrotate`. If it will not respond and just keeps writing to the original handle (many small self-logging programs), fall back to `copytruncate`.

### Verify first, then trigger manually

```bash
sudo logrotate -d /etc/logrotate.conf   # debug mode: print what it would do, without doing it
sudo logrotate -f /etc/logrotate.conf   # force a run to apply immediately
```

Always run `-d` first and read the output to confirm nothing is skipped or syntactically wrong, then force with `-f`.

## Five minutes now for a future without log-driven alerts

Cleanup fixes this incident. The three items below fix "will this happen again?"

1. **Cap both journald and logrotate.** `SystemMaxUse` + `SystemKeepFree` are the highest-ROI settings on the journald side; adding a rotation rule under `/etc/logrotate.d/` for every log that writes to a file is the single most important thing on the text-log side.

2. **Alert before the disk fills.** Set a warning at 80% and critical at 85% for the partition holding `/var/log`. A quick `journalctl --disk-usage` and `du -sh /var/log` during routine checks surfaces the trend early.

3. **Centralize instead of hoarding history on one box.** Logs ultimately belong somewhere searchable and alertable (Loki, ELK, or a remote journald); keep only the recent window locally for incident forensics. Same principle as not letting Docker act as a log warehouse. Where and how long to keep logs and data is fundamentally a storage policy — see [Data Storage Path](/usage/data-storage-path) for related patterns.

## One-page checklist — save it

```bash
journalctl --disk-usage
sudo journalctl --vacuum-size=200M
sudo du -sh /var/log/* | sort -rh | head
sudo logrotate -d /etc/logrotate.conf
sudo systemctl restart systemd-journald
```

Order: diagnose with `--disk-usage` and `du`, clean with `--vacuum` or `logrotate -f`, then set the caps in `journald.conf` and `/etc/logrotate.d/`. Next time the logs try to quietly fill the disk, they will stop themselves first.

---

When a log problem hits, the first step is always to get on the machine and see who is writing — not to delete files blindly. Connect with [Termark](https://www.termark.app/?utm_source=docs&utm_medium=blog&utm_campaign=log_rotation_journald&audience=ops) and run `journalctl` and `du` right in the terminal; SFTP is there when you need to pull a large log back for closer inspection. Set the caps once, and logs filling your disk will largely stop coming for you.

## References

- [systemd-journald.conf man page](https://www.freedesktop.org/software/systemd/man/systemd-journald.conf.html)
- [journalctl man page](https://www.freedesktop.org/software/systemd/man/journalctl.html)
- [logrotate man page](https://linux.die.net/man/8/logrotate)
- [systemd journal file format](https://systemd.io/JOURNAL_FILE_FORMAT/)
