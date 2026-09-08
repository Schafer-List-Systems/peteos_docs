# Invocation

An agentic object is invoked through `invoke_agent()`. The agent reasons about your prompt and responds, using tools to interact with the object's state as needed.

For a complete list of arguments, see the **[AgenticObject reference](../reference/agentic-object-base.md)**.

## Basic Invocation

The simplest invocation creates an agentic object and calls `invoke_agent()` with a prompt:

```python
pete = HelloPete()
result = await pete.invoke_agent("Hello, what's your name?")
print(result)  # My name is Pete.
```

A full runnable example is available in [`examples/hello-pete.py`](../examples/hello-pete.py).

### Input Modality

A prompt is always text. An optional `image` parameter accepts a local file path or HTTP(S) URL to attach an image to the prompt. The image is base64-encoded and sent alongside the text prompt.

### Output Schema

The `output_schema` parameter forces the agent to return structured output matching the provided type. This enables converting unstructured information from an agent into structured data.

Supported schema types:
- Scalar primitives: `str`, `int`, `float`, `bool`
- Collection types: `list`, `list[T]`, `dict`, `dict[K, V]`, `tuple`, `tuple[T, ...]`
- `Enum` with string values
- `dataclass` (including nested dataclasses, self-referential structures, and arbitrary nesting depth)
- Union types (e.g. `str | int`, `MyClass | None`)

When JSON parsing fails and the schema is a scalar or enum, the raw string is interpreted directly as the value. This handles cases where the agent returns a bare string instead of a JSON-encoded one.

```python
result = await pete.invoke_agent(
    "Spell your name.",
    output_schema=list[str],
)
print(result)  # ["P", "e", "t", "e"]
```

## Thread ID and Persistence

Invocations can be transient or persistent, controlled by the `persistent_thread_id` parameter.

### Persistent Sessions

Providing a `persistent_thread_id` persists the session so you can continue a conversation across multiple invocations. This gives the agent short-term memory about the recent conversation.

```python
await pete.invoke_agent("Remember this: the answer is 42.", persistent_thread_id="my-session")
result = await pete.invoke_agent("What number did I ask you to remember?", persistent_thread_id="my-session")
print(result)  # You asked me to remember 42.
```

The `persistent_thread_id` is an arbitrary string you choose. Subsequent invocations with the same thread ID continue the same conversation.

### Transient Sessions

When no `persistent_thread_id` is provided, the conversation is anonymous and temporary. The session and runner are destroyed after the invocation completes, and every subsequent call starts with a fresh context.

```python
await pete.invoke_agent("Remember this: the answer is 42.")
result = await pete.invoke_agent("What number did I ask you to remember?")
print(result)  # I don't have any knowledge about that.
```

## Sub-Agent Invocation

Agentic objects can invoke other agentic objects' agents through tools.
Each agentic object has an invocation lock that prevents race conditions from concurrent tool calls.
**Circular invocation dependencies will deadlock** — if Agent A calls Agent B and Agent B calls Agent A, each agent acquires its own lock and then tries to acquire the other's.
Since the other's agent already holds that lock, neither can proceed.

To prevent indefinite blocking in such scenarios, pass a `timeout` to `invoke_agent`.
If the lock cannot be acquired within the timeout period, a `TimeoutError` is raised:

See the **[Circular Invocation Timeout](../examples/circular-invocation-timeout.py)** example for a complete demonstration.

Agents can invoke other agents' agents in three ways:

### `invoke_agent()` — Direct invocation

The `invoke_agent()` function is the primary way a user calls an agent. It sends a prompt to the agent, which reasons about it and interacts with its own tools.

For a complete list of arguments, see the **[AgenticObject reference](../reference/agentic-object-base.md)**.

When a user calls `invoke_agent()` on multiple agents, each agent's conversation history remains completely separate. There is no way to trace how messages between different agents interacted with each other — for example, why one particular message was prompted to an agent, or where it originated. For details on session management and context, see **[State and Persistence](./state-and-persistence.md)**.

### Indirect Invocation

An agent can also indirectly invoke another agent by holding a reference to it as a member variable. This reference can be provided to the agent through a `@sandbox`-decorated function, enabling the agent to access and manipulate other agentic objects' state directly.

When sandboxed code execution is enabled, the agent can write Python code that retrieves a reference to another agent (via a `@sandbox` method) and calls its member functions. If that member function calls `invoke_agent()` on its own agent, the second agent is invoked indirectly — the agent did not call the other agent's prompt-based communication layer directly, but rather accessed it through a member function call.

```python
@agentic_object(allow_code_execution=True)
class AgentA(AgenticObject):
    """I can access and manipulate other agents."""
    @sandbox
    def get_agent_b(self) -> AgentB:
        """Return the AgentB instance."""
        return self._agent_b
```

The agent can then write Python code that calls `self.get_agent_b()` to retrieve the reference, and pass it to another function or member function that may invoke the second agent's `invoke_agent()`.

### `invoke()` — Direct invocation

The `invoke()` method is the agent-facing way to invoke another agent directly. Unlike `invoke_agent()`, which sends a prompt to the agent's communication layer, `invoke()` prompts the target agent and has distinct thread ID behavior.

```python
from peteos import agentic_object

@agentic_object(invoke_sub_agents=True)
class Supervisor(AgenticObject):
    """You are a supervisor. Delegate tasks to specialists."""

    def __init__(self):
        super().__init__()
        self.specialist = Specialist()

result = await supervisor.invoke(
    target=supervisor.specialist,
    prompt="Analyze this data and classify it.",
    persistent=True,
)
```

The `persistent` flag controls whether the parent's thread ID is forwarded. When `persistent=True`, sub-agent calls inherit the same thread ID, allowing continuity. When `persistent=False`, the sub-agent call is transient.

Hooks are also forwarded to sub-agents via `invoke()`. See **[Invocation Hooks](./invocation-hooks.md)** for details on how hooks propagate across the invocation tree.

### Thread ID Forwarding

When an agentic object invokes sub-agents (via sandboxed code), thread IDs are forwarded. If a parent invocation has a `persistent_thread_id`, sub-agent calls inherit the same thread ID, allowing the agent to maintain continuity when delegating work to other objects or itself.

When `persistent=True`, the sub-agent inherits the parent's thread ID and the session persists on the target object. **Once `persistent=True`, the thread ID is fixed** — it cannot be changed during the sub-agent's lifetime.

```
Parent thread: "parent-tick"
  └─→ Sub-agent on Child (persistent=True) inherits thread_id="parent-tick"
  └─→ Sub-agent on Child (persistent=False) gets a fresh thread
```
