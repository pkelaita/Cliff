# Cliff Supported Models

Cliff uses [L2M2](https://github.com/pkelaita/l2m2), which allows it to support a wide variety of models. To add a new API-based provider, run

```
cliff --config add [provider]
```

To set a model as the default model, run

```
cliff --config default-model [model name]
```

For example, to add a Mistral API key, tell cliff to use mistral-large as its default model, and then use Cliff with the mistral-large model, you would run:

```
cliff --config add mistral [your-mistral-api-key]
cliff --config default-model mistral-large
cliff list my five biggest files
```

Below are Cliff's supported API-based models. Note that model name should be used to specify the model, not the model version.

<!--start-model-table-->

| Model Name | Provider(s) | Model Version(s) |
| --- | --- | --- |
| `o3-mini` | [OpenAI](https://openai.com/api/) | `o3-mini-2025-01-31` |
| `o1` | [OpenAI](https://openai.com/api/) | `o1-2024-12-17` |
| `o1-preview` | [OpenAI](https://openai.com/api/) | `o1-preview-2024-09-12` |
| `o1-mini` | [OpenAI](https://openai.com/api/) | `o1-mini-2024-09-12` |
| `gpt-4o` | [OpenAI](https://openai.com/api/) | `gpt-4o-2024-11-20` |
| `gpt-4o-mini` | [OpenAI](https://openai.com/api/) | `gpt-4o-mini-2024-07-18` |
| `gpt-4-turbo` | [OpenAI](https://openai.com/api/) | `gpt-4-turbo-2024-04-09` |
| `gpt-3.5-turbo` | [OpenAI](https://openai.com/api/) | `gpt-3.5-turbo-0125` |
| `gemini-2.0-pro` | [Google](https://ai.google.dev/) | `gemini-2.0-pro-exp-02-05` |
| `gemini-2.0-flash` | [Google](https://ai.google.dev/) | `gemini-2.0-flash-001` |
| `gemini-2.0-flash-lite` | [Google](https://ai.google.dev/) | `gemini-2.0-flash-lite-preview-02-05` |
| `gemini-1.5-flash` | [Google](https://ai.google.dev/) | `gemini-1.5-flash-001` |
| `gemini-1.5-flash-8b` | [Google](https://ai.google.dev/) | `gemini-1.5-flash-8b` |
| `gemini-1.5-pro` | [Google](https://ai.google.dev/) | `gemini-1.5-pro` |
| `claude-3.7-sonnet` | [Anthropic](https://www.anthropic.com/api) | `claude-3-7-sonnet-20250219` |
| `claude-3.5-sonnet` | [Anthropic](https://www.anthropic.com/api) | `claude-3-5-sonnet-20241022` |
| `claude-3.5-haiku` | [Anthropic](https://www.anthropic.com/api) | `claude-3-5-haiku-20241022` |
| `claude-3-opus` | [Anthropic](https://www.anthropic.com/api) | `claude-3-opus-20240229` |
| `claude-3-sonnet` | [Anthropic](https://www.anthropic.com/api) | `claude-3-sonnet-20240229` |
| `claude-3-haiku` | [Anthropic](https://www.anthropic.com/api) | `claude-3-haiku-20240307` |
| `command-r` | [Cohere](https://docs.cohere.com/) | `command-r-08-2024` |
| `command-r-plus` | [Cohere](https://docs.cohere.com/) | `command-r-plus-08-2024` |
| `command-r7b` | [Cohere](https://docs.cohere.com/) | `command-r7b-12-2024` |
| `mistral-large` | [Mistral](https://docs.mistral.ai/deployment/laplateforme/overview/) | `mistral-large-2411` |
| `mistral-small` | [Mistral](https://docs.mistral.ai/deployment/laplateforme/overview/) | `mistral-small-2501` |
| `ministral-3b` | [Mistral](https://docs.mistral.ai/deployment/laplateforme/overview/) | `ministral-3b-2410` |
| `ministral-8b` | [Mistral](https://docs.mistral.ai/deployment/laplateforme/overview/) | `ministral-8b-2410` |
| `mixtral-8x7b` | [Groq](https://wow.groq.com/) | `mixtral-8x7b-32768` |
| `gemma-2-9b` | [Groq](https://wow.groq.com/) | `gemma2-9b-it` |
| `llama-3.3-70b` | [Groq](https://wow.groq.com/), [Cerebras](https://inference-docs.cerebras.ai) | `llama-3.3-70b-versatile`, `llama3.3-70b` |
| `llama-3.2-3b` | [Groq](https://wow.groq.com/) | `llama-3.2-3b-preview` |
| `llama-3.2-1b` | [Groq](https://wow.groq.com/) | `llama-3.2-1b-preview` |
| `llama-3.1-405b` | [Replicate](https://replicate.com/) | `meta/meta-llama-3.1-405b-instruct` |
| `llama-3.1-8b` | [Groq](https://wow.groq.com/), [Cerebras](https://inference-docs.cerebras.ai) | `llama-3.1-8b-instant`, `llama3.1-8b` |
| `llama-3-70b` | [Groq](https://wow.groq.com/), [Replicate](https://replicate.com/) | `llama3-70b-8192`, `meta/meta-llama-3-70b-instruct` |
| `llama-3-8b` | [Groq](https://wow.groq.com/), [Replicate](https://replicate.com/) | `llama3-8b-8192`, `meta/meta-llama-3-8b-instruct` |
| `qwen-2.5-32b` | [Groq](https://wow.groq.com/) | `qwen-2.5-32b` |
| `deepseek-r1-distill-qwen-32b` | [Groq](https://wow.groq.com/) | `deepseek-r1-distill-qwen-32b` |
| `deepseek-r1-distill-llama-70b` | [Groq](https://wow.groq.com/) | `deepseek-r1-distill-llama-70b` |

<!--end-model-table-->

Additionally, Cliff supports any local model running with [Ollama](https://ollama.ai/). To add a local model to Cliff, run

```
cliff --config add ollama [model name]
```

The model must be available locally with Ollama in order for Cliff to use it (i.e., `ollama serve` must be active on `localhost:11434` and the model name must show up when running `ollama list`).

For example, to add the `qwen2.5-coder:7b` model to Cliff, you would run

```
cliff --config add ollama qwen2.5-coder:7b
```

Note that some models may be available from multiple providers, such as `llama-3.3-70b` from both Groq and Cerebras. If only one of the providers have been added to Cliff, you can use such models normally. If both providers have been added, you must tell Cliff to prefer one of the providers for that model. For example, to tell Cliff to prefer Groq for `llama-3.3-70b`, run

```
cliff --config default-provider groq
```
