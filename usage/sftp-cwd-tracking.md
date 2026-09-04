---
title: "Make SFTP Follow the Terminal Working Directory"
description: "Configure Bash, Zsh, or Fish so the Termark SFTP panel automatically follows the SSH terminal working directory (SFTP CWD tracking)."
outline: deep
---

# SFTP CWD Tracking

Termark's SFTP panel can follow the terminal's current working directory automatically. Add the following snippet to the shell configuration file on the remote host.

How it works: whenever the shell changes directories, it sends an `OSC 1337` sequence with the current path. Termark detects that sequence and updates the SFTP panel to the same directory.

### Bash

Edit `~/.bashrc` or `~/.bash_profile`:

```bash
PROMPT_COMMAND='printf "\e]1337;CurrentDir=%s\a" "$PWD"'
```

### Zsh

Edit `~/.zshrc`:

```zsh
precmd() { printf "\e]1337;CurrentDir=%s\a" "$PWD" }
```

### Fish

Edit `~/.config/fish/config.fish`:

```fish
function __termark_cwd --on-event fish_prompt
    printf "\e]1337;CurrentDir=%s\a" $PWD
end
```

## Apply the change

After adding the configuration, sign in again or run `source` on the corresponding shell file.

## Notes

If you already use `PROMPT_COMMAND` in Bash or define `precmd()` in Zsh, merge the snippet into the existing logic instead of overwriting it.

## Related pages

- [SSH Port Forwarding](/usage/port-forwarding)
- [OpenWrt SFTP Not Working](/usage/openwrt-sftp)
