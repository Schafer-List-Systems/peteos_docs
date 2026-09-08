# Getting Started

Welcome to PeteOS, an agentic application framework that lets you build self‑aware Python objects (**agentic objects**) by combining object‑oriented programming with AI agents.

This section covers the essentials to get you up and running.
First, you will learn how to install PeteOS into your project.
Then, you will configure the LLM backend via `peteos.json`.
Finally, you will see how to set up an agentic object and use it.


## Installation

Create a Python virtual environment and activate it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Either install via PyPI:

```bash
pip install peteos
```

Or clone the repository, then install PeteOS:

```bash
git clone https://github.com/yourusername/peteos.git
cd peteos
pip install .
```

This installs PeteOS as a package so you can `import peteos` from your own code.

### Verifying the Installation

Run the unit tests to confirm everything works:

```bash
python -m pytest tests/unit/ -v
```

This tests the core framework without requiring an LLM backend.


## Configuring the LLM Provider

PeteOS loads its configuration automatically on import from a `peteos.json` file.
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

If everything is set up correctly, the example below will connect to your configured backend and produce a response from the agent.

---

## Hello World

An agentic class is a class that derives from `AgenticObject`.
Behind the scenes, an agent operates on the object.
The class docstring serves as the agent's system prompt.

```python
from peteos import AgenticObject

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
Output schemas can be primitives (`str`, `int`, `float`, `bool`), `list`, `dict`, `Enum`, or `dataclass`, and can be nested arbitrarily (e.g., `list[dataclass]`, `dict[str, list[int]]`).

### Object Interaction

Agentic objects maintain their own state and reason about it. The agent reads and modifies the object using tools:

```python
class Item(Enum):
    TOWEL = "Towel"
    BABEL_FISH = "Babel Fish"
    PAN_GALACTIC_GARGLE_BLASTER = "Pan Galactic Gargle Blaster"
    IMPROBABILITY_DRIVE = "Improbability Drive"

class GroceryList(AgenticObject):
    """You manage a grocery list."""

    def __init__(self):
        super().__init__()
        self._items: dict[Item, int] = {}

    @tool
    def list_items(self) -> list[tuple[str, int]]:
        """Return the current grocery list with quantities."""
        return [
            (item.value, qty)
            for item, qty in self._items.items()
        ]

    @tool
    def add_item(self, item: Item, quantity: int) -> str:
        """Add items to the grocery list."""
        self._items[item] = self._items.get(item, 0) + quantity
        return f"Added {quantity} {item.value}s."
```

The agent reasons about prompts and calls tools to interact with the object's state:

```python
groceries = GroceryList()
await groceries.invoke_agent("Add a towel to the list.")
await groceries.invoke_agent("Add a towel and 3 babel fish to the list.")
await groceries.invoke_agent("What is on my grocery list?")
# [("Towel", 2), ("Babel Fish", 3)]
```

The first invocation calls `add_item` once for a towel.
The second invocation calls `add_item` twice: once for another towel and once for three babel fish, resulting in two towels and three babel fish total.
The final invocation calls `list_items` to retrieve the current list.
**Note:** Trying to add "panic" to the list would fail because it isn’t a member of the `Item` enum; the type system blocks invalid values, guiding the agent.

The docstring of a tool is the description the agent sees when deciding which tool to call.
Providing detailed descriptions — including what the arguments represent — helps the agent call tools correctly on the first try.
Returning a value makes the result visible to the agent; if the function returns `None`, no result is communicated.

### Sandboxed Code Execution

Enable the agent to run Python code by decorating the class with `@agentic_object(allow_code_execution=True)`.
Inside the Python function, `self` refers to the agentic object — the agent can call its `@tool` and `@sandbox` methods as member functions.

```python
@agentic_object(allow_code_execution=True)
class WeightCalculator(AgenticObject):
    """You prefer python to solve problems."""
    
    def __init__(self):
        super().__init__()
        self._items = {
            "apple": 0.1,
            "banana": 0.15,
            "orange": 0.2,
            "watermelon": 2.5,
            "pineapple": 1.2
        }
    
    @tool
    def get_items(self) -> list[str]:
        """Return a list of all item names."""
        return list(self._items.keys())
    
    @sandbox
    def get_item_weight(self, item_name: str) -> float:
        """Return the weight of a specific item by name."""
        return self._items.get(item_name, 0.0)
```

`@sandbox` methods are only callable from within sandboxed Python code (via `self.method()`), not as direct agent tool calls.
The agent uses Python to iterate over the items, retrieve weights, and compute statistics, improving reasoning performance and reliability.

```python
calc = WeightCalculator()
result = await calc.invoke_agent(
    "Calculate the average and standard deviation of the weights of all items.",
    output_schema=tuple[float, float],
)
print(result)  # (0.83, 0.93)
```

### Where to Go Next

- See the **[Concepts](./concepts/index.md)** section to understand how agentic objects work under the hood
- See the **[Best Practices](./best-practices/index.md)** section for proven patterns
- Browse the **[Examples](./examples/)** directory for runnable code — from a basic agentic object to sandboxed execution, adaptive objects with persistent sessions, and more
- Look at the **[pre-built agentic objects](./reference/agentic-objects/)** for ready-to-use agentic classes, including [BashWorkspace](./reference/agentic-objects/bash-workspace.md) and [PdfTranscriber](./reference/agentic-objects/pdf-transcriber.md)
