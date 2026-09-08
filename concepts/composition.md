# Composition

Agentic objects, built from [`AgenticObject`](../reference/agentic-object-base.md) and configured with [`@agentic_object`](../reference/decorator-args.md), can be composed through multi-inheritance to build more complex behavior from simpler building blocks.

For a concrete and full example have a look at our NPC exploring a Dungeon in [`examples/adventure-dungeon.py`](../examples/adventure-dungeon.py). 

## Base Agentic Class

The simplest agentic class derives directly from [`AgenticObject`](../reference/agentic-object-base.md):

```python
class SimpleAssistant(AgenticObject):
    """You are a helpful assistant."""
```

This is all it takes to create an agentic class.
Behind the scenes, an agent operates on the object.

## Composition and Specialization

Agentic objects can be combined or extended using Python's inheritance. There are two primary patterns:

### Composition — Multi-Inheritance

Use multi-inheritance to combine the capabilities of multiple simpler, atomic agents into one. This is like building from Lego blocks:

```python
class ComplexAgent(Calculator, DBTool, TextWriter, AgenticObject):
    """You are a composed agent with capabilities A, B, and C."""
```

Each parent class contributes its `@tool`-decorated methods. The final class must derive from `AgenticObject`. Tools are collected from all classes in the MRO, regardless of whether those parent classes are agentic objects themselves.

### Specialization — Single Inheritance

Use single inheritance to extend or refine an existing agent.
The specialized class inherits the parent's tools and behavior, allowing you to add capabilities or impose more rules in the system prompt.
Here's an example where a parent tool is overridden with a simpler signature:

```python
class BaseAgent(AgenticObject):
    """You are a base agent."""

    @tool
    def calculate(self, x: int, y: int) -> int:
        """Calculate the sum of two numbers."""
        return x + y

class AdditionAgent(BaseAgent, AgenticObject):
    """You always add numbers to 10."""

    @tool
    def calculate(self, x: int) -> int:
        """Add x to 10."""
        return super().calculate(x, 10)
```

`AdditionAgent` inherits `calculate` but provides a more constrained version. More on how the system prompt is constructed in the next section.

## System Prompt Construction

When composing multiple agentic classes, the agent's system prompt is built by concatenating the docstrings of each agentic parent class in the Method Resolution Order (MRO).
The most basic class's docstring (typically `AgenticObject`) comes first, and classes appearing later in the inheritance line are appended later in the combined prompt.

In a diamond inheritance pattern (where a class appears multiple times in the inheritance graph), Python's MRO ensures each class is visited exactly once. The docstring is collected only once and no duplication occurs.

For example, `AdditionAgent(BaseAgent, AgenticObject)` produces a system prompt that contains both base class docstrings:

```
Calculate the sum of two numbers.
You always add numbers to 10.
```

## Config Merging

Configuration from decorated agentic parents (set via the [`@agentic_object` decorator](../reference/decorator-args.md)) is also merged across the inheritance hierarchy:

- `imports` are unioned across all parents.
- `import_aliases` are merged, with later classes' aliases taking precedence.
- Boolean flags like `allow_code_execution` and `allow_media_access` are combined with a logical OR — if any parent enables the flag, the composed agent has it enabled.

`role`, however, is not merged. Only the most-derived decorated class's `role` value is used.

This means composed agentic objects inherit both their behavior and their configuration from all parents.
