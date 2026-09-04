---
title: "Why SFTP Fails on OpenWrt Default SSH (Dropbear)"
description: "Termark shows SFTP subsystem error on OpenWrt? The default Dropbear SSH server does not include SFTP — fix it by installing openssh-sftp-server or switching to OpenSSH."
outline: deep
---

# Why SFTP Fails on OpenWrt Default SSH

If Termark connects to SSH normally but the SFTP panel shows the following error on an OpenWrt device, it is not a Termark bug — OpenWrt uses **Dropbear** by default, which does not include SFTP:

> **Failed to load files: session not found: create SFTP client failed: error receiving version packet from server: server unexpectedly closed connection: unexpected EOF**

Dropbear closes the channel when it receives an `sftp` subsystem request but cannot find the `sftp-server` binary, so the client never receives the version packet and reports `unexpected EOF`. Equivalent messages include `subsystem request failed` / `sftp-server not found` / `unable to initialize SFTP`.

## Symptom

- SSH terminal works fine.
- SFTP panel fails to open, or file transfer reports `unable to initialize SFTP` / `subsystem not found`.
- The same Termark configuration works on Debian / Ubuntu / CentOS hosts.

## Root Cause: Dropbear vs OpenSSH

| | Dropbear (OpenWrt default) | OpenSSH |
|---|---|---|
| Size | ~300 KB, for embedded devices | ~6 MB |
| Purpose | Lightweight SSH shell + SCP | Full SSH suite |
| SFTP support | **No** — `sftp-server` binary is not bundled | Yes — `/usr/lib/openssh/sftp-server` included |

OpenWrt chooses Dropbear to save flash space. SFTP is a separate subsystem (`sftp-server` executable) that Dropbear never ships. Without it, the SSH server has nothing to handle the client's `sftp` subsystem request, so it rejects the channel.

## How to Verify

On the OpenWrt device:

```bash
# 1. Which SSH server is running?
ps | grep -E 'dropbear|sshd'

# 2. Is sftp-server present?
ls -l /usr/libexec/sftp-server /usr/lib/sftp-server 2>&1

# 3. Dropbear has no Subsystem config
cat /etc/config/dropbear 2>&1 | head -20
```

If `sftp-server` is missing and `dropbear` is running, that confirms the cause.

## Fixes (pick one)

### Option 1: Install `openssh-sftp-server` (recommended, ~1 MB)

Keeps Dropbear as the SSH server and only adds the SFTP subsystem:

```bash
opkg update
opkg install openssh-sftp-server

# Verify
ls -l /usr/libexec/sftp-server
# should show: -rwxr-xr-x 1 root root ... /usr/libexec/sftp-server
```

No reboot or config change is needed — Dropbear will automatically find `sftp-server` on the next SFTP connection. Reopen the SFTP panel in Termark to verify.

If Termark still fails, ensure Dropbear is recent enough (OpenWrt 21.02+). Older builds need a symlink:

```bash
mkdir -p /usr/libexec
ln -sf /usr/lib/sftp-server /usr/libexec/sftp-server 2>/dev/null
```

### Option 2: Use SCP Instead

If flash space is extremely tight and you cannot install anything, use SCP for single-file transfers. Termark's SFTP panel requires SFTP, so this is only a workaround outside Termark:

```bash
scp file.bin root@openwrt:/tmp/
```

### Option 3: Replace Dropbear with OpenSSH (heavier)

Only if you need full OpenSSH features (key restrictions, richer `sshd_config`):

```bash
opkg update
opkg install openssh-server openssh-sftp-server
/etc/init.d/dropbear disable
/etc/init.d/sshd enable
/etc/init.d/sshd start
```

Cost: ~5–6 MB more flash and higher RAM. Most users should prefer Option 1.

## Still Not Working?

1. **Installed but still fails** — reconnect SSH after install; some Dropbear versions cache subsystem lookup per connection.
2. **No space left** — run `df -h` and `opkg list-installed | wc -l` to check flash usage; remove unused packages first.
3. **Permission error after SFTP connects** — SFTP now works, but the login user lacks read/write permission on the target path — check `ls -ld /path`.

## Recommendation for Termark Users

For OpenWrt routers / NAS / soft-routers, **Option 1 is the best balance**: one `opkg install` (~1 MB) fixes SFTP for Termark and any other SFTP client, without replacing the lightweight SSH server.

## Related pages

- [SFTP CWD Tracking](/usage/sftp-cwd-tracking)
