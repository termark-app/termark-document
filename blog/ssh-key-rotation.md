---
title: Lost or Leaked SSH Keys? Generate, Manage, and Rotate Them
description: Complete guide to SSH key management for key leaks and rotation — covering ed25519 generation, authorized_keys control, ssh-agent, Ansible batch rotation, and audit monitoring for production Ubuntu/Debian systems.
date: 2026-08-31
updated: 2026-08-31
author: Termark Team
---

# Lost or Leaked SSH Keys? Generate, Manage, and Rotate Them

SSH key compromise is one of the most common security incidents in operations. An employee leaves with their private key, a laptop gets stolen, or a CI/CD pipeline accidentally commits credentials to a repository — any of these means an attacker may already hold valid login credentials. Passwords can be changed immediately, but once SSH keys spread beyond your control, the blast radius is often larger than expected: you can't determine which servers the compromised key has accessed or what commands have been run.

Rather than scrambling to investigate server-by-server after an incident, establish a complete SSH key lifecycle management approach now. This article covers key generation, distribution and storage, rotation procedures, automation scripts, and audit monitoring — each step with copy-ready commands.

## Generating Secure Keys: ed25519 First

Algorithm choice is the first decision in key management. RSA 2048-bit is still considered secure at current compute levels, but produces larger keys and slower generation. Ed25519 achieves equivalent or stronger security with just 256 bits and better performance. OpenSSH 6.5+ supports ed25519, and most modern distributions ship 7.x or later, so compatibility is rarely a concern.

```bash
# Generate an ed25519 key pair (recommended), with comment for identification
ssh-keygen -t ed25519 -C "admin@production-2026" -f ~/.ssh/id_ed25519

# For legacy system compatibility, generate RSA 4096-bit
ssh-keygen -t rsa -b 4096 -C "admin@legacy-2026" -f ~/.ssh/id_rsa_4096

# View the public key fingerprint for server-side cross-verification
ssh-keygen -lf ~/.ssh/id_ed25519.pub
# Example output: 256 SHA256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx admin@production-2026 (ED25519)
```

Private key file permissions must be set to 600, otherwise the SSH client will refuse to use them. Public keys can be freely distributed — they contain no information that could be used to derive the private key.

## Key Management: authorized_keys, ssh-agent, and config

Having a key pair is just the starting point. Managing public key distribution and private key loading is the daily operations focus.

**authorized_keys permissions and configuration:** The server-side `~/.ssh/authorized_keys` must have 600 permissions, and `~/.ssh` must be 700. If permissions are wrong, `sshd` silently ignores public key authentication. Each line holds one public key, with optional restriction fields like `from="IP"`, `command="..."`, and `expiry-time="..."` to narrow authorization scope.

```bash
# Check and fix permissions
chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys

# Restrict a key to a specific IP range and a single command
from="10.0.0.0/8",command="/usr/local/bin/backup.sh" ssh-ed25519 AAAAC3... backup@ci
```

**ssh-agent key loading:** Private keys shouldn't require password entry on every connection. Use ssh-agent to manage them centrally — load once, use everywhere.

```bash
# Start ssh-agent and load a private key (prompts for key passphrase once)
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# List loaded keys
ssh-add -l

# Ensure ssh-agent starts automatically in new terminals (add to .bashrc or .zshrc)
echo 'eval "$(ssh-agent -s)" > /dev/null && ssh-add ~/.ssh/id_ed25519 2>/dev/null' >> ~/.bashrc
```

**SSH config simplifies connections:** Configure `~/.ssh/config` for each server to avoid manually entering port, username, and key path every time. After configuration, connect with `ssh myserver` directly — CI/CD scripts no longer need hardcoded connection parameters.

```ssh-config
Host myserver
    HostName 192.168.1.100
    Port 22
    User deploy
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

## Rotation Procedure: Step by Step

After discovering a key compromise, rotation must follow a strict sequence — deploy the new key first, then revoke the old one. Any reversal risks service interruption. Here is the complete single-server rotation procedure:

```bash
# 1. Generate a new key pair locally
ssh-keygen -t ed25519 -C "admin@rotation-$(date +%Y%m%d)" -f ~/.ssh/id_ed25519_new

# 2. Deploy the new public key to the target server (append to authorized_keys)
ssh-copy-id -i ~/.ssh/id_ed25519_new.pub deploy@target-server

# 3. Verify the new key works (do not close the current session)
ssh -i ~/.ssh/id_ed25519_new deploy@target-server 'echo "new key works"'

# 4. Once confirmed, remove the old public key from the server
# Find the line number of the old key
ssh deploy@target-server 'grep -n "old key comment or fingerprint" ~/.ssh/authorized_keys'
# Delete the specified line (replace line number)
ssh deploy@target-server 'sed -i "LINE_NUMBERd" ~/.ssh/authorized_keys'

# 5. Clean up the old local key
mv ~/.ssh/id_ed25519 ~/.ssh/id_ed25519.bak.$(date +%Y%m%d)
mv ~/.ssh/id_ed25519.pub ~/.ssh/id_ed25519.pub.bak.$(date +%Y%m%d)
mv ~/.ssh/id_ed25519_new ~/.ssh/id_ed25519
mv ~/.ssh/id_ed25519_new.pub ~/.ssh/id_ed25519.pub

# 6. Update IdentityFile path in SSH config if the filename changed
# Edit manually or use sed to replace
```

For rotating keys across multiple servers, scripts beat manual repetition. The critical rule: steps 3 and 4 must happen while the old session stays open. Revoking the old key before verifying the new one locks you out.

## Automated Rotation: Ansible Batch Operations

Managing 10+ servers manually is slow and error-prone. Ansible can batch-deploy new keys, revoke old ones, and verify in one playbook.

```yaml
# rotate-keys.yml — Ansible batch rotation playbook
---
- hosts: all
  become: yes
  vars:
    new_pubkey: "{{ lookup('file', '~/.ssh/id_ed25519_new.pub') }}"
    old_key_comment: "admin@compromised"

  tasks:
    - name: Deploy new public key
      authorized_key:
        user: deploy
        key: "{{ new_pubkey }}"
        state: present

    - name: Revoke old public key
      lineinfile:
        path: /home/deploy/.ssh/authorized_keys
        regexp: "{{ old_key_comment }}"
        state: absent

    - name: Verify new key works
      command: ssh -o BatchMode=yes -o ConnectTimeout=5 deploy@{{ inventory_hostname }} echo ok
      delegate_to: localhost
      become: no
```

Validate against a test environment before running against production. Backing up `authorized_keys` before any batch operation is non-negotiable: `cp ~/.ssh/authorized_keys ~/.ssh/authorized_keys.bak.$(date +%Y%m%d)`.

## Monitoring and Audit: Who's Using What Keys

Key rotation is reactive; monitoring is continuous protection. You need to answer two questions: which keys have logged into which servers, and are there anomalous login patterns?

```bash
# View all SSH login records (including key fingerprints)
sudo grep "Accepted publickey" /var/log/auth.log | tail -20

# Count login frequency by key fingerprint
sudo grep "Accepted publickey" /var/log/auth.log | grep -oP 'SHA256:\S+' | sort | uniq -c | sort -rn

# Audit server SSH configuration with ssh-audit
sudo apt install ssh-audit && ssh-audit localhost

# Check fingerprints of all authorized_keys on the server
for user_dir in /home/*/.ssh /root/.ssh; do
  echo "=== $user_dir/authorized_keys ==="
  while IFS= read -r line; do
    echo "$line" | ssh-keygen -l -f - 2>/dev/null
  done < "$user_dir/authorized_keys" 2>/dev/null
done
```

ssh-audit checks supported key algorithms, MAC algorithms, and KEX algorithms, flagging configurations with known vulnerabilities. Run it quarterly or immediately after an OpenSSH upgrade. Combined with log analysis, you can visualize key usage in Grafana or ELK, catching unfamiliar fingerprints or unusual login times early.

## Conclusion

SSH key management is not a one-time task. Use ed25519 for generation, manage with permission controls and ssh-agent, rotate in strict deploy-then-revoke order, automate batch operations with Ansible, and audit with ssh-audit and log analysis. Turn these five steps into an SOP so the next incident doesn't catch you off guard. Termark, as an SSH connection and key management tool, can simplify multi-server key distribution and connection testing — but tools are only helpers; the core is the management process you establish.

## References

- [OpenSSH Official Documentation - ssh-keygen](https://man.openbsd.org/ssh-keygen)
- [ssh-audit Tool](https://github.com/jtesta/ssh-audit)
- [Ansible authorized_key Module](https://docs.ansible.com/ansible/latest/collections/ansible/posix/authorized_key_module.html)
- [NIST SP 800-57 Key Management Recommendations](https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final)
