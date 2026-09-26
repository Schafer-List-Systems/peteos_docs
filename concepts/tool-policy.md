# Tool Policy

A `tool_policy()` nested inside a `@tool` method lets you define when a specific tool call is safe — based on the actual arguments the agent passed. The decision lives directly next to the tool definition, where you know the tool best.

## The concept

Different tools have different ideas of what makes a call safe. A shell executor needs to check the command. A file reader needs to check the path. A search tool needs to check the query. Before this feature, there was no way to express those rules right at the tool definition. You had to reach outside into an external hook or configuration.

With `tool_policy()` the policy lives with the tool. The tool defines the arguments it accepts, and the policy checks them.

## How to write one

A `tool_policy()` is a parameterless nested function inside a `@tool` method. It reads the method's parameters directly from its enclosing scope:

```python
@tool
def file_read(self, path: str, runner=None):
    def tool_policy():
        return not path.startswith("/home/user/.ssh")

    return self._read(path, runner=runner)
```

The policy sees `path` because PeteOS pre-populates the closure cells from the tool-call arguments before calling the policy. The policy can also read `self` to access instance state:

```python
@tool
def bash_exec(self, command: str, timeout: int = 30):
    def tool_policy():
        safe_commands = {"ls", "pwd", "find", "grep", "cat", "head", "tail"}
        return command.split()[0] in safe_commands

    return self._bash(command, timeout=timeout)
```

## What the policy returns

| Return | Effect |
|---|---|
| `True` | You say: this call is safe — approve it |
| `False` | You say: this call is dangerous — deny it |
| `None` | You have no opinion — let the rest of the system decide |

This is the key strength: you only weigh in when you have something to say. If a call is not clearly dangerous, return `None` and let other policies or hooks in the chain have their say. If a call is clearly off-limits, return `False` and it is denied immediately. If you are certain it is safe, return `True`.

## Denials are final

When a policy returns `False`, that decision is made immediately. The policy loop stops there. This is by design — a clear denial from someone who knows the tool should not be overridden by a less-informed party.

## One policy per tool

The policy belongs to the class that defines the tool. If a subclass overrides the tool, its policy replaces the parent's. Python's method resolution order guarantees each tool has exactly one policy owner.

## Example: path guard

```python
@tool
def file_read(self, path: str, runner=None):
    def tool_policy():
        if path.startswith("/home/user/.ssh"):
            return False  # definitely denied
        if path.startswith("/public/"):
            return True   # definitely safe
        return None      # no opinion — let others decide

    return self._read(path, runner=runner)
```

## Example: command allowlist

```python
@tool
def bash_exec(self, command: str, timeout: int = 30):
    def tool_policy():
        blocked = {"rm", "curl", "wget", "nc", "bash"}
        if command.split()[0] in blocked:
            return False  # definitely denied
        return None      # no opinion on the rest

    return self._bash(command, timeout=timeout)
```
