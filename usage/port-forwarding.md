---
title: "Port Forwarding"
description: "Use Termark's port forwarding: local, remote, and dynamic forwarding, plus auto-start and active-connection management."
outline: deep
---

# Port Forwarding

Termark has built-in port forwarding that reuses your existing SSH connection to set up local (`-L`), remote (`-R`), and dynamic (`-D`) forwarding — no extra tools needed.

## Forwarding Types

Switch the forward type when creating or editing a rule:

- **Local forwarding (-L)**: Maps a remote service reachable by the SSH host (jump host) to a local port. Common for reaching an intranet database or web service through a jump host.
- **Remote forwarding (-R)**: Exposes a local service through the SSH host, letting remote end reach the local service via its port.
- **Dynamic forwarding (-D)**: Listens on a local HTTP or SOCKS5 proxy port and routes traffic through the SSH host to target addresses. Useful as a temporary proxy.

The SSH host can be either a local host or a NextTerminal asset, selectable directly in the creation dialog.

## Creating a Rule

1. Open **Port Forwarding** and click **Create** in the top-right corner.
2. **Rule name** (required): e.g. "Access remote MySQL".
3. **Forward type**: pick local / remote / dynamic.
4. **SSH host** (required): choose the SSH host or NextTerminal asset acting as the forwarding entry (jump host).
5. Fill in ports and addresses per type:
   - **Local forwarding**: local listen port, remote host, remote port. The remote host is relative to the SSH host; use `localhost` for the SSH host itself (e.g. remote MySQL as `localhost:3306`, local listen `3307`).
   - **Remote forwarding**: local service port, SSH host listen port. The SSH host listens on `0.0.0.0:<port>` and forwards to your machine.
   - **Dynamic forwarding**: proxy protocol (SOCKS5 or HTTP), local proxy port.
6. Optional: enable **Auto-start on launch** (start this rule automatically when the app starts).
7. Click **Confirm**.

## Managing Rules

The rule list shows name, status, and the forwarding chain description, and can be searched by name, SSH host, target address, or port.

- **Status**: Running / Reconnecting / Stopped / Error. Click **Stop** while running; click **Start** while stopped.
- **Active connections**: for a running rule, view current connections (source address, listen address, opened at, duration), auto-refreshed every 2 seconds.
- **Auto-start on launch**: determines whether the rule starts automatically when the app starts.
- **Edit / Delete**: stop the rule first — running rules cannot be edited or deleted.

## Configuration Examples

### Access an intranet MySQL through a jump host

```
Local forwarding (-L)
Local listen: 127.0.0.1:3307
Remote host:  localhost
Remote port: 3306
```

After setup, `mysql -h 127.0.0.1 -P 3307` locally reaches the intranet database.

### Expose a local service to a remote end

```
Remote forwarding (-R)
Local service port: 8080
SSH host listen port: 9090
```

The SSH host listens on `0.0.0.0:9090` and forwards to local port `8080`.

### Use the SSH host as a temporary proxy

```
Dynamic forwarding (-D)
Proxy protocol: SOCKS5
Local proxy port: 1080
```

Point your system or browser proxy to `127.0.0.1:1080` to reach the target network through the SSH host.

## Notes

- Ports and addresses are validated (1–65535); invalid values cannot be saved.
- You must stop a rule before modifying or deleting it.
- Error status shows the specific reason, useful for troubleshooting port conflicts or unreachable remote ends.