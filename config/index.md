# Configuration

Peteos auto-loads configuration on `import peteos` — no manual setup required.

## Standard Configuration Flow

### Discovery Locations

`peteos.json` is searched in this order (first match wins):

1. **`PETEOS_CONFIG`** environment variable (full path — always takes precedence)
2. **`./peteos.json`** (current working directory — project-local)
3. **`$XDG_CONFIG_HOME/peteos/peteos.json`** (defaults to `~/.config/peteos/peteos.json` — user-specific)
4. **`/etc/peteos/peteos.json`** (system-wide — last resort)

### Directory Layout

When `peteos.json` is loaded, its parent directory becomes the config root. Two sibling subdirectories are auto-discovered:

| Directory | Purpose |
|---|---|
| `roles/` | Persistent role overrides, loaded automatically via `RoleManager.load_from_dir()` |
| `agents/` | Agent base directory, set as `Agent.agent_base` |

Both directories are optional. If they don't exist, Peteos continues without them.

#### Example Layout

```
my-project/
├── peteos.json
├── agents/                    # Agent base directory (auto-created if needed)
│   └── MyRole/                # Per-role runtime directory (created by Agent)
└── roles/
    └── MyRole/
        ├── description.md     # Required
        ├── system_prompt.md   # Optional
        └── config.json        # Optional
```

### Config File Format

```json
{
    "backends": [
        {
            "name": "local",
            "url": "http://localhost:3001"
        },
        {
            "name": "anthropic",
            "url": "https://api.anthropic.com",
            "api_type": "anthropic"
        }
    ]
}
```

The `backends` array configures LLM endpoints. Roles and agents are loaded from the sibling directories automatically — no manual registration needed.

## Reference

| Page | Description |
|---|---|
| [Backends](./backends.md) | Automatic backend configuration and manual API registration |
| [Roles](./roles.md) | Role structure, config.json fields, manual registration |
