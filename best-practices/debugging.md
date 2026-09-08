# Debugging

Test agentic objects in two layers: deterministic tests first, non-deterministic tests second. This gives fast, reliable feedback while the agent system is being built up.

## Why

Non-deterministic behavior makes testing harder — a single failure may just be a bad agent turn, not a broken implementation. By testing deterministic code first, you verify the foundation. When non-deterministic tests fail, you know exactly which layer is at fault.

## How

### Deterministic Tests

Test every method that does neither directly nor indirectly call `invoke_agent`. These are standard unit tests — fast, deterministic, and easy to debug.

```python
def test_add_item():
    store = Inventory()
    result = store.add_item("laptop", 2)
    assert result == "Added 2 laptops."
    assert store.get_inventory() == [("laptop", 2)]
```

If a method modifies state or performs calculations, test both the return value and the resulting state.

```python
def test_set_price_updates_value():
    item = Product("widget", price=10.0)
    item.set_price(15.0)
    assert item.current_price == 15.0
```

### Agentic Tests

Test the agent's behavior with `invoke_agent()`, accepting that results may vary between runs. These are simple tests like the deterministic tests above, but they can fail or pass depending on the agent's output.

```python
async def test_summarize_sentiment():
    analyzer = SentimentAnalyzer()
    analyzer._documents = ["Great product!", "Terrible service."]
    result = await analyzer.invoke_agent(
        "Summarize the overall sentiment.",
        output_schema=Summary,
    )
    assert isinstance(result, Summary)
    assert result.text
```

Because agent outputs are non-deterministic, individual runs may fail even when the code is correct. To evaluate whether an agent works reliably, run the tests multiple times and check the acceptance rate — a Monte Carlo approach. If the agent passes 8 out of 10 runs, the success rate is 80%, which may be sufficient depending on the use case.

### Debugging

Since agentic object code is standard Python, you can debug it with a Python debugger. Set **breakpoints** in your `@tool` or `@sandbox` decorated functions, and when the agent calls them, the debugger will stop so you can inspect the state. This gives you a much better way to diagnose the runtime of your agentic system compared to cloud-based, graph-based, no-code tools that offer no such visibility. You can debug your agent code exactly the same way you debug any other Python source code.

## Key Principles

- **Test deterministic methods directly.** Every method that does not call `invoke_agent` should have a deterministic unit test.
- **Test agent invocations separately.** Use `invoke_agent()` only in the second layer.
- **Expect variability.** Agent tests can pass or fail on different runs — this is normal.
- **Use Monte Carlo for evaluation.** Loop agent tests multiple times to measure acceptance rates.
- **Build up gradually.** Verify the deterministic foundation before adding agent layers.
