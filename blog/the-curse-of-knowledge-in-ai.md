---
title: The Curse of Knowledge in Large Models
description: Why Termark separates command explanations from executable tool input.
date: 2026-05-26
updated: 2026-08-14
author: Termark Team
---

# The Curse of Knowledge in Large Models

The "curse of knowledge" means that once you know something, it becomes hard to explain it from the perspective of someone who does not.

Termark defines separate tool fields for executable input and its human-readable explanation.

---

Termark is an SSH client available at [https://www.termark.app](https://www.termark.app). It includes terminal-scoped and Global AI. Under the default Balanced policy, clearly read-only observation commands can run automatically, while writes, state changes, unknown commands, and hard-dangerous commands require approval; Auto, Balanced, and Strict are available.

![ai.png](images4/ai.png)

The current Termark prompt separates explanation from execution. The `terminal_execute.command` field must contain only the executable shell command: no explanatory comments, and no leading `#`.

For example, the model should not put this in the command field:

```bash
# View the latest 100 lines of logs
tail -n 100 /var/log/nginx/error.log
```

It should send only:

```bash
tail -n 100 /var/log/nginx/error.log
```

The explanation belongs in the tool's separate `explanation` field. Under Balanced mode, the model marks clearly read-only inspection commands with `confirmation: "none"`; writes, state changes, uncertain commands, and hard-dangerous commands require approval. The runtime also keeps a hard-dangerous command check as a final safeguard.
---

The current system prompt states the boundary directly:

**Only put executable shell commands in the command field. Put the reason in the explanation field.**

![prompt.png](images4/prompt.png)

This rule expresses the intended schema boundary between human-readable context and the command value.
