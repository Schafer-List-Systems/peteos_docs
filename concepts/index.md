# Concepts

Deep dives into the core ideas behind sOAP: how agentic objects are composed, invoked, and persisted.

## Basic

| Topic | Description |
|---|---|
| [Invocation](./invocation.md) | `invoke_agent()`, `invoke()`, output schemas, thread IDs, sub-agents |
| [Error Handling](./error-handling.md) | `Error` objects vs exceptions — when each arises and what they mean |
| [Steering the Agent](./steering.md) | Tool return values and queued messages — two ways to guide the agent mid-invocation |
| [Media Handling](./media.md) | Attaching images, video, and PDFs to prompts; agent-initiated media access |
| [Composition](./composition.md) | Multi-inheritance, MRO-based system prompts, config merging across agentic parents |

## Advanced

| Topic | Description |
|---|---|
| [Invocation Hooks](./invocation-hooks.md) | Observing, controlling, and measuring agent invocations |
| [Agentic Object Roles](./agentic-object-roles.md) | Role naming, canonical role building, user overrides, model selection |
| [State and Persistence](./state-and-persistence.md) | Internal state, session serialization, context forking, token counting, compaction |
| [Adaptive Objects](./adaptive-objects.md) | Objects that manipulate and extend their own code at runtime across class, instance, and session levels |
