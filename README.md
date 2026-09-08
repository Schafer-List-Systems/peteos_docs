# Peteos Documentation

Peteos is a library for developing agentic software, built on **Simple Object-Agentic Programming (sOAP)** — a paradigm that marries object-oriented programming with AI agents. Agentic objects are objects that can think, decide, and interact with their environment on their own.

Object-agentic programming lets you write normal Python classes and expose their parts to an AI agent. Mark methods with `@tool`, call `invoke_agent()`, and the agent reasons about which tools to use to fulfill your task.

## Getting Started

| Page | Description                                                                                      |
|---|--------------------------------------------------------------------------------------------------|
| [Introduction](./introduction.md) | A brief introduction to the sOAP paradigm |
| [sOAP](./soap.md) | The sOAP philosophy, core principles, and mental model for agentic objects |
| [Getting Started](./getting-started.md) | Installation, LLM backend setup, and your first agentic objects                                  |

## Learn

| Page | Description |
|---|---|
| [Concepts](./concepts/index.md) | Deep dives: composition, invocation, state and persistence, media handling |
| [Best Practices](./best-practices/index.md) | Proven patterns: guardrails, unit testing — how to build reliable agentic systems |
| [Examples](./examples/) | Runnable code: hello pete, grocery list, stock portfolio analyzer, and more |

## Reference

| Page | Description |
|---|---|
| [API Index](./reference/index.md) | All classes, decorators, and configuration documented by name |

## Advanced

| Page | Description |
|---|---|
| [Advanced Index](./advanced/index.md) | Internal classes and concepts for debugging, extending, and building on top of Peteos |
