---
title: "SSH Won't Connect, Hangs, or Times Out? A 6-Step Path from Network to Server"
description: When SSH shows Connection refused, Connection timed out, or stalls during authentication, locate the fault by classifying the error, probing the client, tracing the network, checking sshd, examining the authentication phase, and tuning keepalives instead of blindly rebooting.
date: 2026-09-04
updated: 2026-09-04
author: Termark Team
---

# SSH Won't Connect, Hangs, or Times Out? A 6-Step Path from Network to Server

It is 2 a.m. and an alert wakes you. You need to log into a server to check the load, and SSH just hangs — no error, the cursor sits there blinking. You Ctrl+C and retry. This time: `Connection timed out`. Once more: `Permission denied (publickey)`. Three symptoms taking turns, so you start to suspect your own network. You reboot the router, tether to your phone, change the port, and half an hour later the server has not changed at all.

These three symptoms keep getting tangled together because they point at different layers: `timed out` usually means the network, `refused` usually means the server-side port, `permission denied` means authentication, and a silent hang is often buried in an obscure option on either end. An SSH connection happens in stages — DNS resolution, the TCP handshake, protocol negotiation, authentication, then opening a session. The stage where it stops is where the answer is buried. This guide gives a six-step path you can run in order on any machine: locate the stage first, then decide what to change. Blind reboots and config edits turn one incident into three.

## Step 1: Classify the error and locate the layer

The literal text of the error is your first clue. Sorting client output saves half the work:

- `Connection refused`: the TCP packet reached the target, but nothing is listening on that port. Look server-side — sshd is down, the port changed, or a firewall is actively rejecting.
- `Connection timed out`: the packet went out and nothing answered. Look at the network path — a firewall silently DROPping, a broken route, a wrong IP or port, or carrier blocking.
- `Connection reset by peer`: the other side sent an RST mid-handshake. Common with fail2ban, TCP wrappers, or a load balancer killing the connection.
- `No route to host`: routing itself cannot find the host, usually the local routing table, a VPN tunnel, or the gateway.
- `Permission denied (publickey)` / `Permission denied, please try again`: TCP and the handshake succeeded; authentication is the wall. The key was rejected, the password was wrong, or the server only allows a specific method.
- A silent hang with no error: TCP is established (or establishing) but nothing progresses. Usual suspects are reverse DNS, GSSAPI negotiation, or a method waiting for input.

Do not start changing things yet. On the same server, `refused` and `timed out` lead in opposite directions: for `refused` you look at the server port, for `timed out` you walk the network hop by hop. Classifying the error correctly turns "an unknown break" into "a break in one layer."

## Step 2: Use `ssh -vvv` to see where it actually stops

`-vvv` is SSH's built-in probe. It prints every step of the connection; you only need to read where it ends:

```bash
ssh -vvv user@example.com
```

Watch for these key lines:

- Nothing after `debug1: Connecting to example.com [1.2.3.4] port 22` — the TCP handshake never finished; go back to Step 3 and check the network.
- `debug1: Connection established` appears, then a long silence — TCP is up but negotiation or authentication is stuck; jump to Steps 4 and 5.
- Repeated `Authentications that can continue: publickey,password` or `Permission denied` — authentication is failing; see Step 5.
- `Connection established` appears but it takes a long time to reach authentication — the server is doing slow work before the handshake, typically reverse DNS or GSSAPI.

The same command can also settle DNS and port questions on their own:

```bash
# Does DNS resolve, and to which IP?
getent hosts example.com
dig +short example.com

# Is port 22 reachable? Note the difference between refused and timed out
nc -vz -w 5 example.com 22
```

If DNS resolution is slow, or it resolves to a stale IP you retired long ago, the problem may not be SSH at all. Set an explicit connect timeout with `ssh -o ConnectTimeout=10` so a default "hangs with no error" is not misread as a server problem. Once DNS and the port are ruled out, dig deeper into the network.

## Step 3: Walk the network path hop by hop

First confirm which machine you are testing from. "It works from my laptop" does not prove the path works — a laptop test on the office network says nothing about whether the cloud security group allows this source.

Verify layer by layer:

```bash
# Is the target IP reachable? Try ICMP first, then TCP 22
ping -c 3 1.2.3.4
nc -vz -w 5 1.2.3.4 22

# For cloud hosts, confirm the security group's inbound rules allow 22
# If there is a jump host, confirm the jump-to-target leg works
ssh -J jump.example.com user@target.example.com
```

Firewall DROP and REJECT produce different symptoms, and that is itself a clue: REJECT usually shows up as `Connection refused` or `Connection reset`, while DROP shows up as `Connection timed out`. When you see `timed out`, suspect a silently dropping firewall or a routing black hole before you suspect sshd.

Two easy-to-miss causes behind "ping works but SSH hangs":

- **MTU / fragmentation**: large packets do not pass while small ones do. ping works because ICMP packets are small, but the larger packets exchanged during the SSH negotiation are dropped. Confirm with a do-not-fragment probe:

```bash
ping -M do -s 1472 1.2.3.4
```

If 1472 bytes fail while 1400 bytes pass, the tunnel or link MTU is too small — lower the interface MTU or fix PMTUD.

- **Carrier or policy blocking of port 22**: some mobile networks, hotels, and corporate networks restrict port 22, showing up as random `timed out`. If the port is genuinely blocked, switch to a high port or route through a VPN or SSH tunnel.

Over a tunnel, timeouts behave differently from a direct connection — how the tunnel is established, held, and broken matters before the inner SSH. See the [port forwarding configuration](/usage/port-forwarding) for how local and remote forwarding differ, and confirm the tunnel itself is alive before debugging the inner SSH.

## Step 4: Get on the server and check sshd itself

If the network layer checks out, or you suspect the problem is server-side, confirm sshd's state on the target directly:

```bash
sudo systemctl status sshd --no-pager
sudo ss -lntp | grep sshd
```

Check four things:

1. **Is sshd running?** If the process exited, nothing is there to accept connections.
2. **Which port and address is it listening on?** `ss -lntp` shows `*:22`, `127.0.0.1:22`, or an IPv6-only `[::]:22`. A changed port, a loopback-only listener, or a listener bound to one interface all produce external `refused` or `timed out`.
3. **Does the config match what you think it is?** In `/etc/ssh/sshd_config`, check `Port`, `ListenAddress`, `AllowUsers`, `DenyUsers`, and `PasswordAuthentication`. Read the effective values with `sshd -T`, not the file you edited:

```bash
sudo sshd -T | grep -E '^(port|listenaddress|passwordauthentication|allowusers|maxstartups)'
```

4. **Are you being blocked by a security policy?** Tools like fail2ban and denyhosts ban an IP after repeated failures, and the symptom is exactly `Connection reset by peer`. Check the server logs:

```bash
sudo journalctl -u sshd --since '15 minutes ago' --no-pager
# On Debian/Ubuntu you can also read
sudo tail -n 100 /var/log/auth.log
```

If the log shows your IP being refused or banned, look at the fail2ban jail instead of trying more passwords.

There is also a subtle "connects but is refused" cause: `MaxStartups`. It caps the number of connections that are connected but not yet authenticated; beyond that, new connections are closed with `ssh_exchange_identification: Connection closed by remote host`. Under attack or a burst of concurrency, this threshold is exhausted first. Do not skip resources either: exhausted memory stops sshd from forking child processes, and exhausted file descriptors can drop connections before authentication — check `free -h` and `sudo ss -s` once each.

## Step 5: Authentication stalls or fails repeatedly

TCP is up and `Connection established` prints, but authentication hangs — half of this layer is configuration, half is waiting.

A slow handshake is classically caused by server-side reverse DNS. `UseDNS yes` (the default on some distros) makes sshd reverse-resolve the client IP before authentication; when the DNS server responds slowly, every connection waits a few seconds to tens of seconds for nothing:

```bash
sudo sshd -T | grep usedns
```

On the client, `GSSAPIAuthentication` also slows things down — without Kerberos, the client tries GSSAPI negotiation first and only falls back after it fails. If you do not want that delay, disable it in the client `~/.ssh/config`:

```text
Host example.com
    GSSAPIAuthentication no
```

For **authentication failures**, separate the cases:

- Password auth is disabled but you only brought a password: several `Permission denied, please try again`, then `Permission denied (publickey)`. Confirm the server's `PasswordAuthentication` value.
- The key is not accepted: first check whether the local agent has loaded the right key, then the permissions of the server-side files.

```bash
ssh-add -l
# Server side: ~/.ssh should be 700, authorized_keys should be 600
ls -ld ~/.ssh
ls -l ~/.ssh/authorized_keys
```

- Two-factor stalls: when the server enforces OTP, keyboard-interactive, or `AuthenticationMethods` multi-factor, the prompt may not appear, or it appears but your token is out of sync. For this interactive flow, see [Automatic OTP interactive auth](/usage/otp-interactive-auth) for when the verification code should be entered — it addresses the question of where in the flow the code belongs.

Use `ssh -v` to read the server's final `Authentications that can continue` line; it tells you exactly which methods remain available. Satisfy the list one by one rather than blindly retrying passwords.

## Step 6: Disconnects and freezes after you are in

The connection establishes and authentication succeeds, but it drops mid-session or the terminal freezes — this has moved past "cannot connect" into "cannot keep it," but the path is just as structured.

The number-one cause of idle drops is NAT or firewall idle-connection reaping: a middlebox silently removes the connection after a period of no traffic, and SSH itself does not know until your next keystroke reveals it is gone. The fix is periodic heartbeat traffic; client and server each have their own knobs:

```text
# Client ~/.ssh/config
Host *
    ServerAliveInterval 30
    ServerAliveCountMax 3
```

`ServerAliveInterval` is how often the client probes, and `ServerAliveCountMax` is how many unanswered probes before it declares the connection dead. The server-side equivalents are `ClientAliveInterval` and `ClientAliveCountMax`. Note that `TCPKeepAlive` and `ServerAlive` are not the same thing: the former is the TCP-level keepalive, whose default interval is long (usually two hours) and nearly useless against "NAT reaps in tens of seconds." Do not expect it to save you.

A frozen terminal with the connection still alive is usually not the network — a remote process is dragging the session down: output flooding, a full disk, or a command waiting on input that will never come. This "connection alive, interaction dead" state is not fixed by heartbeats. The right fix is to keep the remote session independent of the SSH connection, using a terminal multiplexer (tmux, screen) to hold the session on the server so you can reconnect and recover the scene after a drop or freeze.

During diagnosis, keeping commands, logs, and config checks in one reproducible session saves a lot of back-and-forth; with Termark, terminal and SFTP share a workspace, so reading logs and pulling config files does not require switching tools. That improves the operating path; it does not decide for you which layer is broken.

## A checklist to run in order

```bash
# 1. Classify the error: refused / timed out / reset / permission denied / hang
ssh -vvv user@example.com

# 2. Verify DNS and port separately
getent hosts example.com
nc -vz -w 5 example.com 22

# 3. Network path: ping, MTU, jump host
ping -M do -s 1472 1.2.3.4

# 4. sshd state and effective config
sudo systemctl status sshd --no-pager
sudo ss -lntp | grep sshd
sudo sshd -T | grep -E '^(port|listenaddress|passwordauthentication|maxstartups|usedns)'

# 5. Server logs: banned or slow handshake?
sudo journalctl -u sshd --since '15 minutes ago' --no-pager

# 6. Authentication and keepalive
ssh-add -l
# Add ServerAliveInterval / ServerAliveCountMax to the client config
```

The order is part of the answer: classify the error first, use `-vvv` to pin down the stage, then move through network, server, authentication, and keepalive in turn. Change one thing at a time, retest with the same `ssh -vvv`, and record the before/after difference. SSH failing to connect is never one disease but a stack of "which link did not respond" — finding that one link beats rebooting the whole thing every time.

## References

- [OpenSSH client manual: connection and keepalive options in ssh_config](https://man.openbsd.org/ssh_config)
- [OpenSSH server manual: authentication and limits in sshd_config](https://man.openbsd.org/sshd_config)
- [OpenSSH manual: the ssh command's verbose output options](https://man.openbsd.org/ssh)
- [Termark port forwarding configuration](/usage/port-forwarding)
- [Termark automatic OTP interactive auth](/usage/otp-interactive-auth)
