import asyncio
from peteos import AgenticObject, agentic_object, tool


@agentic_object(allow_code_execution=True)
class ErrorDemo(AgenticObject):
    """You demonstrate error handling."""

    @tool
    def break_things(self, count: int) -> int:
        """Call this to trigger an error."""
        raise RuntimeError(f"Something went wrong after {count} attempts")

    @tool
    def get_value(self, x: int) -> int:
        """Returns x * 2."""
        return x * 2


async def main():
    demo = ErrorDemo()
    try:
        result = await demo.invoke_agent(
            "Call break_things with 3."
        )
        print("Result:", result)
    except RuntimeError as e:
        print("Caught exception:", e)


if __name__ == "__main__":
    asyncio.run(main())
