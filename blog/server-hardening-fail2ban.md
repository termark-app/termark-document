---
title: "Stop SSH Brute Force: 5 Steps with Port Change, Key-Only, and fail2ban"
description: Harden SSH against brute-force attacks in five production-safe steps — change the default port, enforce key-only authentication, block password and root login, deploy fail2ban, and verify without locking yourself out.
date: 2026-08-27
updated: 2026-08-27
author: Termark Team
---

# Stop SSH Brute Force: 5 Steps with Port Change, Key-Only, and fail2ban

It is 2:14 AM. Your monitor reports repeated SSH login failures from three IP ranges. You check the auth log and the same pattern has been running for days:

```
Failed password for invalid user admin from 43.154.12.88 port 52341
Failed password for root from 43.154.12.88 port 52342
Failed password for invalid user deploy from 43.154.12.88 port 52343
```

Nothing is breached — yet. The server wastes CPU on thousands of useless logins a day and a single weak password is all an attacker needs. Blocking one IP will not help — brute force is permanent background noise for any host with port 22 open.

This guide gives you a five-step hardening path for Ubuntu/Debian or RHEL/Rocky: change the port to cut noise, close the password attack surface, add automatic blocking with fail2ban, and verify without locking yourself out.

> **Scope:** This article hardens OpenSSH Server (`sshd`) on Linux. A desktop client like [Termark](https://www.termark.app/?utm_source=docs&utm_medium=blog&utm_campaign=server_hardening_fail2ban) makes the workflow smoother, but the security decisions live on the server.

## Before you start: keep a lifeline open

Every SSH lockout follows the same script: you reload `sshd_config` and the new settings reject your next login. Prevent it with one rule:

**Never close your existing session until a new connection succeeds.**

Open two terminals. Make changes from one and test from the other. On cloud hosts, confirm console access first. Snapshot and back up:

```bash
sudo ss -tlnp | grep sshd
sudo sshd -T | grep -E '^(port|pubkeyauthentication|passwordauthentication|permitrootlogin|challenge)'
sudo tail -n 100 /var/log/auth.log 2>/dev/null || sudo journalctl -u sshd --since '1 hour ago' --no-pager | tail -n 100

sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak.$(date +%F)
```

## Step 1: Move SSH off port 22

Changing the port does not fix authentication — anyone can scan your host. It removes you from the cheapest automated scanning: bots that try `root`/`admin` against every `22/tcp` they find. On a busy host this cuts auth noise by >90%.

Pick a port between 1024 and 65535 that is not in use. Avoid `2222` (also heavily scanned). Example: `22222`.

### 1.1 Check availability and open the firewall first

```bash
# Is the candidate port already listening?
sudo ss -tlnp | grep 22222

# Ubuntu/Debian with UFW — allow the new port BEFORE you switch
sudo ufw allow 22222/tcp comment 'SSH'
sudo ufw status numbered

# RHEL/Rocky/Alma with firewalld
sudo firewall-cmd --add-port=22222/tcp --permanent
sudo firewall-cmd --reload
sudo firewall-cmd --list-ports

# Provider firewall / security group: also allow 22222/tcp there.
# Skipping this locks you out at the network layer.
```

On SELinux-enforcing systems (RHEL family), label the new port:

```bash
sudo semanage port -a -t ssh_port_t -p tcp 22222 2>/dev/null \
  || sudo semanage port -m -t ssh_port_t -p tcp 22222
```

### 1.2 Change sshd and reload

```bash
sudo tee -a /etc/ssh/sshd_config <<'EOF'
# Custom SSH port — do not leave both 22 and 22222 open long-term
Port 22222
EOF

# Never reload without a syntax check
sudo sshd -t && echo "syntax ok"

sudo systemctl reload sshd
# Older distributions may use: sudo systemctl reload ssh

sudo ss -tlnp | grep sshd
```

### 1.3 Test from a second session

```bash
# From your second terminal or a new Termark tab
ssh -p 22222 user@your-server -v

# Inside the new session, confirm the listener
sudo ss -tlnp | grep sshd
```

Only when `ssh -p 22222` succeeds should you close port 22. Leaving both open doubles the surface you monitor. Save the port locally:

```bash
# ~/.ssh/config
Host myserver
    HostName your-server.example.com
    Port 22222
    User your-user
```

## Step 2: Disable password authentication and enforce key-only login

If passwords are accepted, brute force has something to guess. The most effective single change is to require public-key authentication and reject passwords entirely.

### 2.1 Create and deploy your key

On your **local machine**, not the server:

```bash
# ed25519 is the modern default — short, fast, secure
ssh-keygen -t ed25519 -C "your-email@example.com"

# Copy the public key (use the new port if you already moved it)
ssh-copy-id -p 22222 user@your-server

# Verify key login works
ssh -p 22222 user@your-server
```

On the server, permissions must be exact — `sshd` will ignore keys otherwise:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

Protect the private key with a passphrase. A client like Termark can store keys with client-side encryption so you avoid copying them over email or chat.

### 2.2 Turn off passwords and root login

Edit `/etc/ssh/sshd_config`. Directive names matter — `PasswordAuthentication`, `ChallengeResponseAuthentication`, and `KbdInteractiveAuthentication` are distinct:

```bash
sudo tee -a /etc/ssh/sshd_config <<'EOF'
# Key-only authentication
PubkeyAuthentication yes
PasswordAuthentication no
ChallengeResponseAuthentication no
KbdInteractiveAuthentication no
UsePAM yes
PermitRootLogin no
PermitEmptyPasswords no
X11Forwarding no
AllowAgentForwarding no
EOF
```

What each line does:

- `PubkeyAuthentication yes` — allow keys.
- `PasswordAuthentication no` + `ChallengeResponseAuthentication`/`KbdInteractiveAuthentication no` — disable all password prompts (set both challenge variants for cross-version compatibility).
- `UsePAM yes` — keep PAM for session handling without allowing password logins.
- `PermitRootLogin no` — deny direct `root`. Use a normal user with `sudo`.
- `PermitEmptyPasswords no` — block blank passwords.

Optionally restrict logins:

```bash
sudo tee -a /etc/ssh/sshd_config <<'EOF'
AllowUsers deploy ops
EOF
```

Validate and reload:

```bash
sudo sshd -t && echo "syntax ok"
sudo systemctl reload sshd
```

### 2.3 Prove that passwords are rejected

```bash
ssh -p 22222 -o PreferredAuthentications=password -o PubkeyAuthentication=no user@your-server
# Expected: Permission denied (publickey).

# Key login from an allowed host should still work
ssh -p 22222 user@your-server
```

If the prompt still appears, a `Match` block lower in `sshd_config` is overriding the global setting — check `sshd -T`.

## Step 3: Add automatic blocking with fail2ban

With key-only auth, brute force cannot guess a password — but scanners still hammer the service and fill logs. fail2ban watches the auth log and temporarily bans repeat offenders. It complements key-only auth.

### 3.1 Install and enable

```bash
# Debian / Ubuntu
sudo apt update && sudo apt install -y fail2ban

# RHEL / Rocky / Alma
sudo dnf install -y epel-release
sudo dnf install -y fail2ban
sudo systemctl enable --now fail2ban

sudo systemctl status fail2ban --no-pager
sudo fail2ban-client status
```

### 3.2 Configure the sshd jail

Never edit `jail.conf` directly — it is overwritten on upgrades. Create `jail.local`:

```bash
sudo tee /etc/fail2ban/jail.local <<'EOF'
[DEFAULT]
# Whitelist your own networks — never ban yourself
ignoreip = 127.0.0.1/8 ::1 10.0.0.0/8 172.16.0.0/12 192.168.0.0/16

backend = systemd
bantime  = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled  = true
port     = 22222
filter   = sshd
# Firewall action — pick the one matching your setup:
# UFW:       action = ufw
# firewalld: action = firewallcmd-ipset
# iptables:  action = iptables-multiport
EOF
```

Key fields:

- `ignoreip` — office, VPN, deploy runners. A typo can lock you out.
- `backend = systemd` — for `journald` hosts; use `backend = auto` for file logging.
- `bantime / findtime / maxretry` — 5 failures in 10 min → 1h ban. Consider `24h` on heavily scanned hosts.
- `port = 22222` — must match Step 1.

Apply:

```bash
sudo fail2ban-client reload
sudo fail2ban-client status sshd
```

### 3.3 Verify a ban

Five failed attempts from a test IP should produce:

```bash
sudo fail2ban-client status sshd
# Status for the jail: sshd
# |- Filter
# |  |- Currently failed: 0
# |  |- Total failed:     5
# `- Actions
#    |- Currently banned: 1
#    `- Banned IP list:   203.0.113.45

# Confirm the firewall rule exists
sudo iptables -L f2b-sshd --line-numbers 2>/dev/null
sudo ufw status numbered 2>/dev/null | grep -i f2b

# Check fail2ban's own log
sudo tail -n 100 /var/log/fail2ban.log
sudo journalctl -u fail2ban --since '10 minutes ago' --no-pager
```

If bans never trigger, verify the filter matches your log format:

```bash
sudo fail2ban-regex /var/log/auth.log /etc/fail2ban/filter.d/sshd.conf
# or for journald:
sudo journalctl -u sshd --since '1 hour ago' --no-pager | fail2ban-regex - /etc/fail2ban/filter.d/sshd.conf
```

## Step 4: Verify the whole chain without locking yourself out

Run these checks in order before you consider the work done:

```bash
# 1. Syntax
sudo sshd -t && echo "sshd syntax ok"

# 2. Effective config (after all Match blocks)
sudo sshd -T | grep -E '^(port|pubkeyauthentication|passwordauthentication|permitrootlogin|allowusers)'

# 3. Listening sockets
sudo ss -tlnp | grep sshd

# 4. Firewall — server side and from outside
sudo ufw status numbered 2>/dev/null; sudo firewall-cmd --list-ports 2>/dev/null
nc -vz -w 3 your-server.example.com 22222

# 5. Real login with verbose auth trace
ssh -p 22222 -v user@your-server 2>&1 | grep -E 'Authenticat|Offering public key|Accepted'

# 6. Negative test — password must be rejected
ssh -p 22222 -o PubkeyAuthentication=no -o PreferredAuthentications=password user@your-server
```

Common pitfalls:

- **Port changed but firewall still blocks it.** Allow the port before reloading. If already locked out, use the provider console.
- **`PasswordAuthentication no` has no effect.** A `Match` block lower in the file overrides the global value. Move globals above any `Match` section.
- **fail2ban never bans.** Check `backend` and `port`, then run `fail2ban-regex` as above.
- **SELinux denies the new port.** Check `sudo ausearch -m avc -ts recent | grep sshd` and apply `semanage port` from Step 1.
- **`AllowUsers` omits a deploy account.** Every SSH user, including CI, must be listed. Test each one.

Rollback if needed:

```bash
sudo cp /etc/ssh/sshd_config.bak.$(date +%F) /etc/ssh/sshd_config
sudo sshd -t && sudo systemctl reload sshd
```

## Step 5: Monitor, tune, and unban safely

Hardening is not one-and-done. You need visibility into bans and a way to recover from false positives.

### 5.1 Daily log review

```bash
# Who is currently banned?
sudo fail2ban-client status sshd

# Top attackers in the last 24 hours
sudo journalctl -u sshd --since '24 hours ago' --no-pager \
  | grep -E 'Failed|Invalid user' | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head -20

# What did fail2ban do?
sudo grep -E 'Ban|Unban' /var/log/fail2ban.log | tail -n 50
```

Ship `auth.log`/`journald` and `fail2ban.log` to your aggregator. Alert on banned-IP growth or `Accepted` logins from unusual ASNs — not on every `Failed password`.

### 5.2 Unban and whitelist

```bash
# Unban a single IP
sudo fail2ban-client set sshd unbanip 203.0.113.45

# Permanent whitelist — add to jail.local and reload
sudo tee -a /etc/fail2ban/jail.local <<'EOF'
[DEFAULT]
ignoreip = 127.0.0.1/8 ::1 203.0.113.45
EOF
sudo fail2ban-client reload
```

For dynamic IPs, whitelist a VPN range rather than a single address.

### 5.3 Tune to your threat model

- **Small team, low traffic:** `maxretry = 5`, `bantime = 1h` is sufficient.
- **Heavily scanned public host:** `maxretry = 3`, `bantime = 24h`, with a persistent ban database.
- **Behind NAT or a proxy:** Ensure `sshd` logs the real client IP, not the proxy's, or fail2ban will ban the proxy.

Add a weekly runbook check:

```bash
sudo fail2ban-client status sshd
sudo sshd -T | grep -E '^(port|passwordauthentication|permitrootlogin)'
sudo ufw status numbered 2>/dev/null
```

## A safe-order checklist you can reuse

```bash
# 0. Keep one session open — test from a second one
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak.$(date +%F)

# 1. Move port — allow firewall first
sudo ufw allow 22222/tcp &&sudo ufw status numbered
# Edit /etc/ssh/sshd_config: Port 22222
sudo sshd -t && sudo systemctl reload sshd
ssh -p 22222 user@host -v   # must succeed before closing port 22

# 2. Key-only — deploy key first, then disable passwords
ssh-copy-id -p 22222 user@host
# Edit sshd_config: PasswordAuthentication no, PermitRootLogin no
sudo sshd -t && sudo systemctl reload sshd
ssh -p 22222 -o PubkeyAuthentication=no user@host  # must fail

# 3. fail2ban — jail.local with correct port and backend
sudo apt install -y fail2ban && sudo tee /etc/fail2ban/jail.local <<'EOF'
[DEFAULT]
ignoreip = 127.0.0.1/8 ::1
backend = systemd
bantime = 1h
findtime = 10m
maxretry = 5
[sshd]
enabled = true
port = 22222
EOF
sudo fail2ban-client reload && sudo fail2ban-client status sshd

# 4. Verify
sudo sshd -T | grep -E 'port|passwordauth|permitroot'
sudo ss -tlnp | grep sshd

# 5. Unban when needed
sudo fail2ban-client set sshd unbanip <IP>
```

Order matters: firewall before port change, key deployment before disabling passwords, syntax check before reload, new login before closing the old port.

## Conclusion: Make brute force boring

You cannot stop the internet from knocking — you can make the door boring to knock on. A non-standard port removes cheap scans, key-only auth removes the guessable secret, `PermitRootLogin no` removes the top target, and fail2ban removes persistence. Together they turn thousands of daily failures into an occasional auto-banned curiosity.

Keep a second session open, validate with `sshd -t` and `sshd -T`, prove passwords are rejected, and monitor bans instead of ignoring logs.

---

## References

- [OpenSSH sshd_config manual — Port, Authentication, and Match](https://man.openbsd.org/sshd_config)
- [OpenSSH security — key-based authentication](https://www.openssh.com/manual.html)
- [fail2ban manual — jails, filters, and actions](https://fail2ban.readthedocs.io/en/latest/)
- [fail2ban sshd jail and systemd backend](https://fail2ban.readthedocs.io/en/latest/jail/)
- [Ubuntu Server Guide — OpenSSH](https://ubuntu.com/server/docs/service/openssh)
- [Termark — modern SSH terminal and data storage](https://www.termark.app/)
- [Termark documentation — data storage and operations](/usage/data-storage-path)
