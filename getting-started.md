# Getting Started

Welcome to Peteos.
This section covers the essentials to get you up and running.
First, you will learn how to install Peteos into your project.
Then, you will configure the LLM backend via `peteos.json`.
Finally, you will see how to set up an agentic object and use it.


## Installation

Create a Python virtual environment and activate it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Either install via pip:

```bash
pip install peteos
```

Or clone the repository, then install Peteos:

```bash
git clone https://github.com/yourusername/peteos.git
cd peteos
pip install .
```

This installs Peteos as a package so you can `import peteos` from your own code.

```bash
pip install -e ".[camera,web,dev]"
```

The `-e` flag installs Peteos in editable (development) mode, so changes to the source are reflected immediately without needing to reinstall.

### Verifying the Installation

Run the unit tests to confirm everything works:

```bash
python -m pytest tests/unit/ -v
```

This tests the core framework without requiring an LLM backend.


## Configuring the LLM Provider

Peteos loads its configuration automatically on import from a `peteos.json` file.
Copy the example file to get started:

```bash
cp peteos.json.example peteos.json
```

A minimal configuration for a local Ollama instance looks like this:

```json
{
  "backends": [
    {
      "name": "ollama",
      "url": "http://localhost:11434",
      "model_priorities": {
        "glm-4.7-flash:latest": 100
      },
      "max_output": 16384
    }
  ]
}
```

Each backend in the `backends` array defines an LLM provider with options such as the API URL, type (`openai`, `anthropic`, `gemini`), API key, model priorities, streaming mode, and retry behaviour.
For a complete list of backend options and how configuration is discovered across the filesystem, see the **[Configuration](./config/index.md)** and **[Backends](./config/backends.md)** reference pages.

To verify that your configuration works, run the hello-pete example:

```bash
python3 examples/00_hello_pete.py
```

If everything is set up correctly, the example will connect to your configured backend and produce a response from the agent.

---

## Hello World

An agentic class is a class that derives from `AgenticObject`.
Behind the scenes, an agent operates on the object.
The class docstring serves as the agent's system prompt.

```python
class HelloPete(AgenticObject):
    """You are Pete, a helpful assistant."""
```

That is all it takes to create an agentic class.
Invoke it directly:

```python
pete = HelloPete()
result = await pete.invoke_agent("Hello, what's your name?")
print(result)  # My name is Pete.
```

The agent reasons about your prompt and responds directly.
This is the simplest way to use an agentic object: create the instance, invoke the agent, get a response.

### Structured Output

You can force structured output by passing an `output_schema`:

```python
result = await pete.invoke_agent(
    prompt="What is your name and your most significant character trait?",
    output_schema=dict[str, str],
)
print(result)  # {"name": "Pete", "character": "helpful"}
```

The `output_schema` parameter tells the agent to return structured output.
No additional prompt engineering is needed — the agent adapts to the schema.
Output schemas can be primitives (`str`, `int`, `float`, `bool`), `list`, `dict`, `Enum`, or `dataclass`.

### Object Interaction

Agentic objects maintain their own state and reason about it. The agent reads and modifies the object using tools:

```python
_PRICES = {
    "Milk": 1.50,
    "Bread": 2.00,
    "Egg": 0.25,
    "Butter": 3.00,
}

class Grocery(Enum):
    MILK = "Milk"
    BREAD = "Bread"
    EGG = "Egg"
    BUTTER = "Butter"

class GroceryList(AgenticObject):
    """You manage a grocery list. Read the current list with list_items,
    add items with add_item, and clear the list with clear."""

    def __init__(self):
        super().__init__()
        self._items: dict[Grocery, int] = {}

    @tool
    def list_items(self) -> list[tuple[str, float, int]]:
        """Return the current grocery list with prices."""
        return [
            (item.value, _PRICES[item.value], qty)
            for item, qty in self._items.items()
        ]

    @tool
    def add_item(self, item: Grocery, quantity: int) -> str:
        """Add items to the grocery list."""
        self._items[item] = self._items.get(item, 0) + quantity
        return f"Added {quantity} {item.value}s."

    @tool
    def clear(self) -> str:
        """Clear the grocery list."""
        self._items.clear()
        return "List cleared."
```

The agent reasons about prompts and calls tools to interact with the object's state:

```python
groceries = GroceryList()
await groceries.invoke_agent("Add 2 milk and 3 eggs to the list.")
await groceries.invoke_agent("How much will my shopping cost?")
# 1.50 * 2 + 0.25 * 3 = 3.75
```

The docstring of a tool is the description the agent sees when deciding which tool to call.
Providing detailed descriptions — including what the arguments represent — helps the agent call tools correctly on the first try.
Returning a value makes the result visible to the agent; if the function returns `None`, no result is communicated.

### Sandboxed Code Execution

Enable the agent to run Python code in a restricted sandbox by decorating the class with `@agentic_object(allow_code_execution=True)`.
This enables a hidden tool called `python_exec` that the agent can call.
Code executed in the sandbox can access the agentic object through the `self` parameter:

```python
@agentic_object(allow_code_execution=True)
class FibonacciSquared(AgenticObject):
    """You are a helpful assistant."""
```

```python
seq = FibonacciSquared()
result = await seq.invoke_agent(
    f"Compute the sequence where each element is the sum of the squares of its two predecessors."
    f" Start with 0, 1. And compute the 10-th element.",
    output_schema=int,
)
print(result)
```

The sandbox provides pure functions and builtins but blocks file I/O, network access, and dangerous operations.

The `@agentic_object` decorator offers additional options such as `imports` to add modules to the sandbox, and `import_aliases` for module aliases. Providing more imports adds functionality but also increases the attack surface.

Beyond single objects, agentic systems can compose into hierarchies of agents and sub-agents for more complex tasks. Within the sandbox, the Python code can access the agentic object directly as if it were a member function. See the **[Decorator Arguments reference](./reference/decorator-args.md)** for details.

### Where to Go Next

- See the **[Concepts](./concepts/index.md)** section to understand how agentic objects work under the hood
- See the **[Best Practices](./best-practices/index.md)** section for proven patterns
- Browse the **[Examples](./examples/)** directory for runnable code — from a basic agentic object to sandboxed execution, adaptive objects with persistent sessions, and more
- Look at the **[pre-built agentic objects](./reference/agentic-objects/)** for ready-to-use agentic classes, including [BashWorkspace](./reference/agentic-objects/bash-workspace.md) and [PdfTranscriber](./reference/agentic-objects/pdf-transcriber.md)
