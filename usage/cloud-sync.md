---
title: "Termark Cloud Sync"
description: "Learn how Termark cloud sync works, which storage channels are supported, and why self-hosted sync channels need to be reconfigured on a new device."
outline: deep
---

# Cloud Sync

Termark can synchronize hosts, credentials, groups, snippets, port forwards, and other data across devices. Sync uses your own storage channel, and data is encrypted with a sync passphrase you set before it leaves the device.

::: tip Core principle
The sync channel itself is stored **only on the current device** and is never uploaded. Termark does not store your channel address or access credentials.
:::

## Supported channels

Termark supports the following sync channels:

- **Official sync**: Termark's hosted sync service, signed in with your account.
- **GitHub**: Stores the sync data as a private repository, accessed with a Personal Access Token.
- **Git**: Points to any Git remote (for example your own Gitea, GitLab, or self-hosted Git).
- **WebDAV**: Points to any WebDAV service (for example Nutstore, Nextcloud, Synology).
- **S3**: S3-compatible object storage (for example AWS S3, MinIO, Cloudflare R2, Tencent COS, Aliyun OSS).
- **iCloud**: An iCloud Drive directory (macOS).
- **Local folder**: A local or LAN-shared directory.
- **FTP / SFTP**: Points to any FTP or SFTP server.

Except for **official sync**, which signs in with a Termark account, all other channels are provided by you — you supply the storage location and access credentials, and your data lives in your own service or space.

## How sync data is encrypted

With non-official channels, data is encrypted on your device before being uploaded to your storage:

- The sync passphrase is set by you. Termark uses PBKDF2-SHA256 to derive a 32-byte key from your sync passphrase and a random salt.
- The data to be uploaded is encrypted with AES-256-GCM. The content stored on the sync service or third-party storage is ciphertext.
- The sync passphrase is never uploaded to a server and never placed in your storage space.
- The server (third-party channel) only stores and transfers ciphertext and cannot decrypt your hosts, credentials, private keys, or other synced information.

If you choose to remember the sync passphrase, Termark stores it in the system keychain under the service name `termark.app`, entry name `sync-passphrase`. This is a separate entry from the local data key, `local-data-key`; the two do not replace each other.

## Why the channel configuration does not sync with the cloud

This is the most frequently asked question: **why do I have to reconfigure my own sync channel when I switch to a new device?**

The answer is that the sync channel does not travel through the cloud:

- The full channel configuration (type, server address, repository path, account, token/password, etc.) is stored **only in the local database on the current device**, and like other sensitive fields it is encrypted at rest.
- This channel configuration is **not** written into the synced data payload, so it never appears in any of your cloud storage.
- Termark **does not and cannot** store your channel address or access credentials.

In other words, the cloud holds only a snapshot of your business data (hosts, credentials, groups, etc.). The information about "where this data lives and how to connect to it" always stays on your device.

### Why it is designed this way

If Termark synced the channel along with the data, you would not need to reconfigure after switching devices — but that would mean your channel address and access credentials are obtained and stored by our server. Once channel information leaves your device and is centralized on our server, two problems appear:

1. **The data source is no longer "yours".** Your data lives in your own WebDAV / S3 / Git, yet the way to reach it would be routed and stored by us, turning your data source into storage managed under our service and defeating the point of owning the data source.
2. **One more place where channel credentials can leak.** Channel credentials are sensitive. Centralizing them on a server only increases the exposure surface. Keeping channel information on each device is the most minimal exposure.

So this is not a flaw, but a deliberate trade-off: **your data lives in your own storage, and the key to that storage stays on your device.** This is the core value of a self-hosted channel compared with official sync.

### What you need to do when switching devices

On a new device, simply re-select the sync channel in Settings, enter the channel address and credentials, and unlock with the **same sync passphrase**. Channel information is filled once per device; after that, reads and writes go to your own storage, and there is no need to sync the data itself again.

## Official sync vs. self-hosted channels

| Aspect | Official sync | Self-hosted channel (WebDAV/S3/Git/…) |
|--------|---------------|----------------------------------------|
| Sign in | Termark account | Your channel credentials |
| Data location | Termark service | Storage you specify |
| Reconfigure on new device | Just sign in again | Reconfigure the channel on each device |
| Data encryption | Sync passphrase | Sync passphrase |

Official sync trades the convenience of skipping channel setup (via account identity) for storing data in Termark's service. Self-hosted channels keep both the storage and the credentials entirely on your side. Both encrypt data with the sync passphrase you set.

## Related documentation

- [Local Encryption and Data Recovery](/usage/local-encryption): field-level encryption of local data, system keychain, and portable-build passphrase handling.
- [Data Storage Path](/usage/data-storage-path): where local data files and directories live.