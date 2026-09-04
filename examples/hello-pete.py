import asyncio
from peteos import AgenticObject


class HelloPete(AgenticObject):
    """You are Pete, a helpful assistant."""


async def main():
    pete = HelloPete()
    result = await pete.invoke_agent("Hello, what's your name?")
    print(result)


asyncio.run(main())
