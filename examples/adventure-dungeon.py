import random
from enum import Enum
import asyncio

from peteos import AgenticObject, agentic_object, sandbox, tool


class Direction(Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"


class Map:
    """A dungeon map with randomly placed items."""

    def __init__(self, num_food: int = 20, num_treasure: int = 3, num_monsters: int = 8):
        random.seed(42)
        self._grid: list[list[tuple[str, float] | None]] = [[None] * 10 for _ in range(10)]

        items = (
            [("food", random.uniform(0.5, 2.0)) for _ in range(num_food)]
            + [("treasure", random.uniform(1.0, 5.0)) for _ in range(num_treasure)]
            + [("monster", random.uniform(1.0, 3.0)) for _ in range(num_monsters)]
        )
        for item_type, weight in items:
            while True:
                x, y = random.randint(0, 9), random.randint(0, 9)
                if self._grid[x][y] is None:
                    self._grid[x][y] = (item_type, weight)
                    break

    def print_map(self, x: int = None, y: int = None) -> None:
        """Print the dungeon map with NPC highlighted."""
        # Header
        print("".join(f"{col:>4}" for col in range(10)))
        for row in range(10):
            row_str = f"{row}  "
            for col in range(10):
                if col == x and row == y:
                    row_str += "🧙  "
                else:
                    cell = self._grid[col][row]
                    if cell is None:
                        row_str += "··  "
                    elif cell[0] == "monster":
                        row_str += "🧟  "
                    elif cell[0] == "treasure":
                        row_str += "🏆  "
                    elif cell[0] == "food":
                        row_str += "🍖  "
            print(row_str)

    def get_item(self, x: int, y: int) -> tuple[str, float] | None:
        """Return item at position if one exists."""
        return self._grid[x][y]

    def remove_item(self, x: int, y: int) -> tuple[str, float] | None:
        """Remove and return item at position."""
        item = self._grid[x][y]
        self._grid[x][y] = None
        return item

    def count_monsters(self) -> int:
        """Return the number of monsters remaining on the map."""
        return sum(1 for row in self._grid for cell in row if cell and cell[0] == "monster")

    def roaring_volume(self, x: int, y: int) -> float:
        """Return a volume level (0.0-1.0) based on proximity to nearest monster. 1.0=adjacent, 0.0=far."""
        min_dist = float('inf')
        for rx in range(10):
            for ry in range(10):
                cell = self._grid[rx][ry]
                if cell and cell[0] == "monster":
                    dist = ((rx - x)**2 + (ry - y)**2)**0.5
                    if dist < min_dist:
                        min_dist = dist
        if min_dist == float('inf'):
            return 0.0
        if min_dist == 0:
            return 1.0
        return max(0.0, 1.0 - min_dist / 10.0)


class GameOverError(Exception):
    """Raised when the NPC dies."""


@agentic_object(allow_code_execution=True)
class Navigator(AgenticObject):
    """You are the navigation specialist of this NPC. You understand
    maps, positions, and movement. Use move(north/south/east/west) to travel.
    Valid range is 0-9 in both directions."""

    def __init__(self):
        super().__init__()
        self._position: tuple[int, int] = (0, 0)

    @tool
    def move(self, direction: str) -> tuple[float, bool]:
        """Move one step in the given direction. Returns (distance traveled, wall_hit)."""
        dx, dy = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}[direction]
        original_x = self._position[0]
        original_y = self._position[1]
        new_x = min(9, max(0, self._position[0] + dx))
        new_y = min(9, max(0, self._position[1] + dy))
        hit_wall = new_x != original_x + dx or new_y != original_y + dy
        distance = ((new_x - self._position[0])**2 + (new_y - self._position[1])**2)**0.5
        self._position = (new_x, new_y)
        return distance, hit_wall


@agentic_object(allow_code_execution=True)
class InventoryManager(AgenticObject):
    """You are the inventory specialist of this NPC. You understand
    what items are available and how they can be used."""

    def __init__(self):
        super().__init__()
        self._items: dict[str, float] = {}

    @tool
    def get_inventory(self) -> dict[str, float]:
        """Return the current list of held items and their weights."""
        return self._items

    @tool
    def add_item(self, item: str, weight: float) -> str:
        """Add an item to the inventory."""
        if weight < 0:
            raise ValueError("Weight must be positive. Use use_item to decrease weight.")
        self._items[item] = self._items.get(item, 0) + weight
        return f"Picked up: {item}. Now having {self._items[item]:.1f}kg."

    @tool
    def use_item(self, item: str, weight: float) -> float:
        """Remove weight from an item. Returns how much was actually obtained."""
        available = self._items.get(item, 0)
        actual = min(weight, available)
        self._items[item] = max(0, available - actual)
        if self._items[item] == 0:
            del self._items[item]
        return actual

    @sandbox
    def get_total_weight(self) -> float:
        """Return the total weight of all items in the inventory."""
        return sum(self._items.values())


@agentic_object(allow_code_execution=True)
class NPC(Map, Navigator, InventoryManager, AgenticObject):
    """You are an adventurer navigating a dungeon. You can explore
    rooms, pick up items, and decide where to go next.

    Game rules:
    - Move using move(north/south/east/west) to explore. The dungeon is 10x10 (0-9).
    - When you arrive at a position, you see what's there: food, treasure, or a monster.
    - Use pickup_item(item_name) to pick up food or treasure. It adds to your inventory.
    - Monsters must be fought, not picked up.
    - Fighting a monster: roll a dice. Your chance to win = min(0.95, 0.3 + health*0.4 + total_weight*0.05).
      Winning grants a large treasure (5-15kg). Losing costs 0.1-0.3 health.
    - Use eat(item, amount) to consume food and restore health (max 1.0). Each kg of food restores 1.0 health and reduces hunger by 2.0.
    - A roaring sound grows louder as you approach monsters (volume 0.0=far, 1.0=adjacent). Use it to find or avoid them.
    - Hunger formula: hunger += distance*0.1 * ((2 - health) + total_weight*0.1).
    - After each move, health -= distance*0.1*hunger*0.01. If health <= 0, you die (game over).
    - Always provide a short reason when moving to explain your decision (e.g., "following roar to monster", "searching for food").
    - Your goal is to beat all monsters! You win when all monsters are defeated. Use your senses to find or avoid them!
    - When you quit but you hear still monsters roar, you lose!
    """

    def __init__(self):
        Map.__init__(self)
        Navigator.__init__(self)
        InventoryManager.__init__(self)
        self._hunger = 0
        self._health = 1.0

    @tool
    def move(self, direction: str, reason: str) -> dict:
        """Move one step in the given direction. Returns status dictionary with position info."""
        distance, hit_wall = super().move(direction)
        self._hunger += distance * 0.1 * ((2 - self._health) + self.get_total_weight() * 0.1)
        total_weight = self.get_total_weight()
        self._health -= distance * self._hunger * 0.01
        self._health = max(0.0, self._health)
        if self._health <= 0:
            raise GameOverError("NPC has died. Game over.")
        x, y = self._position
        item = self._grid[x][y]
        description = None
        if item:
            if item[0] == "monster":
                description = f"You see a monster at ({x}, {y})."
            elif item[0] == "food":
                description = f"You see food at ({x}, {y})."
            elif item[0] == "treasure":
                description = f"You see treasure at ({x}, {y})."
        roaring = self.roaring_volume(x, y)
        return {
            "distance": distance,
            "hit_wall": hit_wall,
            "item": description,
            "hunger": self._hunger,
            "health": self._health,
            "total_weight": total_weight,
            "roaring_volume": roaring,
            "monsters_left": self.count_monsters(),
        }

    @tool
    def pickup_item(self, item_name: str) -> str:
        """Pick up an item at the current position. Only works for food and treasure."""
        x, y = self._position
        item = self._grid[x][y]
        if item is None:
            return f"No item at your current position."
        if item[0] != item_name:
            return f"There is '{item[0]}' at your position, not '{item_name}'."
        if item[0] == "monster":
            return f"You cannot pick up a monster. You must fight it."
        self._grid[x][y] = None
        weight_added = item[1]
        self.add_item(item[0], weight_added)
        return f"Picked up {item_name} (weight: {weight_added:.1f}kg) from position ({x}, {y})."

    @tool
    def fight_monster(self) -> str:
        """Fight the monster at your current position. Win chance depends on health and inventory."""
        x, y = self._position
        item = self._grid[x][y]
        if item is None:
            return f"No monster at your current position."
        if item[0] != "monster":
            return f"There is '{item[0]}' at your position, not a monster."
        
        # Win chance based on health and inventory
        inventory_weight = self.get_total_weight()
        win_chance = 0.3 + self._health * 0.4 + inventory_weight * 0.05
        win_chance = min(0.95, win_chance)
        
        won = random.random() < win_chance
        
        # Remove the monster from the map
        self._grid[x][y] = None
        
        if won:
            # Large treasure reward
            reward = random.uniform(2.5, 7.5)
            self.add_item("treasure", reward)
            result_msg = f"You defeated the monster! Found treasure worth {reward:.1f}kg."
        else:
            # Lose health
            damage = random.uniform(0.1, 0.3)
            self._health = max(0.0, self._health - damage)
            result_msg = f"You were defeated by the monster. Health decreased by {damage:.1f} to {self._health:.1f}."
        
        # Check win condition
        if not any(cell is not None and cell[0] == "monster" for row in self._grid for cell in row):
            total_treasure = sum(weight for item_type, weight in self._items.items() if item_type == "treasure")
            result_msg += f" All monsters defeated! You win! Final stats: Treasure={total_treasure:.1f}kg, Hunger={self._hunger:.1f}, Health={self._health:.1f}."
        
        return result_msg

    @tool
    def eat(self, item: str, amount: float) -> str:
        """Eat food to restore health. Increases health up to a maximum of 1.0."""
        actual = self.use_item(item, amount)
        health_gain = actual * 1.0
        self._health = min(1.0, self._health + health_gain)
        self._hunger = max(0.0, self._hunger - actual * 2.0)
        if actual == amount:
            return f"Ate {actual:.1f}kg of {item}. Health increased by {health_gain:.1f}, hunger decreased by {actual*2.0:.1f}."
        return f"Ate {actual:.1f}kg of {item} (only {actual:.1f}kg available). Health increased by {health_gain:.1f}, hunger decreased by {actual*2.0:.1f}."


async def main():
    npc = NPC()
    PRINT_MAP_EVERY_TOOL_CALL = True

    print("Initial dungeon map:")
    npc.print_map()
    
    # Print tool calls
    def make_tool_hook(npc, print_map_flag):
        def on_tool_call(ctx: dict) -> None:
            args = ctx["arguments"]
            tool_name = ctx["tool_name"]
            emojis = {
                "move": "🚶",
                "pickup_item": "📦",
                "eat": "🍖",
                "fight_monster": "⚔️",
                "use_item": "🍽️",
                "python_exec": "🧮",
            }
            emoji = emojis.get(tool_name, "📝")
            print(f"  └── {emoji} {tool_name}({', '.join(f'{k}={v}' for k, v in args.items())})")
            if tool_name == "move" and "reason" in args:
                print(f"      Reason: {args['reason']}")
            x, y = npc._position
            cell = npc._grid[x][y]
            item_text = f"({x}, {y}): {cell[0]}" if cell else f"({x}, {y}): empty"
            print(f"      Pos: {x},{y} | {item_text} | Roar: {npc.roaring_volume(x, y):.2f} | Monsters: {npc.count_monsters()} | Hunger: {npc._hunger:.1f} | Health: {npc._health:.1f} | Weight: {npc.get_total_weight():.1f}kg")
            inv = npc._items if hasattr(npc, '_items') else {}
            if inv:
                print(f"      Items: {inv}")
            if print_map_flag:
                npc.print_map(x, y)
        return on_tool_call
    
    # Actually invoke
    try:
        result = await npc.invoke_agent(
            "Explore the dungeon. Pick up any items you find.",
            persistent_thread_id="adventure-1",
            hooks={"on_tool_call": [make_tool_hook(npc, PRINT_MAP_EVERY_TOOL_CALL)]},
        )
        print(f"\nResult: {result}")
    except GameOverError as e:
        print(f"\nGame Over: {e}")

if __name__ == "__main__":
    asyncio.run(main())
