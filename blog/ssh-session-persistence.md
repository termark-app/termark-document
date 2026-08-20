---
title: After SSH Disconnects, Is Your Program Still Running? nohup vs tmux vs systemd
description: Whether a program survives an SSH disconnect depends on its terminal, shell session, and process manager. This guide explains the distinct roles of nohup, tmux, and systemd, and what to check after reconnecting.
date: 2026-08-20
updated: 2026-08-20
author: Termark Team
---

# After SSH Disconnects, Is Your Program Still Running?

Many people have been in this situation: you start a script on a server, close the SSH window, and immediately wonder whether the process has disappeared with it.

The answer is not as simple as “the server is still on, so everything is fine.” What matters is whether the program still depends on the terminal and shell session that just closed, and whether a more appropriate tool is managing it. Three common candidates are `nohup`, `tmux`, and `systemd`, but they solve fundamentally different problems. `nohup` deals with hangup signals and output destinations. `tmux` gives you a terminal session you can reconnect to. `systemd` manages the complete lifecycle of a service. Treating them as interchangeable “keep-alive spells” can produce an absurd result after SSH disconnects: the process is technically alive, but the task is out of control, its logs are missing, and nobody knows its exit status.

Here is a rough selection guide before we examine the details:

| Scenario | Better fit |
| --- | --- |
| Run a one-off command without reconnecting to its interactive interface | `nohup`, or a proper job queue |
| Disconnect and later return to the same terminal | `tmux` |
| Run a long-lived service with startup, restart, and logging requirements | `systemd` |
| Run a long build, migration, or batch operation | Usually `tmux`; use a job manager when it is fully unattended |

## One SSH login contains several separate layers

SSH connections, terminals, shells, and processes are often discussed as if they were the same thing, but they are separate layers:

```text
Local SSH client
        │
        │ encrypted connection
        ▼
sshd ── login shell ── terminal/PTY ── your program
```

The OpenSSH `ssh` command connects to the remote `sshd`. If it requests a pseudo-terminal, the server allocates a PTY and runs a shell or a specified command inside it, forwarding standard input and output over the encrypted channel.[1] Each command you enter is normally started by that login shell, which connects the child process to the terminal's standard streams.

That means several conditions must be considered separately: whether the SSH connection is open, whether the PTY is open, whether the login shell has exited, whether a particular process is still running, and—if a service manager owns it—what state that service is in. An SSH disconnect does not mean the kernel instantly kills every child process. It also does not guarantee that every program will continue normally. The result depends on signal handling, terminal dependencies, and how the parent process and login session are cleaned up.

## Why do some programs exit after a disconnect?

When an interactive shell exits, processes associated with it may receive `SIGHUP`, the hangup signal. A program may terminate under its default behavior, catch the signal and handle it, or ignore it because it does not depend on that terminal.[5]

Even if `SIGHUP` does not terminate the program immediately, closing the terminal can expose other problems: the program may keep writing to a terminal that no longer exists; it may block while waiting for standard input; shell job-control relationships may end; logs that existed only on the terminal may become inaccessible; or the task may finish without leaving a clear exit status.

So “Is the process still running after SSH disconnects?” is not the most useful question. A better one is: does this task have input, output, lifecycle management, and result recording that are independent of this SSH connection?

## `nohup`: make a command ignore hangup signals

The name `nohup` means “no hangup.” It makes a command ignore the hangup signal. If standard output still points to a terminal, GNU `nohup` appends it to `nohup.out` and handles standard error similarly.[2]

```bash
nohup ./backup.sh > backup.log 2>&1 &
pid=$!
printf 'pid=%s\n' "$pid"
```

This line combines three separate actions: `nohup` makes the script ignore the hangup signal, `> backup.log 2>&1` redirects standard output and error to a log file, and the final `&` lets the shell return without waiting for the script to finish. After reconnecting, you can inspect it with:

```bash
ps -p "$pid" -o pid=,stat=,etime=,cmd=
tail -n 50 backup.log
```

But `nohup` is not a complete service manager. It does not tell you whether the task succeeded, restart it after a crash, or preserve an interactive terminal you can rejoin. A surviving PID does not prove the task is healthy: it may be stuck, repeatedly logging errors, or may have already finished without recording its exit status. If the task needs interaction or live input, or if you want to return to the same terminal, `nohup` is usually not the best fit.

## `tmux`: separate the terminal session from the SSH connection

`tmux` is a terminal multiplexer. It creates an independent session on the server and runs a shell inside it. Your SSH client is merely one terminal attached to that session. If SSH disconnects, the tmux session remains on the server and can be attached again later.[3]

```bash
tmux new -s deploy
cd /srv/example
./deploy.sh
```

To leave without ending the session, press `Ctrl-b`, then `d`. After reconnecting through SSH:

```bash
tmux ls
tmux attach -t deploy
```

`tmux` is a good fit when you need to watch live build or deployment output, respond during a data migration, run a temporary development server, or keep working despite an unstable network. Its key advantage is that the shell state, working directory, and foreground process remain in place. But `tmux` solves session persistence, not program reliability. The program can still crash, exit because of application logic, or fail for another reason. After reconnecting, you still need to inspect its output and status:

```bash
tmux ls
ps -ef --forest
```

## `systemd`: manage the lifecycle of a long-running service

Web servers, background workers, message consumers, and other long-running programs are better managed by `systemd`. A service unit describes how a program starts and stops, whether it should restart after failure, and the conditions under which it should run.[4]

```ini
[Unit]
Description=Example worker
After=network-online.target

[Service]
Type=simple
WorkingDirectory=/srv/example
ExecStart=/srv/example/bin/worker
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Save it as `/etc/systemd/system/example-worker.service`, then run:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now example-worker.service
systemctl status example-worker.service
journalctl -u example-worker.service -f
```

`systemd` is appropriate for long-running services because it makes previously informal knowledge explicit: who starts the service, its working directory and command, whether it restarts after failure, where its logs live, whether it starts at boot, its current state, and why it failed last time. This is completely different from the problem `tmux` solves. A production web service normally should not live in one administrator's tmux window, and `nohup` should not be expected to replace restart policies, dependency management, or permission configuration.

## Comparing the three tools

| Capability | `nohup` | `tmux` | `systemd` |
| --- | --- | --- | --- |
| Continue after SSH disconnects | Usually | Yes | Yes |
| Reattach to the original interactive terminal | No | Yes | Not applicable |
| Output location | Redirected file | Preserved in the session | Journal |
| Automatic restart after failure | No | No | Configurable |
| Start at boot | No | No | Configurable |
| How to inspect status | Check PID and logs yourself | Inspect sessions and processes | `systemctl status` |
| Suitable by itself for long-running services | Not recommended | Not recommended | Yes |
| Suitable for temporary interactive tasks | Sometimes | Yes | Usually not |

Continuing after an SSH disconnect and being suitable for production are two different things. Detaching a command from one connection does not make its lifecycle observable, recoverable, or auditable.

## What should you inspect after reconnecting?

Do not stop after running `ps` and seeing that a process exists. Check according to the type of task:

```bash
# Temporary task
ps -ef | grep '[j]ob.sh'
tail -n 100 job.log

# tmux task
tmux ls
tmux attach -t maintenance

# systemd service
systemctl is-active example-worker.service
systemctl status example-worker.service
journalctl -u example-worker.service --since '30 minutes ago'
```

Also verify whether the process is still making progress, whether CPU, memory, or disk usage looks abnormal, whether logs continue to grow, whether the task has completed, whether it produced a verifiable result, and whether it restarted or ran more than once. “The process is alive” is one item on the checklist, not proof of success.

## Common misunderstandings

**Does adding `&` prevent a command from exiting when SSH disconnects?** Not necessarily. `&` only lets the shell continue without waiting for the foreground command. It does not handle hangup signals, standard streams, or service restarts.

**Can `nohup` restore the original session?** No. It addresses the command's dependency on the hangup signal and may redirect terminal output, but it does not preserve an interactive terminal that you can reattach to.

**Will programs inside `tmux` run forever?** Of course not. They can still crash, exit intentionally, or be killed by the OOM killer. `tmux` preserves a reconnectable session; it does not guarantee program correctness.

**Is `systemd` only for starting programs at boot?** No. It also manages service state, stopping behavior, restart policies, dependencies, and logging. Boot startup is only one option.

**Does an existing PID prove the task succeeded?** No. You must consider exit status, logs, output files, service state, and the actual business result.

## Final thoughts

An SSH connection is only a channel for accessing a server. It does not manage a task's lifecycle. If an unstable network is your main concern, ask: does this task need interaction? Do you need to reconnect to it? Should it restart automatically? Does it need to start at boot and use centralized logging? Answering those questions is more useful than searching for one universal “keep-alive command.”

As for an SSH/SFTP client such as [Termark](https://termark.app), it is not meant to replace `tmux`, `systemd`, or a job queue. It connects you to the server so you can use those server-side tools to manage the task: connect to the target host over SSH, create or reattach to a tmux session, inspect logs, processes, and systemd status, transfer scripts or retrieve logs over SFTP when needed, and reconnect later to continue checking the result. The client provides remote access; server-side tools own the task lifecycle. Keeping that boundary clear tells you whether to investigate the connection, the session, or the service configuration when something goes wrong.

## References

[1] [OpenSSH ssh manual](https://man7.org/linux/man-pages/man1/ssh.1.html)

[2] [GNU Coreutils nohup](https://www.gnu.org/software/coreutils/manual/html_node/nohup-invocation.html)

[3] [tmux manual](https://man7.org/linux/man-pages/man1/tmux.1.html)

[4] [systemd.service manual](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html)

[5] [GNU Bash Signals](https://www.gnu.org/software/bash/manual/html_node/Signals.html)
