---
title: "Independently Building a Desktop SSH Tool: The Hardest Part Is Not Writing Code"
description: Notes from building Termark, a cross-platform desktop SSH tool for real server workflows.
---

# Independently Building a Desktop SSH Tool: The Hardest Part Is Not Writing Code

When people look at desktop software, they usually look at the interface first.

Does it look good? Does it start quickly? Does it have enough features? Is the price reasonable?

Those things matter. But after actually building one, I increasingly feel that the most annoying part of desktop software is often not implementing a specific feature. It is all the work around the feature that still has to be done.

This is especially true for an SSH client.

On the surface, it is just a tool for "connecting to servers." In reality, you have to deal with cross-platform desktop behavior, terminal compatibility, credential security, installers, updates, licensing, downloads, documentation, user feedback, and all kinds of real server environments.

Many of these things are not exciting, but missing even one of them can decide whether users can keep using the product over time.

## SSH connection is only the smallest piece

A minimal prototype is not hard: save a host, enter an account, choose a password or private key, open a terminal, and run commands.

But once users actually start using it, the requirements expand quickly.

They do not only ask, "Can it connect?" They ask:

Can it group many machines? Can it import existing configurations? Can it work through jump hosts and proxies? What if an old server cannot connect? What about Chinese encoding issues? How does SFTP transfer files? How do I enable port forwarding? Can I save common commands? Can I execute commands on multiple machines in batch? Can I sync to another computer? Where are passwords and private keys stored? Is data still there after uninstalling and reinstalling? How do I migrate the Windows portable version? Why does security software block the download package?

None of these questions can be avoided.

So when a desktop SSH tool keeps growing, it becomes less like a simple connection tool and more like a workspace built around server assets. The SSH connection is only the entry point.

## Cross-platform: the same thing becomes two problems

macOS and Windows users have very different expectations for software.

macOS users care about whether Apple Silicon and Intel packages are separated, whether the app is signed, whether notarization passed, whether there is a security prompt on first launch, where the data directory is, whether keychain permissions work correctly, and whether dark mode feels natural.

Windows users care about installer versus portable package, where the install directory is, where the data directory is, whether antivirus software reports false positives, whether uninstalling deletes data, how to unlock the portable version after moving to another computer, and whether shortcuts and auto updates work correctly.

Linux also needs attention, but for me it is currently more of a supplementary platform. The priority is to support Ubuntu well first, so users who really need a Linux version know that they can use it.

The same idea, such as "saving data locally," may become a keychain issue on macOS and a portable-version migration issue on Windows. You cannot design only according to the habits of one platform.

Cross-platform is not just compiling the same interface twice.

## Installers, signing, and downloads

Many indie developers underestimate this at the beginning.

Getting the code to run is one thing. Letting ordinary users download, install, open, and upgrade it smoothly is another.

macOS signing, notarization, Windows installers, portable zip packages, Linux builds, auto updates, CDN, version numbers, changelogs, rollback packages, old-version compatibility, and security software false positives all have to be handled.

They rarely appear in product marketing.

But if users fail to download, install, or open the app the first time, they may never try a second time.

The first impression of desktop software is not the feature set. It is whether the app can run smoothly.

## Terminal: detail engineering inside a black box

A terminal looks like a black box. But once you build one, you find that every detail matters to someone.

Fonts, line height, themes, cursor style, copy and paste, right-click paste, copy-on-select, shortcut conflicts, search, split panes, multiple tabs, auto reconnect, Chinese character width, GBK encoding, terminal size changes, and full-screen output from remote programs are not big features by themselves. Together, they decide whether users are willing to open the tool every day.

Developer tools have a special characteristic: users may open them dozens of times a day. At that frequency, every small annoyance gets amplified.

"Minimal" does not mean having fewer features. It means not interrupting high-frequency operations.

## Real servers will keep teaching you

If you only test on a few of your own cloud servers, it is easy to misjudge the product.

Real users bring old Linux distributions, strange SSH algorithms, non-UTF-8 encodings, multi-level jump hosts, company proxies, keyboard-interactive authentication, intranet assets, Telnet devices, serial devices, SFTP with limited permissions, and bastion systems they already use.

It is hard to think of all these problems at the beginning. You can only keep filling the gaps through user feedback.

This is also why a tool cannot only chase new concepts. Many basic compatibility capabilities do not attract attention, but when users run into those issues, they affect real usage very directly.

A tool that only serves demo environments will have a hard time entering real workflows.

## Credential security: slogans are not boundaries

An SSH tool will inevitably touch credentials: passwords, private keys, proxy passwords, jump host credentials, and sync passwords. All of them are sensitive.

When users ask, "Will you steal my passwords?" it may sound sharp, but it is a normal question.

For this kind of question, saying "no" is not enough. You need to explain whether local data is stored in plaintext, how sensitive fields are encrypted, where the encryption key is stored, whether sync data is encrypted before upload, whether the server can see plaintext, and whether a lost password can be recovered.

Writing these explanations is less satisfying than building a new feature, but it has to be done.

This is especially important for closed-source commercial software. Users may not require you to reveal all the code, but you should at least tell them how their data is handled.

Security trust is not a slogan. It is a concrete explanation of boundaries.

## Sync: much more complicated than "uploading a file"

The need for multi-device sync is reasonable.

When switching between an office computer, a home computer, and a laptop, the experience becomes fragmented if SSH assets and command snippets cannot sync.

But once you build sync, many questions appear: which data should sync? Should credentials sync? Is data encrypted before sync? How is the sync password handled? Should it support an official service or third-party storage? How should WebDAV, S3, iCloud, and local directories be adapted? How do you resolve conflicts when multiple devices modify data at the same time? How should sync failures be shown? How does a user recover data after changing computers?

The key point is that sync data may contain server information and credentials. The server should not be able to see plaintext.

That makes the implementation much more complicated, but it is the complexity that should be paid.

## Pricing: do not turn basic features into fake free

For indie developers building tools, charging money is unavoidable.

Without charging, long-term maintenance is difficult. But a full subscription model is naturally disliked by many developer users. This is especially true for local tools. If users have to pay every month for basic features, it feels uncomfortable.

I prefer aligning paid features with ongoing costs.

Core local capabilities such as SSH, SFTP, port forwarding, and command snippets do not have obvious ongoing service costs, so I try to let users use them for free.

Advanced capabilities such as cloud sync, multi-device licensing, batch execution, and priority support are easier to explain as paid features.

For developer tools, users usually care about two things: do not lock them into a subscription immediately, and do not make basic features fake free.

If the free version can solve real problems, users are more likely to trust that you are not only trying to harvest trial traffic.

## Documentation is part of the product, not an accessory

If many features have no documentation, users effectively do not know how to use them.

Where is the data storage path? What happens if the local encryption passphrase is forgotten? How do you configure SFTP directory following? Why does an AI model need to turn off thinking mode? How are sync conflicts handled? How do you migrate the portable version? These all need to be written clearly.

Documentation also cannot be written only for the author.

The author knows how the system works, so it is easy to omit key steps. Users do not know. They only see a popup, an error message, or an unfamiliar setting.

Many "users do not know how to use it" problems are really cases where the documentation and interface did not explain the boundaries clearly enough.

## AI: an assistant, not automated operations

These days, not adding AI seems to make a product look behind the times.

But AI in an SSH tool should not exist only to chase a trend. Servers are different from code repositories. If AI directly executes commands, the risk lands on real machines.

Termark now separates terminal-scoped and Global AI and offers Auto, Balanced, and Strict approval. Balanced is the default: clearly read-only observation commands can run automatically, while writes, state changes, unknown commands, and hard-dangerous commands require approval.

I do not want to package it as a "fully automated ops agent."

The stronger the AI feature becomes, the more important command confirmation, risk judgment, and user visibility become. This kind of design is less easy to market, but it fits server scenarios better.

## User feedback keeps reordering your priorities

When building independently, it is easy to get trapped in your own imagination.

You may think the next version should add a cool new feature. Users may only want: a shortcut to be configurable, terminal fonts to be slightly thinner, SFTP folder upload to be more stable, an old server to connect successfully, Windows portable migration to be clearer, AI command confirmation to interrupt the flow less, or sync conflict prompts to be more explicit.

These requests are not grand, but they decide whether users stay.

Tool software does not end after one big feature is finished. It is a continuous process of removing friction from real usage. Often, fixing small problems is more valuable than adding a new concept.

## Finally

After building Termark, I increasingly feel that the most annoying part of desktop software is not writing code. It is filling in everything outside the code, one piece at a time.

Installation, updates, signing, security, sync, documentation, compatibility, licensing, and feedback rarely produce a beautiful marketing sentence. But they decide whether a tool can be maintained for the long term and whether it can truly enter a user's workflow.

The tradeoffs have also become clearer over time: keep local core features free as much as possible; charge for ongoing costs and advanced capabilities; keep the interface simple while making the lower layers handle real server environments; AI can improve efficiency, but control over servers should stay in the user's hands.

Termark currently supports macOS, Windows, and Linux. The Linux version mainly supports Ubuntu for now. Basic features are free to use, and the mobile version is also in development. If you need advanced capabilities such as batch execution and cloud sync, you can purchase a license.

Official website: [https://www.termark.app](https://www.termark.app)
