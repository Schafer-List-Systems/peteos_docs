# Invocation Hooks

Hooks let you observe and control agent invocations. Pass a `hooks` dict as the `hooks` parameter to [`invoke_agent()`](../reference/agentic-object-base.md#invoke_agent):

For a concrete example of an `on_tool_call` hook in action, see **[adventure-dungeon](../examples/adventure-dungeon.py)**.

```python
hooks = {
    "on_invoke": [lambda ctx: print(ctx["prompt"])],
    "on_tool_call": [lambda ctx: print(f"Tool: {ctx['tool_name']}")],
    "on_invoke_complete": [lambda ctx: print(ctx["result"])],
}
result = await obj.invoke_agent(
    prompt="Analyze this data.",
    hooks=hooks,
)
```

## Hook Types

### `on_invoke`

Fires **before** the agent starts reasoning. You can inspect the prompt or prevent the invocation.

| Key | Type | Description |
|---|---|---|
| `role` | `str` | The agent's role name |
| `prompt` | `str` | The prompt passed to `invoke_agent()` |
| `session` | `Session` | The session object |

```python
def log_and_guard(ctx):
    print(f"[{ctx['role']}] Prompt: {ctx['prompt']!r}")
    return None  # allow
    # return "Error message"  # abort and return to caller

result = await obj.invoke_agent(
    prompt="Analyze this data.",
    hooks={"on_invoke": [log_and_guard]},
)
```

The hook receives a context dict with `role`, `prompt`, and `session`. Return `None` to allow the invocation, or a non-`None` string to abort it — the agent is not started and the string is returned as an `Error` to the caller.

### `on_invoke_complete`

Fires **after** the agent finishes, regardless of outcome.

| Key | Type | Description |
|---|---|---|
| `role` | `str` | The agent's role name |
| `prompt` | `str` | The prompt passed to `invoke_agent()` |
| `session` | `Session` | The session object |
| `result` | `Any` | The agent's return value or an `Error` object |

```python
def log_result(ctx):
    print(f"[{ctx['role']}] Done: {type(ctx['result']).__name__}")

result = await obj.invoke_agent(
    prompt="Analyze this data.",
    hooks={"on_invoke_complete": [log_result]},
)
```

The context dict includes `role`, `prompt`, `session`, and `result` — the agent's return value or an `Error` object.

### `on_tool_call`

Fires **before each tool execution**. Use this to monitor or block specific tools.

| Key | Type | Description |
|---|---|---|
| `role` | `str` | The agent's role name |
| `session` | `Session` | The session object |
| `tool_name` | `str` | The name of the tool being called |
| `arguments` | `dict` | The parsed arguments for the tool |

```python
def block_python_exec(ctx):
    if ctx["tool_name"] == "python_exec":
        return "Code execution is not allowed"
    return None  # allow

result = await obj.invoke_agent(
    prompt="Write a file and count its lines.",
    hooks={"on_tool_call": [block_python_exec]},
)
```

The context dict includes `role`, `session`, `tool_name`, and `arguments`.
Return `None` to allow execution, or a non-`None` string to deny it — the tool and all remaining tools in the same group are skipped, and the agent is given another reasoning turn.

### `before_tool_execution`

Fires **right before a tool executes** — after the tool has been selected and arguments cast, but before the actual function runs. Use this to inject behavior or block execution at the last moment.

```python
def log_execution(runner, tool_call):
    print(f"Running {tool_call.name}")
    return None  # allow

result = await obj.invoke_agent(
    prompt="Analyze this data.",
    hooks={"before_tool_execution": [log_execution]},
)
```

The hook receives `(runner, tool_call)` directly — `runner` is the active Runner, and `tool_call` is a `ContentPart` with `name`, `arguments`, and `call_id`. Return a tuple `(False, "reason")` to deny, or `None` to allow.

### `after_tool_execution`

Fires **after a tool finishes** — whether it succeeded, failed, or returned `None`. Use this to log results, update external state, or trigger follow-up actions.

```python
def log_result(runner, tool_call, result_str, success):
    print(f"{tool_call.name} → {result_str} (ok={success})")
    return None

result = await obj.invoke_agent(
    prompt="Analyze this data.",
    hooks={"after_tool_execution": [log_result]},
)
```

The hook receives `(runner, tool_call, result_str, success)`:
- `runner`: the active Runner
- `tool_call`: the `ContentPart` that was executed
- `result_str`: the string the tool returned, or `"None"` if it returned `None`
- `success`: `True` if the tool succeeded, `False` otherwise

### `before_send_to_chatbot`

Fires **before the context is sent to the LLM** for a reasoning turn. The context holds the full conversation so far. Use this to inspect, log, or enrich the context before the model reasons.

```python
def log_context(runner, active_context):
    print(f"Tokens in context: {len(str(active_context))}")
    return None

result = await obj.invoke_agent(
    prompt="Analyze this data.",
    hooks={"before_send_to_chatbot": [log_context]},
)
```

The hook receives `(runner, active_context)`. `active_context` is the session's context object. Return `None` to proceed, or an `ExecStatus` to override the step result.

### `after_step`

Fires **after each reasoning step completes** — whether the step produced text, ran tools, or is waiting. Use this to monitor progress, apply policies, or inject state between turns.

```python
def watch_progress(runner, status):
    print(f"Step ended with: {status}")
    return None

result = await obj.invoke_agent(
    prompt="Analyze this data.",
    hooks={"after_step": [watch_progress]},
)
```

The hook receives `(runner, status)`. `status` is an `ExecStatus` (`PENDING`, `CONTINUE`, `FINISHED`, `CRITICAL`). Return `None` to let execution continue, or an `ExecStatus` to override — for example, returning `ExecStatus.CRITICAL` stops the run loop.

### `after_message_append`

Fires **after a message is appended to the session context** — this happens for every LLM response, user message, and internal notification. Use this to react to new context content in real time.

```python
def on_message(runner, message):
    print(f"New message: {message.role}")
    return None

result = await obj.invoke_agent(
    prompt="Analyze this data.",
    hooks={"after_message_append": [on_message]},
)
```

The hook receives `(runner, message)`. `message` is the `Message` that was appended. Return `None`.

### `before_notification_publish`

Fires **before an internal notification is published** to subscribed channels. Notifications are how the runner broadcasts state changes to external consumers (e.g., a UI). Use this to observe or intercept system messages.

```python
def on_notification(runner, message):
    print(f"Notifying: {message.role}")
    return None

result = await obj.invoke_agent(
    prompt="Analyze this data.",
    hooks={"before_notification_publish": [on_notification]},
)
```

The hook receives `(runner, message)`. `message` is the notification `Message`. Return `None`.

### `on_truncation_exhausted`

Fires when the **LLM keeps getting cut off by the token limit** after repeated retries. This means the model produced a too-long response and the system gave it a conciseness reminder, but it kept overflowing. Use this to log failures, reset state, or replace the context.

```python
def on_exhausted(counter, max_retries):
    print(f"Truncation limit hit: {counter}/{max_retries}")
    raise RuntimeError("Giving up")

result = await obj.invoke_agent(
    prompt="Analyze this data.",
    hooks={"on_truncation_exhausted": [on_exhausted]},
)
```

The hook receives `(counter, max_retries)` — the current count and the limit. The hook is called **instead of** raising, giving you a chance to handle it. If it returns normally, the RuntimeError is still raised afterward.

## Recursive Propagation

Hooks are automatically forwarded to every sub-agent invocation via `invoke()`.
If an agentic object calls another via `invoke()`, the same hooks fire for the sub-agent, giving you visibility across the entire invocation tree.

**Note:** Hooks are not forwarded when an agent calls another agent's `invoke_agent()` from within a tool (e.g., `self._other.invoke_agent("message")`).
In that case, the child agent's invocation receives no hooks — only sub-agent calls via `invoke()` propagate hooks.

## Combining Hooks

Register multiple hooks in the same list. They execute in registration order — the first hook runs before the second.

```python
def log1(ctx):
    print(f"[{ctx['role']}] first hook")

def log2(ctx):
    print(f"[{ctx['role']}] second hook")

result = await obj.invoke_agent(
    prompt="Analyze this data.",
    hooks={"on_invoke": [log1, log2]},
)
```

Both hooks fire when `on_invoke` is invoked, with `log1` executing before `log2`.