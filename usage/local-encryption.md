---
title: "Termark Local Encryption and Data Recovery"
description: "Learn how Termark encrypts credentials and settings locally, where encryption keys are stored, and how recovery works."
outline: deep
---

# Local Encryption and Data Recovery

Termark stores hosts, credentials, sync settings, and other data on your device. To avoid writing sensitive information to disk as plaintext, Termark encrypts sensitive fields locally.

Regular installed builds store the local data key required for decryption in the operating system's secure storage. The Windows portable build asks you to set a local encryption passphrase and derives the local data key directly from that passphrase.

This means your data can be used normally on your device, but we cannot obtain your local data key and cannot decrypt your data without the key or your sync passphrase.

## How local data is encrypted

Local sensitive fields are encrypted with a 32-byte local data key. This key is not written to Termark's regular database file as plaintext.

Regular installed builds save the local data key in the system keychain:

| Installed build platform | Secure storage |
|--------------------------|----------------|
| macOS | Keychain |
| Windows | Credential Manager |
| Linux | Secret Service |

On first launch of a regular installed build, Termark generates a random 32-byte key as the local data encryption key and saves it in the system keychain. Termark uses `termark.app` as the service name in the system keychain. The regular installed build's local data key entry is named `local-data-key`.

The Windows portable build uses a separate portable key mode. On first launch, Termark asks you to set a local encryption passphrase and uses Argon2id to derive a 32-byte local data key from that passphrase and a random salt. The database only stores non-secret KDF parameters, including the version, KDF name, salt, time, memory, and threads. It does not store your plaintext passphrase or plaintext local data key.

<div class="local-encryption-summary">
  <p><strong>In short:</strong> the portable build asks you to enter a local encryption key and uses it to encrypt the sensitive data stored on this device. After a successful unlock, Termark caches the derived encryption key in the current computer's system keychain. If you move the portable build to another computer, the new computer's keychain will not have that cache, so Termark will show a prompt asking you to enter the local encryption key again before it can decrypt the data.</p>
</div>

After the portable build is set up or unlocked successfully, Termark caches the derived local data key in the system keychain. It uses the same service name, `termark.app`, and the entry name `portable-local-data-key`. This entry is separate from the regular installed build's `local-data-key`, so the portable build does not overwrite the installed build's local data key.

When the portable build starts, it first tries to read the `portable-local-data-key` cache. If the cache is missing, inaccessible, or fails validation, Termark asks you to enter the local encryption passphrase again. With the correct passphrase, Termark derives the local data key again from the KDF parameters stored in the database and caches it in the system keychain. This means that when migrating to a new device, you do not need to carry over the old device's `portable-local-data-key` cache, but you must keep the full data directory, remember the local encryption passphrase, and ensure the current system keychain is accessible.

When writing to the database, Termark uses this local data key to encrypt sensitive fields with AES-256-GCM. A new random nonce is generated for each encryption operation, so saving the same value twice usually produces different ciphertext.

When reading from the database, Termark first loads or derives the local data key, then decrypts the sensitive fields before passing them to the app interface and connection logic. Regular installed builds load `local-data-key` from the system keychain. The Windows portable build reads `portable-local-data-key` from the system keychain, or derives it again from the local encryption passphrase you enter. If the corresponding key source is unavailable, the local encryption passphrase is incorrect, or the local data key fails validation, Termark refuses to continue writing new data in an unencrypted state.

## What is encrypted

Local field-level encryption currently covers sensitive connection and credential data, including:

- Host manual login passwords
- Host proxy passwords
- Credential passwords
- SSH private keys
- SSH private key passphrases

Regular configuration used for display and management, such as host names, addresses, ports, groups, remarks, and terminal preferences, remains stored in a readable configuration form. This keeps lists, search, sorting, and management features working while encrypting the actual passwords and key material at rest.

## How sync data is encrypted

If you enable data sync, synced data uses a separate encryption flow.

The sync passphrase is set by you. Termark uses PBKDF2-SHA256 to derive a 32-byte key from your sync passphrase and a random salt, then encrypts the data that will be uploaded with AES-256-GCM. The data stored on the sync server or third-party storage is ciphertext.

The sync passphrase is not uploaded to the server. The server only stores and transfers ciphertext, and cannot decrypt your hosts, credentials, private keys, or other synced information.

If you choose to remember the sync passphrase, Termark stores it in the system keychain. It uses the same service name, `termark.app`, but a different entry name: `sync-passphrase`. This is separate from the regular installed build's local data key entry, `local-data-key`; the two entries do not replace each other.

## Why we cannot decrypt your data

Termark's encryption design keeps decryption capability on your device and with you:

- Sensitive fields in the local database require the local data key to decrypt.
- In regular installed builds, `local-data-key` is stored in your device's system keychain and is not uploaded to Termark's server.
- In the Windows portable build, the local data key is derived from your local encryption passphrase and the KDF parameters in the database. The `portable-local-data-key` entry in the system keychain is only a local cache and is not uploaded to Termark's server.
- Synced data requires the sync passphrase you set.
- The sync passphrase is not uploaded to the server; if remembered, it is only stored in your device's system keychain.
- AES-GCM includes integrity checks. With the wrong key or wrong sync passphrase, decryption fails instead of producing readable data.

As a result, if you only provide the database file, sync ciphertext, or server-side data, we cannot restore your passwords, private keys, or other sensitive fields from it. If a regular installed build does not have the corresponding system keychain entry, the Windows portable build does not have the local encryption passphrase, or synced data does not have the sync passphrase, the ciphertext is unreadable to us as well.

## What happens if the key or passphrase is lost

The following situations can make existing sensitive data impossible to decrypt:

- The `termark.app / local-data-key` entry is deleted or reset in the system keychain.
- When using a regular installed build, the operating system is reinstalled or data is migrated without migrating the system keychain.
- When using a regular installed build, a local database file is copied directly to another device without the corresponding local data key.
- When using the Windows portable build, the local encryption passphrase set on first launch is forgotten.
- When using the Windows portable build, the portable KDF parameters or local data key check value in the database are deleted or damaged.
- The sync passphrase is forgotten and no accessible device still has it.
- The operating system keychain is damaged, removed by cleanup tools, or inaccessible to the current user.

If the local data key is lost, Termark cannot decrypt sensitive fields in the original database. You may still be able to see some non-sensitive configuration, but encrypted fields such as passwords, private keys, and proxy passwords cannot be recovered.

If the sync passphrase is lost, Termark cannot decrypt cloud sync data. We also cannot reset or recover the sync passphrase from server-side data.

## Backup recommendations

To avoid losing access during cleanup or migration:

- When migrating data from a regular installed build, do not copy only the Termark data directory. Use the operating system's migration tools to migrate the keychain as well.
- When migrating data from the Windows portable build, copy the full `data` directory under the program directory and keep the local encryption passphrase safe. If the new device does not have a `portable-local-data-key` cache, you can unlock the data again with this passphrase. Also make sure the current user on the new device can access the system keychain.
- If you enable sync, store the sync passphrase safely, such as in a password manager you trust.
- Keep the old device available until the new device has signed in and sync has been confirmed.
- For long-term archival, confirm that the local data, the corresponding key source, and the sync passphrase are all available. Regular installed builds require the system keychain; the Windows portable build requires the complete data directory and the local encryption passphrase.

Termark does not host your local data key or sync passphrase for you. This has an important consequence: we cannot recover lost sensitive data on your behalf, and the server or staff do not have the ability to decrypt user data.
