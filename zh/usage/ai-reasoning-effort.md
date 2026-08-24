---
title: "Termark AI 模型思考强度配置：GPT、DeepSeek、Qwen、Kimi、GLM 等"
description: "通过附加请求参数（CustomRequestBody）配置 GPT、DeepSeek、Qwen、Kimi、GLM、Gemini、Grok、Ollama 等模型的思考开关、思考强度和思考 token 上限。"
outline: deep
---

# AI 模型思考强度配置

Termark 可以通过 API 环境中的“附加请求参数（JSON）”配置模型的思考开关和思考强度。该配置在程序内部对应 `CustomRequestBody`。

不同供应商、不同接口使用的字段并不统一。例如，OpenAI Chat Completions 使用 `reasoning_effort`，OpenAI Responses API 使用 `reasoning.effort`，Qwen 的 Chat Completions 接口则使用 `enable_thinking` 和 `thinking_budget`。配置前必须先确认当前 API 环境的“供应商类型”。

## 在哪里配置

1. 打开 Termark 设置，进入“AI 助手”。
2. 新增或编辑一个 API 环境。
3. 展开“高级设置”。
4. 在“附加请求参数（JSON）”中填写本文提供的 JSON。
5. 保存 API 环境，然后执行连接测试或发起一轮新对话。

填写 `{}` 表示不附加任何参数，模型将使用服务端默认行为。

## 先确认供应商类型

Termark 当前提供以下三种供应商类型：

| Termark 供应商类型 | 实际请求路径 | 思考参数的常见结构 |
|---------------------|--------------|--------------------|
| `OpenAI` | `/v1/chat/completions` | 顶层字段，例如 `reasoning_effort` |
| `OpenAI-Response` | `/v1/responses` | 嵌套字段，例如 `reasoning.effort` |
| `Anthropic` | `/v1/messages` | 不使用“附加请求参数（JSON）” |

“附加请求参数（JSON）”只在 `OpenAI` 和 `OpenAI-Response` 类型下可用。Termark 会把 JSON 顶层字段合并到每次请求中，但不会验证供应商是否支持这些字段，也不会在 Chat Completions 和 Responses 两种格式之间自动转换。

::: warning
不要在附加请求参数中设置 `model`、`messages`、`input`、`instructions`、`tools`、`tool_choice`、`parallel_tool_calls`、`stream` 或 `store`。这些字段由 Termark 管理，覆盖后可能导致对话、工具调用、流式输出或上下文处理异常。
:::

## 快速对照

| 模型服务 | Termark 供应商类型 | 开启或配置思考 | 关闭思考 |
|----------|---------------------|----------------|----------|
| OpenAI GPT | `OpenAI` | `{"reasoning_effort":"high"}` | 使用模型支持的 `none`，或删除该字段恢复模型默认值 |
| OpenAI GPT | `OpenAI-Response` | `{"reasoning":{"effort":"high"}}` | 使用模型支持的 `none`，或删除该字段恢复模型默认值 |
| DeepSeek | `OpenAI` | `{"thinking":{"type":"enabled"},"reasoning_effort":"high"}` | `{"thinking":{"type":"disabled"}}` |
| DeepSeek | `OpenAI-Response` | `{"reasoning":{"effort":"high"}}` | `{"reasoning":{"effort":"none"}}` |
| Qwen | `OpenAI` | `{"enable_thinking":true,"thinking_budget":8192}` | `{"enable_thinking":false}` |
| Qwen | `OpenAI-Response` | `{"reasoning":{"effort":"high"}}` | `{"reasoning":{"effort":"none"}}` |
| Kimi K3 | `OpenAI` | `{"reasoning_effort":"high"}` | 不支持关闭思考 |
| Kimi K2.6/K2.5 | `OpenAI` | `{"thinking":{"type":"enabled"}}` | `{"thinking":{"type":"disabled"}}` |
| GLM-5.2 及以上 | `OpenAI` | `{"thinking":{"type":"enabled"},"reasoning_effort":"high"}` | 取决于型号；GLM-5.3 不支持关闭 |
| Gemini | `OpenAI` | `{"reasoning_effort":"high"}` | 只有部分 Gemini 2.5 型号支持 `none` |
| Grok 4.5/4.6 | `OpenAI-Response` | `{"reasoning":{"effort":"high"}}` | 不支持关闭思考 |
| Ollama | `OpenAI` | `{"reasoning_effort":"high"}` | 取决于本地模型 |
| OpenRouter | `OpenAI` | `{"reasoning":{"effort":"high"}}` | 取决于路由到的模型 |
| Claude 直连 | `Anthropic` | 当前不能通过该字段配置 | 当前不能通过该字段配置 |

表中的 JSON 为单行速查形式。实际填写时可以使用下文更易读的多行格式。

## OpenAI GPT

### 使用 OpenAI 类型

供应商类型选择 `OpenAI` 时，Termark 调用 Chat Completions API。使用顶层 `reasoning_effort` 配置思考强度：

```json
{
  "reasoning_effort": "high"
}
```

OpenAI 当前定义的可能值包括：

| 值 | 一般含义 |
|----|----------|
| `none` | 不进行额外推理，前提是所选模型支持 |
| `minimal` | 最少推理，优先降低延迟和 token 消耗 |
| `low` | 较低思考强度 |
| `medium` | 平衡速度、消耗和回答质量 |
| `high` | 较高思考强度，适合复杂分析和代码任务 |
| `xhigh` | 更高思考强度，仅部分模型支持 |
| `max` | 最高思考强度，仅部分模型支持 |

具体模型不一定支持表中的全部值，默认值也由模型决定。如果接口返回“不支持该值”之类的错误，应按该模型的官方文档降低强度，或删除 `reasoning_effort` 让模型使用默认值。

### 使用 OpenAI-Response 类型

供应商类型选择 `OpenAI-Response` 时，Termark 调用 Responses API。该接口使用嵌套的 `reasoning.effort`：

```json
{
  "reasoning": {
    "effort": "high"
  }
}
```

可选值同样取决于具体模型。不要在 `OpenAI-Response` 类型下填写顶层 `reasoning_effort`，否则服务端可能忽略参数或直接返回参数错误。

## DeepSeek

DeepSeek 的思考参数同时受到接口类型影响。

### 使用 OpenAI 类型

开启思考并设置为高强度：

```json
{
  "thinking": {
    "type": "enabled"
  },
  "reasoning_effort": "high"
}
```

DeepSeek Chat Completions 当前支持的思考强度为 `low`、`high` 和 `max`。

如果只想开启思考并使用模型默认强度，可以省略 `reasoning_effort`：

```json
{
  "thinking": {
    "type": "enabled"
  }
}
```

关闭思考：

```json
{
  "thinking": {
    "type": "disabled"
  }
}
```

关闭时建议同时删除 `reasoning_effort`，避免向不需要思考的请求继续发送强度参数。

### 使用 OpenAI-Response 类型

DeepSeek Responses API 使用 `reasoning.effort`，当前可用值为 `none`、`low`、`high` 和 `max`：

```json
{
  "reasoning": {
    "effort": "high"
  }
}
```

将 `effort` 设置为 `none` 可以关闭思考：

```json
{
  "reasoning": {
    "effort": "none"
  }
}
```

## Qwen

Qwen 的 Chat Completions 接口和 Responses API 使用两套不同的思考控制方式。

### 使用 OpenAI 类型

对于支持混合思考模式的 Qwen 模型，可以通过 `enable_thinking` 开启思考，并用 `thinking_budget` 限制思考过程最多使用的 token 数：

```json
{
  "enable_thinking": true,
  "thinking_budget": 8192
}
```

`thinking_budget` 是思考 token 上限，不是固定消耗量。数值越大，模型越有空间处理复杂问题，但通常也会增加延迟和 token 消耗。不同模型的有效范围和默认上限不同，应以所选模型的官方说明为准。

只开启思考、使用模型默认上限：

```json
{
  "enable_thinking": true
}
```

关闭思考：

```json
{
  "enable_thinking": false
}
```

部分纯思考模型始终会推理，不支持通过 `enable_thinking` 关闭。部分开源 Qwen 模型只支持流式思考；Termark 的 AI 对话本身使用流式请求，无需额外设置 `stream`。

阿里云百炼中的某些 Qwen，以及部署在百炼或 Moonshot AI 上的特定 Kimi 模型，还可能支持以下扩展参数：

```json
{
  "enable_thinking": true,
  "preserve_thinking": true
}
```

`preserve_thinking` 用于把之前轮次的思考内容继续传给模型，它不控制思考强度，并且只受部分模型和部署渠道支持。Kimi 官方直连接口使用的是下文所述 `thinking.keep`，不要把两个字段混用。除非当前 API 端点的官方文档明确列出支持，否则不要添加 `preserve_thinking`。

### 使用 OpenAI-Response 类型

Qwen 的 Responses API 使用 `reasoning.effort`：

```json
{
  "reasoning": {
    "effort": "high"
  }
}
```

当前支持 `none`、`minimal`、`low`、`medium` 和 `high`，其中 `none` 表示关闭思考。Responses API 下应使用 `reasoning.effort`，不要再同时填写 `enable_thinking` 或 `thinking_budget`。

## Kimi

Kimi 不同型号的思考参数差异较大，不能把同一份 JSON 用于整个 Kimi 系列。以下配置适用于 Kimi 官方 OpenAI 兼容 Chat Completions 接口，因此 Termark 供应商类型选择 `OpenAI`。

### Kimi K3

`kimi-k3` 始终进行推理，通过顶层 `reasoning_effort` 调节强度：

```json
{
  "reasoning_effort": "high"
}
```

当前支持 `low`、`high` 和 `max`，默认值为 `max`。K3 不支持关闭思考，也不应向它发送 `thinking` 对象。

### Kimi K2.6 和 K2.5

`kimi-k2.6` 和 `kimi-k2.5` 使用 `thinking.type`，默认即为 `enabled`。显式开启：

```json
{
  "thinking": {
    "type": "enabled"
  }
}
```

关闭思考：

```json
{
  "thinking": {
    "type": "disabled"
  }
}
```

`kimi-k2.6` 还支持通过 `thinking.keep` 控制是否在多轮对话中保留历史思考：

```json
{
  "thinking": {
    "type": "enabled",
    "keep": "all"
  }
}
```

`keep: "all"` 不会提高当前轮的思考强度，只用于延续历史 `reasoning_content`。不填写 `keep` 时，K2.6 默认不保留之前轮次的思考。

### Kimi K2.7 Code

`kimi-k2.7-code` 始终思考并始终保留思考，不需要也不应该发送 `thinking` 参数。该型号当前没有可配置的思考强度字段，使用 `{}` 即可让它保持模型默认行为。

## GLM

智谱 GLM 的 OpenAI 兼容 Chat Completions 接口使用 `thinking.type` 控制思考开关。GLM-5.2 及以上还可以通过 `reasoning_effort` 控制推理程度。

开启思考并设置高强度：

```json
{
  "thinking": {
    "type": "enabled"
  },
  "reasoning_effort": "high"
}
```

不同型号支持的强度不同：

| 型号 | `reasoning_effort` 可用值 | 说明 |
|------|----------------------------|------|
| GLM-5.3 | `low`、`high`、`max` | 不支持关闭思考，传 `thinking.type: "disabled"` 会报错 |
| GLM-5.2 | `none`、`minimal`、`low`、`medium`、`high`、`xhigh`、`max` | `none/minimal` 放弃思考；`low/medium` 映射为 `high`；`xhigh` 映射为 `max` |
| GLM-5.1、GLM-5、GLM-4.7、GLM-4.6、GLM-4.5 等 | 不支持 `reasoning_effort` | 只使用模型支持的 `thinking.type` |

对于明确支持关闭思考的型号，可以填写：

```json
{
  "thinking": {
    "type": "disabled"
  }
}
```

不要将该关闭配置用于 GLM-5.3。

部分 GLM 型号还支持在 `thinking` 对象中设置 `clear_thinking: false`，用于保留工具调用过程中的思考内容。它不是强度参数，只有在所选型号和接口文档明确支持时才应使用：

```json
{
  "thinking": {
    "type": "enabled",
    "clear_thinking": false
  }
}
```

## Gemini

Google Gemini 的 OpenAI 兼容 Chat Completions 接口支持顶层 `reasoning_effort`。在 Termark 中应选择 `OpenAI` 类型，并使用 Gemini 的 OpenAI 兼容地址。

```json
{
  "reasoning_effort": "high"
}
```

兼容接口当前接受 `minimal`、`low`、`medium` 和 `high`，再由 Gemini 按型号映射为原生的 `thinking_level` 或 `thinking_budget`。不填写时使用模型默认强度或预算。

只有允许关闭思考的 Gemini 2.5 型号可以使用：

```json
{
  "reasoning_effort": "none"
}
```

Gemini 2.5 Pro 和 Gemini 3 系列不能关闭思考。不要同时填写 `reasoning_effort` 和 Gemini 原生的 `thinking_level`/`thinking_budget`，因为这些参数控制的是同一项能力，官方兼容接口不允许同时使用。

当前官方 OpenAI 兼容说明覆盖 Chat Completions；在 Termark 中使用 Gemini 时优先选择 `OpenAI`，不要仅因为 OpenAI 原生支持 Responses API 就推断 Gemini 兼容端点也支持 `OpenAI-Response`。

## Grok

xAI 当前文档中的 Grok 4.5 和 Grok 4.6 通过 Responses API 的 `reasoning.effort` 调节强度。在 Termark 中选择 `OpenAI-Response`：

```json
{
  "reasoning": {
    "effort": "high"
  }
}
```

当前强度包括 `low`、`medium`、`high` 和 `xhigh`，默认值为 `high`。Grok 4.5/4.6 的思考不能关闭，因此不要设置 `none`。

其他 Grok 型号的支持值可能不同。使用较早或不同系列的 Grok 时，应查看该型号的 xAI 文档，不要直接套用 4.5/4.6 的值域。

## Ollama

Termark 通过 Ollama 的 OpenAI 兼容 `/v1/chat/completions` 接口调用本地模型，因此供应商类型选择 `OpenAI`。Ollama 的兼容接口支持 `reasoning_effort`：

```json
{
  "reasoning_effort": "high"
}
```

Ollama 兼容层列出的值包括 `low`、`medium`、`high`、`max` 和 `none`，但最终是否生效仍取决于本地模型。

`gpt-oss` 是一个需要单独注意的例外：它只接受 `low`、`medium` 和 `high`，不能完全关闭思考；传入布尔值也会被忽略。

Ollama 原生 `/api/chat` 接口使用 `think` 字段，但 Termark 的 Ollama 预设走的是 OpenAI 兼容接口。不要在 Termark 中照抄只适用于 `/api/chat` 的 `{"think": ...}` 示例，应使用兼容接口支持的 `reasoning_effort`。

## OpenRouter

OpenRouter 为不同供应商的推理模型提供统一的 `reasoning` 对象。Termark 使用 OpenRouter 时选择 `OpenAI` 类型。

按档位设置思考强度：

```json
{
  "reasoning": {
    "effort": "high"
  }
}
```

直接设置最多使用的思考 token：

```json
{
  "reasoning": {
    "max_tokens": 8192
  }
}
```

使用模型或网关默认配置开启思考：

```json
{
  "reasoning": {
    "enabled": true
  }
}
```

OpenRouter 会根据具体模型把 `effort` 或 `max_tokens` 映射到上游参数。可用档位、是否支持 token 预算、是否强制思考，都以 OpenRouter 模型接口返回的能力信息为准。

还可以设置 `"exclude": true`，让模型继续思考但不在响应中返回思考内容。该字段只影响思考内容是否返回，不会关闭推理。

### 通过 OpenRouter 使用 Claude

Termark 直连 Claude 时供应商类型为 `Anthropic`，当前界面不会显示“附加请求参数（JSON）”，因此不能通过 `CustomRequestBody` 发送 Claude 原生的 `thinking`、`budget_tokens` 或 `output_config.effort`。

如果通过 OpenRouter 等 OpenAI 兼容网关调用 Claude，应把供应商类型设为 `OpenAI`，并使用该网关定义的 `reasoning` 对象，例如：

```json
{
  "reasoning": {
    "effort": "high"
  }
}
```

这里使用的是 OpenRouter 的统一参数，不是 Anthropic 原生 Messages API 参数。某些 Claude 工具调用流程要求完整保留结构化思考块；如果网关返回的不是 Termark 当前可识别的 `reasoning_content`，思考展示或连续工具调用可能不完整。

## 其他 OpenAI 兼容模型

MiniMax、豆包、SiliconFlow 托管模型以及其他中转服务虽然可能兼容 OpenAI 请求格式，但“思考强度”没有统一标准。常见形式包括：

- 顶层枚举字段：`reasoning_effort`；
- 嵌套枚举字段：`reasoning.effort`；
- 思考开关：`thinking` 或 `enable_thinking`；
- token 上限：`thinking_budget`。

不要仅根据模型名称猜测字段。先确认服务商文档说明的是 Chat Completions 还是 Responses API，再把官方 HTTP 请求示例中除 `model`、输入消息和工具之外的思考字段，原样填写到“附加请求参数（JSON）”中。

例如，某个兼容服务的官方请求体如果是：

```json
{
  "model": "example-model",
  "messages": [],
  "reasoning_effort": "high"
}
```

那么 Termark 中只需要填写：

```json
{
  "reasoning_effort": "high"
}
```

## 常见问题

### 保存时提示 JSON 无效

“附加请求参数（JSON）”必须是一个合法的 JSON 对象。字段名和字符串值必须使用双引号，不能写注释，也不能在最后一个字段后保留逗号。

正确示例：

```json
{
  "reasoning_effort": "high"
}
```

错误示例：

```text
{
  reasoning_effort: 'high',
}
```

### 接口返回 unknown parameter 或 invalid value

通常有以下原因：

- 当前供应商类型选错，混用了 Chat Completions 和 Responses API 的字段；
- 当前模型不支持该思考参数或强度值；
- 使用的中转服务没有完整透传上游字段；
- 服务商已经调整了模型能力或参数格式。

可以先把配置恢复为 `{}` 并重新测试。如果基础对话可以使用，再按照当前服务商文档逐个添加字段。

### 配置后没有明显变得更会思考

思考强度只是模型的推理预算提示，不保证每个问题都使用更多 token，也不保证回答一定更好。简单问题即使配置较高强度，模型也可能很快完成；复杂任务则通常更容易体现差异。

建议从 `medium` 或供应商默认值开始，只有在复杂代码分析、故障排查、数学推理等任务中确实需要时再提高强度。

### 修改后为什么旧对话表现异常

不同模型对历史思考内容的格式和保留方式可能不同。切换模型、供应商类型或思考协议后，建议新建一个 AI 对话测试，避免旧对话中的思考历史与新模型协议不兼容。

## 官方资料

- [OpenAI Reasoning models](https://developers.openai.com/api/docs/guides/reasoning)
- [OpenAI Chat Completions API](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create)
- [DeepSeek Thinking Mode](https://api-docs.deepseek.com/guides/thinking_mode)
- [阿里云百炼：Deep thinking](https://www.alibabacloud.com/help/en/model-studio/deep-thinking)
- [阿里云百炼：OpenAI Responses API compatibility](https://www.alibabacloud.com/help/en/model-studio/compatibility-with-openai-responses-api#example-deep-thinking-title)
- [Kimi API：思考模型](https://platform.kimi.com/docs/guide/use-thinking-models)
- [智谱 BigModel：深度思考](https://docs.bigmodel.cn/cn/guide/capabilities/thinking)
- [Gemini API：OpenAI compatibility](https://ai.google.dev/gemini-api/docs/openai#thinking)
- [xAI：Reasoning](https://docs.x.ai/developers/model-capabilities/text/reasoning)
- [Ollama：OpenAI compatibility](https://docs.ollama.com/openai)
- [Ollama：Thinking](https://docs.ollama.com/capabilities/thinking)
- [OpenRouter：Reasoning tokens](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens)
- [Claude：Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)
- [Claude：Effort](https://platform.claude.com/docs/en/build-with-claude/effort)

模型能力和参数会随服务商更新。出现参数错误时，应以当前所用模型和 API 端点的官方文档为准。
