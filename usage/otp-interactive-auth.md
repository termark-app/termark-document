---
title: "Automatic OTP Interactive Authentication"
description: "Configure the host OTP secret and interactive prompt match so Termark automatically matches the SSH interactive auth prompt and submits the verification code."
outline: deep
---

# Automatic OTP Interactive Authentication

Some SSH servers (for example, OpenSSH with PAM / google-authenticator two-factor setup) ask for a one-time verification code via keyboard-interactive authentication after the password succeeds. Termark lets you configure an **OTP secret** plus an **interactive prompt match** for such hosts, so it can detect and submit the current 6-digit code automatically, without typing it by hand.

## Two Required Fields

In the host's advanced settings, after enabling "Enable one-time password" you must fill in both fields:

- **OTP secret**: the Base32 secret generated when the account was enrolled for two-factor codes (for example `JBSWY3DPEHPK3PXP` from Google Authenticator / Authenticator).
- **Interactive prompt match**: text used to recognize the server's challenge prompt, so Termark can tell this step is the one asking for a verification code.

## How to Fill the Interactive Prompt Match

This field only needs to uniquely identify the server's verification-code prompt — it does not need to match verbatim. Termark performs a **case-insensitive substring match**: it hits as long as any part of the server's prompt text (`challenge.Name`, `challenge.Instruction`, or a question in `challenge.Questions`) contains what you entered.

So:

- Enter a **key snippet** of the prompt, e.g. `Verification code`, `OTP`, or `code`.
- Case does not need to match exactly (`verification code` and `Verification code` both hit).
- Leading/trailing whitespace is ignored; you don't need to reproduce the full sentence.
- Prefer a **reasonably unique** term — something as generic as a lone `code` may match other questions — but a prompt that is too exact will break if the server wording changes.

### Suggested Values

| Example server prompt | Suggested match text |
| --- | --- |
| `Verification code:` | `Verification code` |
| `OTP:` / `One-time password:` | `OTP` |
| `6-digit code:` | `code` |

## Prerequisites for Auto-Submission

Beyond the prompt match, Termark also requires:

1. The authentication challenge from the server has **exactly one question** (`Questions` count is 1).
2. On a match, Termark generates the current code from the OTP secret and submits it automatically.

If these conditions are not met, no code is submitted and the connection will prompt you to type it manually as usual.

## FAQ

- **Configuration not working**: auto-submission stays disabled if either the OTP secret or the prompt match is empty.
- **No auto-submit**: check whether the match text actually hits the server prompt wording, and confirm this challenge is the one-time code step (a single question).
- For multi-hop (Jump Host) setups, each host that needs OTP must be configured separately.