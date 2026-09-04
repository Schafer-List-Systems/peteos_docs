# Backends

The ChatBotManager configures which LLM APIs the agent can use. Backends are automatically loaded from `peteos.json` on `import peteos`. Manual registration is available for dynamic or runtime scenarios.

## Automatic Configuration

Backends are configured by placing a `peteos.json` file in one of the standard discovery locations described in [Configuration](./index.md). The `backends` array inside the JSON configures LLM endpoints:

```json
{
    "backends": [
        {
            "name": "production",
            "url": "https://api.openai.com/v1",
            "api_type": "openai",
            "streaming": true,
            "max_tokens": 4096,
            "model_priorities": {
                "gpt-4-turbo": 100,
                "gpt-4": 80
            },
            "retry_delays": [0, 1, 3],
            "timeout": 30
        },
        {
            "name": "local",
            "url": "http://localhost:8000",
            "api_type": "openai"
        }
    ]
}
```

No Python code is needed — backends are loaded and registered automatically.

### Backend Config Fields

| Field | Type | Default | Purpose |
|---|---|---|---|
| `name` | string | _(required)_ | Unique backend identifier. |
| `url` | string | _(required)_ | API base URL. |
| `api_type` | string | auto-detected | API provider: `"openai"`, `"anthropic"`, or `"gemini"`. |
| `api_key` | string | | API key for authentication. |
| `chat_endpoint` | string | API-specific default | Custom chat endpoint path (e.g. `/chat/completions`). |
| `models_endpoint` | string | API-specific default | Custom models endpoint path. |
| `streaming` | bool | `false` | Use streaming mode by default. |
| `max_tokens` | int | `4096` | Maximum tokens to generate. |
| `model_priorities` | object | `{}` | Map of model IDs to priority integers. Higher values take precedence. |
| `retry_delays` | float[] | `[0, 1, 3]` | Delay in seconds before each retry attempt. |
| `timeout` | float | provider-specific | HTTP request timeout in seconds. |

## Manual Configuration

For dynamic scenarios, you can register backends manually at runtime. The ChatBotManager is a class-method-only singleton — there is exactly one manager shared across the entire application.

### Register a Backend by Name and URL

The manager auto-detects the API type (OpenAI, Anthropic, or Gemini) and discovers available models:

```python
from peteos.chatbot.manager import ChatBotManager

await ChatBotManager.add_backend("local", "http://localhost:8000")
```

You can also specify the API type explicitly to skip auto-detection:

```python
await ChatBotManager.add_backend("anthropic-api", "https://api.anthropic.com", api_type="anthropic")
```

### Load from JSON Programmatically

```python
from peteos.chatbot.manager import ChatBotManager
import asyncio

config = {
    "backends": [
        {"name": "local", "url": "http://localhost:8000"},
        {"name": "gemini", "url": "https://generativelanguage.googleapis.com", "api_type": "gemini"},
    ]
}

await ChatBotManager.load_from_json(config)
```

`load_from_json` clears all previously registered backends before loading — it replaces state entirely.

## Security

API keys from the configuration are never stored in a way that can be read back from the program.
After the backend is set up, the key is removed from all user-accessible runtime data structures.
This mitigates the risk of API key exposure through internal data structures via prompt injection attacks.
