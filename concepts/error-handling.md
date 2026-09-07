# Error Handling

`invoke_agent()` returns a structured result on success. On failure, it either returns an `Error` value (agentic failure) or raises an exception (framework/tool failure).

## Error (returned, not raised)

`Error` is an agentic failure — the agent reasoned through the task and concluded it could not produce the requested output. It is a return value, just like a successful result.

`Error` can arise from these scenarios:

| Cause | Description |
|---|---|
| `produce_error` | The agent calls the `produce_error` tool with a message explaining why it failed. |
| Schema validation failure | The agent produced output that does not match the expected output schema after all retries. |
| Max turns exceeded | The agent finished a step without calling `produce_output` or `produce_error` for more than the allowed number of turns. |
| Timeout exceeded | The agent did not produce output or error within the timeout period. |
| Invocation hook | An `on_invoke` hook returns a non-`None` string, aborting the agent before it starts. |
| Persistent session conflict | A request is made on a persistent session that is already active. |

When the agent calls `produce_error`, the framework treats it like any other tool call: the agent can reason about the error, attempt another approach, or retry.

## Exceptions (raised, not returned)

Exceptions represent framework or tool failures — something broke inside the execution pipeline rather than the agent failing. These propagate out of `invoke_agent()` with `raise`.

| Cause | Description |
|---|---|
| Tool call failure | A tool decorated with `@tool` raises an exception during execution. |
| Internal framework error | `ValueError` (no agent available, invalid configuration), `TimeoutError` (lock not acquired within timeout), or other unexpected conditions. |
| System prompt hook exception | A system prompt hook raises an exception during session setup. |

> **Note:** The behavior of tool exceptions — whether they propagate out of `invoke_agent()` or are caught and shown to the agent — is under discussion and may change.

## Error Propagation

In a chain of agentic objects, the behavior depends on how the call is made:

- **`invoke_agent()`** — `Error` values are returned; exceptions are raised. The caller handles each independently.
- **`invoke()` (sub-agent)** — The calling agent executes in a sandbox. If the target raises an exception from a tool call, it is raised in the sandbox. `Error` values from the target's `produce_error` are returned through `invoke()` as the result.
