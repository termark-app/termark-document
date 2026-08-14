---
title: "Termark Windows Antivirus False Positive Guide"
description: "Learn why Windows security software may flag Termark, how Go binary false positives happen, and how to verify downloads safely."
outline: deep
---

# Windows Antivirus False Positive Notice

When downloading or running Termark on Windows, some antivirus or security software may show a warning, block the installer, or mark the program as suspicious.

The Windows version of Termark is currently not code-signed with a paid certificate, so Windows and security software may not be able to verify the publisher identity through a certificate. Also, Termark's backend and some local features are written in Go, and Go-compiled binaries may occasionally be reported as suspicious on Windows.

The Go official FAQ describes a similar situation: [Why does my virus-scanning software think my Go distribution or compiled binary is infected?](https://go.dev/doc/faq#virus)

The key point from the official explanation is that this is common on Windows machines and is "almost always a false positive"; commercial antivirus tools can sometimes be confused by "the structure of Go binaries".

If you see this kind of warning, check the following first:

- Download Termark only from official Termark channels, not from third-party repackaged files.
- Make sure the downloaded file has not been modified by the browser, proxy software, or another download tool.
- If your security software supports false-positive reports, send the detection result to the security software vendor.
- If you are still unsure about the file source or safety, do not continue running it.

Lack of a paid code-signing certificate and possible Go binary false positives do not mean the program is necessarily unsafe. At the same time, security warnings should not be ignored blindly. Confirm the download source first, then decide based on the specific result reported by your security software.
