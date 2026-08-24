---
title: "Configure Reasoning Effort for GPT, DeepSeek, Qwen, Kimi, GLM, and More"
description: "Configure thinking mode, reasoning effort, and reasoning token budgets for GPT, DeepSeek, Qwen, Kimi, GLM, Gemini, Grok, Ollama, and other models through CustomRequestBody."
outline: deep
---

# Configure AI Model Reasoning Effort

Termark lets you configure a model's thinking mode and reasoning effort through **Additional Request Parameters (JSON)** in an API environment. This setting corresponds to `CustomRequestBody` internally.

Different providers and APIs do not use the same fields. For example, OpenAI Chat Completions uses `reasoning_effort`, the OpenAI Responses API uses `reasoning.effort`, while Qwen's Chat Completions API uses `enable_thinking` and `thinking_budget`. Before configuring these parameters, you must first confirm the **Provider Type** of the current API environment.

## Where to Configure It

1. Open Termark Settings and go to **AI Assistant**.
2. Add or edit an API environment.
3. Expand **Advanced Settings**.
4. Enter the JSON provided in this guide under **Additional Request Parameters (JSON)**.
5. Save the API environment, then run a connection test or start a new conversation.

Entering `{}` means that no additional parameters will be sent and the model will use the server-side defaults.

## Confirm the Provider Type First

Termark currently provides the following three provider types:

| Termark provider type | Actual request path | Common reasoning parameter structure |
|-----------------------|---------------------|--------------------------------------|
| `OpenAI` | `/v1/chat/completions` | Top-level fields such as `reasoning_effort` |
| `OpenAI-Response` | `/v1/responses` | Nested fields such as `reasoning.effort` |
| `Anthropic` | `/v1/messages` | Does not use **Additional Request Parameters (JSON)** |

**Additional Request Parameters (JSON)** is available only for the `OpenAI` and `OpenAI-Response` provider types. Termark merges the top-level fields in this JSON object into every request, but it does not verify whether the provider supports those fields and does not automatically convert parameters between the Chat Completions and Responses formats.

::: warning
Do not set `model`, `messages`, `input`, `instructions`, `tools`, `tool_choice`, `parallel_tool_calls`, `stream`, or `store` in Additional Request Parameters. Termark manages these fields. Overriding them may break conversations, tool calls, streaming output, or context handling.
:::

## Quick Reference

| Model service | Termark provider type | Enable or configure thinking | Disable thinking |
|---------------|-----------------------|------------------------------|------------------|
| OpenAI GPT | `OpenAI` | `{"reasoning_effort":"high"}` | Use `none` if the model supports it, or remove the field to restore the model default |
| OpenAI GPT | `OpenAI-Response` | `{"reasoning":{"effort":"high"}}` | Use `none` if the model supports it, or remove the field to restore the model default |
| DeepSeek | `OpenAI` | `{"thinking":{"type":"enabled"},"reasoning_effort":"high"}` | `{"thinking":{"type":"disabled"}}` |
| DeepSeek | `OpenAI-Response` | `{"reasoning":{"effort":"high"}}` | `{"reasoning":{"effort":"none"}}` |
| Qwen | `OpenAI` | `{"enable_thinking":true,"thinking_budget":8192}` | `{"enable_thinking":false}` |
| Qwen | `OpenAI-Response` | `{"reasoning":{"effort":"high"}}` | `{"reasoning":{"effort":"none"}}` |
| Kimi K3 | `OpenAI` | `{"reasoning_effort":"high"}` | Thinking cannot be disabled |
| Kimi K2.6/K2.5 | `OpenAI` | `{"thinking":{"type":"enabled"}}` | `{"thinking":{"type":"disabled"}}` |
| GLM-5.2 and later | `OpenAI` | `{"thinking":{"type":"enabled"},"reasoning_effort":"high"}` | Depends on the model; GLM-5.3 does not support disabling thinking |
| Gemini | `OpenAI` | `{"reasoning_effort":"high"}` | Only some Gemini 2.5 models support `none` |
| Grok 4.5/4.6 | `OpenAI-Response` | `{"reasoning":{"effort":"high"}}` | Thinking cannot be disabled |
| Ollama | `OpenAI` | `{"reasoning_effort":"high"}` | Depends on the local model |
| OpenRouter | `OpenAI` | `{"reasoning":{"effort":"high"}}` | Depends on the routed model |
| Direct Claude connection | `Anthropic` | Cannot currently be configured through this field | Cannot currently be configured through this field |

The JSON in this table is shown on one line for quick reference. You can use the more readable multiline examples below when entering the configuration.

## OpenAI GPT

### Using the OpenAI Provider Type

When the provider type is set to `OpenAI`, Termark calls the Chat Completions API. Use the top-level `reasoning_effort` field to configure reasoning effort:

```json
{
  "reasoning_effort": "high"
}
```

OpenAI currently defines the following possible values:

| Value | General meaning |
|-------|-----------------|
| `none` | No additional reasoning, provided that the selected model supports it |
| `minimal` | Minimal reasoning, prioritizing lower latency and token usage |
| `low` | Lower reasoning effort |
| `medium` | A balance between speed, token usage, and response quality |
| `high` | Higher reasoning effort for complex analysis and coding tasks |
| `xhigh` | Extra-high reasoning effort, supported only by some models |
| `max` | Maximum reasoning effort, supported only by some models |

A particular model may not support every value in the table, and the model determines its own default. If the API reports that a value is unsupported, lower the effort according to that model's official documentation or remove `reasoning_effort` to use the model default.

### Using the OpenAI-Response Provider Type

When the provider type is set to `OpenAI-Response`, Termark calls the Responses API. This API uses the nested `reasoning.effort` field:

```json
{
  "reasoning": {
    "effort": "high"
  }
}
```

The available values likewise depend on the specific model. Do not use the top-level `reasoning_effort` field with the `OpenAI-Response` provider type, or the server may ignore the parameter or return a parameter error.

## DeepSeek

DeepSeek's reasoning parameters also depend on the API type.

### Using the OpenAI Provider Type

To enable thinking with high reasoning effort:

```json
{
  "thinking": {
    "type": "enabled"
  },
  "reasoning_effort": "high"
}
```

DeepSeek Chat Completions currently supports `low`, `high`, and `max` reasoning effort.

If you only want to enable thinking and use the model's default effort, omit `reasoning_effort`:

```json
{
  "thinking": {
    "type": "enabled"
  }
}
```

To disable thinking:

```json
{
  "thinking": {
    "type": "disabled"
  }
}
```

When disabling thinking, you should also remove `reasoning_effort` so that an effort parameter is not sent with a request that does not require reasoning.

### Using the OpenAI-Response Provider Type

The DeepSeek Responses API uses `reasoning.effort`, with `none`, `low`, `high`, and `max` currently available:

```json
{
  "reasoning": {
    "effort": "high"
  }
}
```

Set `effort` to `none` to disable thinking:

```json
{
  "reasoning": {
    "effort": "none"
  }
}
```

## Qwen

Qwen's Chat Completions API and Responses API use two different methods for controlling thinking.

### Using the OpenAI Provider Type

For Qwen models that support hybrid thinking mode, use `enable_thinking` to enable thinking and `thinking_budget` to limit the maximum number of tokens used for reasoning:

```json
{
  "enable_thinking": true,
  "thinking_budget": 8192
}
```

`thinking_budget` is a maximum reasoning token budget, not a fixed amount of token usage. A larger value gives the model more room to handle complex problems, but generally also increases latency and token consumption. The valid range and default limit differ by model; refer to the official documentation for the selected model.

To enable thinking while using the model's default budget:

```json
{
  "enable_thinking": true
}
```

To disable thinking:

```json
{
  "enable_thinking": false
}
```

Some reasoning-only models always reason and do not support disabling thinking through `enable_thinking`. Some open-source Qwen models support thinking only with streaming requests. Termark's AI conversations already use streaming requests, so you do not need to set `stream` separately.

Some Qwen models on Alibaba Cloud Model Studio, as well as certain Kimi models deployed on Model Studio or Moonshot AI, may also support the following extension:

```json
{
  "enable_thinking": true,
  "preserve_thinking": true
}
```

`preserve_thinking` passes reasoning content from previous turns back to the model. It does not control reasoning effort and is supported only by certain models and deployment channels. Kimi's official API uses `thinking.keep`, described below; do not mix these two fields. Do not add `preserve_thinking` unless the official documentation for the current API endpoint explicitly lists it as supported.

### Using the OpenAI-Response Provider Type

Qwen's Responses API uses `reasoning.effort`:

```json
{
  "reasoning": {
    "effort": "high"
  }
}
```

It currently supports `none`, `minimal`, `low`, `medium`, and `high`, where `none` disables thinking. With the Responses API, use `reasoning.effort`; do not also set `enable_thinking` or `thinking_budget`.

## Kimi

Reasoning parameters differ significantly between Kimi models, so the same JSON cannot be used across the entire Kimi family. The following configurations apply to Kimi's official OpenAI-compatible Chat Completions API; select the `OpenAI` provider type in Termark.

### Kimi K3

`kimi-k3` always reasons. Use the top-level `reasoning_effort` field to adjust its effort:

```json
{
  "reasoning_effort": "high"
}
```

It currently supports `low`, `high`, and `max`, with `max` as the default. K3 does not support disabling thinking, and you should not send it a `thinking` object.

### Kimi K2.6 and K2.5

`kimi-k2.6` and `kimi-k2.5` use `thinking.type`, which defaults to `enabled`. To enable thinking explicitly:

```json
{
  "thinking": {
    "type": "enabled"
  }
}
```

To disable thinking:

```json
{
  "thinking": {
    "type": "disabled"
  }
}
```

`kimi-k2.6` also supports `thinking.keep` to control whether previous reasoning is preserved across multiple turns:

```json
{
  "thinking": {
    "type": "enabled",
    "keep": "all"
  }
}
```

`keep: "all"` does not increase the current turn's reasoning effort; it only preserves previous `reasoning_content`. If `keep` is omitted, K2.6 does not preserve reasoning from previous turns by default.

### Kimi K2.7 Code

`kimi-k2.7-code` always thinks and always preserves its reasoning, so you neither need nor should send a `thinking` parameter. This model currently has no configurable reasoning-effort field. Use `{}` to keep the model's default behavior.

## GLM

Zhipu GLM's OpenAI-compatible Chat Completions API uses `thinking.type` to enable or disable thinking. GLM-5.2 and later can also use `reasoning_effort` to control the degree of reasoning.

To enable thinking with high reasoning effort:

```json
{
  "thinking": {
    "type": "enabled"
  },
  "reasoning_effort": "high"
}
```

Supported effort values differ by model:

| Model | Available `reasoning_effort` values | Notes |
|-------|-------------------------------------|-------|
| GLM-5.3 | `low`, `high`, `max` | Thinking cannot be disabled; passing `thinking.type: "disabled"` returns an error |
| GLM-5.2 | `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max` | `none/minimal` skip thinking; `low/medium` map to `high`; `xhigh` maps to `max` |
| GLM-5.1, GLM-5, GLM-4.7, GLM-4.6, GLM-4.5, and others | Does not support `reasoning_effort` | Use only the `thinking.type` value supported by the model |

For models that explicitly support disabling thinking, use:

```json
{
  "thinking": {
    "type": "disabled"
  }
}
```

Do not use this configuration with GLM-5.3.

Some GLM models also support `clear_thinking: false` inside the `thinking` object to preserve reasoning content during tool calls. It is not an effort parameter and should be used only when the documentation for the selected model and API explicitly supports it:

```json
{
  "thinking": {
    "type": "enabled",
    "clear_thinking": false
  }
}
```

## Gemini

Google Gemini's OpenAI-compatible Chat Completions API supports the top-level `reasoning_effort` field. In Termark, select the `OpenAI` provider type and use Gemini's OpenAI-compatible endpoint.

```json
{
  "reasoning_effort": "high"
}
```

The compatibility endpoint currently accepts `minimal`, `low`, `medium`, and `high`, which Gemini then maps to the model's native `thinking_level` or `thinking_budget`. If the field is omitted, the model's default effort or budget is used.

Only Gemini 2.5 models that allow thinking to be disabled can use:

```json
{
  "reasoning_effort": "none"
}
```

Thinking cannot be disabled for Gemini 2.5 Pro or the Gemini 3 family. Do not set `reasoning_effort` together with Gemini's native `thinking_level` or `thinking_budget`, because these parameters control the same capability and the official compatibility endpoint does not allow them to be used together.

The current official OpenAI compatibility documentation covers Chat Completions. When using Gemini in Termark, prefer the `OpenAI` provider type. Do not assume that Gemini's compatibility endpoint supports `OpenAI-Response` merely because OpenAI itself supports the Responses API.

## Grok

In xAI's current documentation, Grok 4.5 and Grok 4.6 use `reasoning.effort` with the Responses API. Select `OpenAI-Response` in Termark:

```json
{
  "reasoning": {
    "effort": "high"
  }
}
```

The current effort levels are `low`, `medium`, `high`, and `xhigh`, with `high` as the default. Thinking cannot be disabled for Grok 4.5/4.6, so do not set it to `none`.

Other Grok models may support different values. If you use an older model or another Grok family, consult the xAI documentation for that model instead of applying the 4.5/4.6 value range directly.

## Ollama

Termark calls local Ollama models through Ollama's OpenAI-compatible `/v1/chat/completions` endpoint, so select the `OpenAI` provider type. Ollama's compatibility endpoint supports `reasoning_effort`:

```json
{
  "reasoning_effort": "high"
}
```

Ollama's compatibility layer lists `low`, `medium`, `high`, `max`, and `none`, but whether each value takes effect ultimately depends on the local model.

`gpt-oss` is an exception that requires special attention: it accepts only `low`, `medium`, and `high`, and reasoning cannot be disabled completely. Boolean values are also ignored.

Ollama's native `/api/chat` endpoint uses the `think` field, but Termark's Ollama preset uses the OpenAI-compatible endpoint. Do not copy examples such as `{"think": ...}` that apply only to `/api/chat` into Termark; use the compatibility endpoint's `reasoning_effort` field instead.

## OpenRouter

OpenRouter provides a unified `reasoning` object for reasoning models from different providers. Select the `OpenAI` provider type when using OpenRouter in Termark.

To set reasoning effort by level:

```json
{
  "reasoning": {
    "effort": "high"
  }
}
```

To set the maximum number of reasoning tokens directly:

```json
{
  "reasoning": {
    "max_tokens": 8192
  }
}
```

To enable thinking with the model or gateway default configuration:

```json
{
  "reasoning": {
    "enabled": true
  }
}
```

OpenRouter maps `effort` or `max_tokens` to upstream parameters based on the specific model. The available effort levels, support for token budgets, and whether reasoning is mandatory all depend on the capability information returned by OpenRouter's model API.

You can also set `"exclude": true` to let the model continue reasoning without returning the reasoning content in the response. This field only controls whether reasoning content is returned; it does not disable reasoning.

### Using Claude Through OpenRouter

When connecting directly to Claude, Termark uses the `Anthropic` provider type, and the current UI does not display **Additional Request Parameters (JSON)**. Therefore, you cannot use `CustomRequestBody` to send Claude's native `thinking`, `budget_tokens`, or `output_config.effort` parameters.

If you call Claude through an OpenAI-compatible gateway such as OpenRouter, set the provider type to `OpenAI` and use the gateway's `reasoning` object. For example:

```json
{
  "reasoning": {
    "effort": "high"
  }
}
```

This is OpenRouter's unified parameter, not a native Anthropic Messages API parameter. Some Claude tool-call workflows require complete structured thinking blocks to be preserved. If the gateway does not return a format that Termark currently recognizes as `reasoning_content`, reasoning display or consecutive tool calls may be incomplete.

## Other OpenAI-Compatible Models

Although MiniMax, Doubao, models hosted by SiliconFlow, and other proxy services may be compatible with the OpenAI request format, there is no universal standard for reasoning effort. Common formats include:

- A top-level enum field: `reasoning_effort`;
- A nested enum field: `reasoning.effort`;
- A thinking toggle: `thinking` or `enable_thinking`;
- A token limit: `thinking_budget`.

Do not guess fields based only on the model name. First confirm whether the provider documentation describes the Chat Completions API or the Responses API. Then copy the reasoning fields from the official HTTP request example, excluding `model`, input messages, and tools, into **Additional Request Parameters (JSON)** exactly as shown.

For example, if the official request body for a compatible service is:

```json
{
  "model": "example-model",
  "messages": [],
  "reasoning_effort": "high"
}
```

Then you only need to enter the following in Termark:

```json
{
  "reasoning_effort": "high"
}
```

## Troubleshooting

### An Invalid JSON Error Appears When Saving

**Additional Request Parameters (JSON)** must be a valid JSON object. Field names and string values must use double quotes, comments are not allowed, and there must not be a trailing comma after the last field.

Correct example:

```json
{
  "reasoning_effort": "high"
}
```

Incorrect example:

```text
{
  reasoning_effort: 'high',
}
```

### The API Returns `unknown parameter` or `invalid value`

Common causes include:

- The wrong provider type is selected, mixing fields from the Chat Completions and Responses APIs;
- The current model does not support that reasoning parameter or effort value;
- The proxy service does not fully pass through upstream fields;
- The provider has changed the model's capabilities or parameter format.

First reset the configuration to `{}` and test again. If a basic conversation works, add fields one at a time according to the current provider documentation.

### The Model Does Not Seem to Reason More After Configuration

Reasoning effort is a hint for the model's reasoning budget. It does not guarantee that every question will use more tokens or that every answer will be better. Even with a higher effort level, a model may finish simple questions quickly; complex tasks usually make the difference easier to observe.

Start with `medium` or the provider default. Increase the effort only when it is genuinely needed for tasks such as complex code analysis, troubleshooting, or mathematical reasoning.

### Why Do Existing Conversations Behave Unexpectedly After a Change?

Models can use different formats and retention rules for historical reasoning content. After switching the model, provider type, or reasoning protocol, start a new AI conversation for testing to avoid incompatibilities between reasoning history from an existing conversation and the new model's protocol.

## Official Documentation

- [OpenAI Reasoning models](https://developers.openai.com/api/docs/guides/reasoning)
- [OpenAI Chat Completions API](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create)
- [DeepSeek Thinking Mode](https://api-docs.deepseek.com/guides/thinking_mode)
- [Alibaba Cloud Model Studio: Deep thinking](https://www.alibabacloud.com/help/en/model-studio/deep-thinking)
- [Alibaba Cloud Model Studio: OpenAI Responses API compatibility](https://www.alibabacloud.com/help/en/model-studio/compatibility-with-openai-responses-api#example-deep-thinking-title)
- [Kimi API: Thinking models](https://platform.kimi.com/docs/guide/use-thinking-models)
- [Zhipu BigModel: Deep thinking](https://docs.bigmodel.cn/cn/guide/capabilities/thinking)
- [Gemini API: OpenAI compatibility](https://ai.google.dev/gemini-api/docs/openai#thinking)
- [xAI: Reasoning](https://docs.x.ai/developers/model-capabilities/text/reasoning)
- [Ollama: OpenAI compatibility](https://docs.ollama.com/openai)
- [Ollama: Thinking](https://docs.ollama.com/capabilities/thinking)
- [OpenRouter: Reasoning tokens](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens)
- [Claude: Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)
- [Claude: Effort](https://platform.claude.com/docs/en/build-with-claude/effort)

Model capabilities and parameters change as providers update their services. If an API returns a parameter error, refer to the latest official documentation for the specific model and API endpoint you are using.
