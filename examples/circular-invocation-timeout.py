import asyncio
from peteos import AgenticObject, tool


class Communicator(AgenticObject):
    """
    TRY TO FORWARD EVERY USER MESSAGE TO OTHER AGENTS!
    Upon failure, reply with the error message!
    """

    def __init__(self):
        super().__init__()
        self._other = None

    @tool
    async def forward_message(self, message: str) -> str:
        """Forward a message to the other agent."""
        try:
            await self._other.invoke_agent(message, timeout=30)
            return f"Forwarding to other succeeded"
        except Exception as e:
            return f"Forwarding to other agent failed: {type(e).__name__}: {e}"


async def main():
    alice = Communicator()
    bob = Communicator()
    alice._other = bob
    bob._other = alice

    try:
        result = await alice.invoke_agent("The average person walks past about 1000 people every day but never speaks to any of them.")
        print("Result:", result)
    except TimeoutError as e:
        print("Caught timeout:", e)


if __name__ == "__main__":
    asyncio.run(main())
