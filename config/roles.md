# Roles

You can customize any agentic object's role from the outside without changing the class code. This is useful for steering the agent toward a specific model — for example, applying an expensive model where it is needed and a cheaper one elsewhere. Roles are registered manually or loaded from disk.

## Manual Registration

```python
from peteos.persona.role import Role
from peteos.persona.rolemanager import RoleManager

RoleManager.register_role(Role(
    name="oap_MyAgent",
    model="gpt-4",
    description="A customized agent",
))
```

The role name must match the canonical role name of the agentic object class it targets. Use `@agentic_object(role="...")` to set a custom name on your class.

## Loading from Disk

Instead of registering a transient role manually, a persistent role can be loaded from disk:

```python
loaded = RoleManager.load_from_dir("/path/to/roles/")
```

Each subdirectory represents a role:

```
oap_MyAgent/
  description.md          # Required
  system_prompt.md        # Optional
  config.json             # Optional
```

The `config.json` format:

```json
{
    "model": "gpt-4",
    "required_tools": ["read_file"],
    "auto_approve_tools": ["read_file"],
    "tool_filter": ["read_.*"],
    "execution_environment": "REPL",
    "behavior_policy": "responsive",
    "max_truncation_retries": 2,
    "max_output_turns": 3,
    "max_output_attempts": 3
}
```

| Field | Type | Default | Purpose |
|---|---|---|---|
| `description` | string | from `description.md` | Role description. Only used if no `description.md` exists. |
| `system_prompt` | string | from `system_prompt.md` | System prompt text. Only used if no `system_prompt.md` exists. |
| `required_tools` | string[] | `[]` | Tool names available to this role. |
| `execution_environment` | string | `"REPL"` | Execution environment identifier. |
| `model` | string | `".*"` | Regex matching allowed model IDs. |
| `auto_approve_tools` | string[] | `[]` | Tool names auto-approved without user confirmation. |
| `tool_filter` | string[] | `[]` | Regex patterns; only matching tools are visible to the role. |
| `behavior_policy` | string | `"responsive"` | `"responsive"` yields on output; `"continuous"` loops until `yield_back`. |
| `max_truncation_retries` | int | `2` | Max retries for token-window truncation. |
| `max_output_turns` | int | `3` | Max output-producing turns per `invoke_agent` call. |
| `max_output_attempts` | int | `3` | Max `produce_output` attempts per output turn. |

Markdown files take precedence over `config.json` entries. Returns a list of successfully loaded role names.
