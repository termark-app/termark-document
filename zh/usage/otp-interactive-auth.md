---
title: "自动 OTP 交互认证与识别文本"
description: "配置主机 OTP 密钥与交互认证识别文本，让 Termark 自动匹配 SSH 交互认证提示并提交动态验证码。"
outline: deep
---

# 自动 OTP 交互认证

部分 SSH 服务（如配置了 PAM / google-authenticator 两步验证的 OpenSSH）在密码验证通过后，还会通过键盘交互认证（keyboard-interactive）要求输入一个动态验证码。Termark 支持为这类主机配置 **OTP 密钥** + **交互认证识别文本**，自动识别并提交当前的 6 位验证码，免去手动输入。

## 两项必填配置

在主机的高级设置中，开启「启用动态验证码」后需要同时填写两项，缺一不可：

- **OTP 密钥**：该账号绑定动态验证码时生成的 Base32 密钥（例如 Google Authenticator / Authenticator 应用中导出或扫码时的 `JBSWY3DPEHPK3PXP`）。
- **交互认证识别文本**：用于识别服务端认证提示的文本，Termark 用它判断当前这一步是否需要提交验证码。

## 交互认证识别文本怎么填

这一个字段只需要能唯一标记服务端的那条动态验证码提示，不需要与提示完全一致。Termark 会做**不区分大小写的子串匹配**：只要服务端提示文本（`challenge.Name`、`challenge.Instruction` 或问题文本 `challenge.Questions`）中任意一处包含你填的内容，就会命中。

因此：

- 填服务端提示里的**关键片段**即可，例如 `Verification code`、`OTP`、`code`。
- 大小写不必严格一致（`verification code` 与 `Verification code` 都能命中）。
- 前后多余空格会被忽略，无需逐字完整复刻整句提示。
- 建议选一个**足够独特**的词，避免太泛（如单独的 `code`）误命中其他提问；但太精确的整句提示在服务端措辞变化时会失效。

### 填写建议

| 服务端提示示例 | 建议填写的识别文本 |
| --- | --- |
| `Verification code:` | `Verification code` |
| `OTP:` / `One-time password:` | `OTP` |
| `6-digit code:` | `code` |

## 自动提交的前置条件

除了识别文本命中，Termark 还会要求：

1. 服务端该次认证请求**只有一个问题**（`Questions` 数量为 1）。
2. 命中后自动用 OTP 密钥生成当前动态码并提交，无需手动介入。

不满足上述条件时不会自动提交，连接会像往常一样提示你手动输入。

## 常见问题

- **配置无效**：OTP 密钥或识别文本缺少任一，自动提交都不会启用。
- **没自动提交**：检查识别文本是否命中了认证提示的实际措辞，并确认服务端该步确属动态验证码（单个问题）。
- 如果主机还涉及多跳（Jump Host），每台需要 OTP 的主机都要单独配置。