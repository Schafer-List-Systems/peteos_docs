import asyncio
import random
from peteos import AgenticObject, agentic_object, tool
from peteos.oap.decorators import sandbox


@agentic_object(allow_code_execution=True)
class TravelingOptimizer(AgenticObject):
    """You manage trips. Each destination is a point in a 2D-coordinate system."""

    def __init__(self, destinations: dict[str, tuple[float, float]]):
        super().__init__()
        self._destinations = destinations

    @tool
    def list_destinations(self) -> list[str]:
        """List the desired destinations."""
        return list(self._destinations.keys())

    @sandbox
    def get_coordinates(self, destination: str) -> tuple[float, float] | None:
        """Get the coordinates of a destination."""
        return self._destinations.get(destination)


async def main():
    # Initialize random seed for reproducible results
    random.seed(42)
    # Create destinations dictionary with letters A-F and random X, Y coordinates
    destinations: dict[str, tuple[float, float]] = {
        letter: (random.uniform(-100, 100), random.uniform(-100, 100))
        for letter in [chr(i) for i in range(ord('A'), ord('F')+1)]
    }
    optimizer = TravelingOptimizer(destinations)
    result = await optimizer.invoke_agent(
        "What is the shortest path when traveling from A to F while visiting every destination?",
        output_schema=tuple[list[str], float]
    )
    print("Shortest path:", result)
    # Shortest path: (['A', 'D', 'C', 'E', 'B', 'F'], 424.02311606335303)


if __name__ == "__main__":
    asyncio.run(main())
