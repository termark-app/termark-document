---
title: "Highlight Keywords in SSH Terminal Output"
description: "Configure Termark keyword highlighting to spot errors, warnings, IDs, paths, and other important terminal output."
outline: deep
---

# Keyword Highlight

Termark keyword highlight is used to mark text you care about in regular terminal output, such as errors, warnings, failure states, IP addresses, ports, order IDs, task IDs, or custom business keywords.

Its role is output observation assistance: it does not change the original terminal text, command results, or remote shell behavior. You can think of it as an extra text-color overlay added by Termark at the terminal display layer.

## What It Is For

Keyword highlight is useful when you need important information to stand out in long output.

Common scenarios include:

- Highlighting `ERROR`, `WARN`, `failed`, `timeout`, `denied`, and similar keywords in deployment, build, or test output.
- Marking HTTP status codes, exception types, request IDs, task IDs, container names, or service names in logs.
- Making failed hosts, failed steps, or risky operations easier to spot during batch command execution.
- Adding visual reminders for high-risk commands or output in production sessions, such as `rm -rf`, `DROP DATABASE`, `iptables`, or `systemctl stop`.
- Using different colors to distinguish IP addresses, ports, paths, and other repeated output patterns.

Keyword highlight is not an alerting system and does not prevent command execution. It only makes matched text more visible.

## Difference From Bash/Zsh/Fish Highlighting

Highlighting in Bash, Zsh, or Fish usually means shell input highlighting or command-line syntax highlighting. Fish includes command-line highlighting by default, and Zsh can highlight the command you are currently typing through plugins.

Termark keyword highlight is a different kind of feature.

| Item | Termark Keyword Highlight | Bash/Zsh/Fish Highlighting |
|------|---------------------------|----------------------------|
| Where it works | Termark terminal display layer | Local or remote shell |
| Main target | Plain text already written to the terminal | The command line currently being typed |
| How it decides | Matches text with user-defined regular expressions | Usually understands shell syntax, commands, paths, quotes, and related structures |
| Scope | Terminal sessions inside Termark | Environments where the shell feature or plugin is installed and configured |
| Shell impact | Does not affect the shell, commands, prompt, or remote environment | Requires shell configuration changes or plugins |
| Typical use | Highlight logs, errors, status codes, risky words, and business keywords | Indicate whether commands exist, paths are valid, or syntax is complete |

In short:

- If you want the command you are typing to be colored by syntax, use Bash/Zsh/Fish configuration or plugins.
- If you want certain text in command output, logs, or batch execution results to stand out, use Termark keyword highlight.

Both can be used together. Shell highlighting covers the input stage, while Termark keyword highlight helps with output observation.

## Limitations

Keyword highlight has clear boundaries:

- It only overlays decorations on regular terminal output. Full-screen TUI applications do not receive these decorations for now, such as `vim`, `top`, `htop`, and full-screen `less`.
- It does not understand shell syntax. It does not determine whether a command exists, whether quotes are closed, whether a path is valid, or whether text is command input or program output.
- It does not change the terminal buffer content. Copied text, command execution, and logs remain the original text.
- It does not prevent dangerous commands from running. Even if `rm -rf` or `DROP DATABASE` is highlighted, it is only a visual reminder.
- Highlighting is based on regular expression matches, so overly broad rules can produce false positives. For example, `err` may match fragments inside ordinary words.
- When multiple rules overlap, earlier rules take priority. Put more important matches higher in the rule list.
- It currently only sets the text color of matched content. Background color, bold, underline, and similar styles are not provided.

If you need reliable recognition of structured logs, prefer JSON output, fixed fields, or explicit prefixes, then match those stable fields with keyword highlight. Avoid relying on overly vague natural-language fragments.

## Example Rules

You can refer to the example rules in the Termark repository:

[https://github.com/termark-app/termark/tree/main/highlights](https://github.com/termark-app/termark/tree/main/highlights)

Start with a small number of rules and highlight only what truly needs attention. Too many rules and colors can make output harder to read.
