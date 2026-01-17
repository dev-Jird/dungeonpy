# AGENTS.md

This document describes the main **agents** (entities with behavior and state) in the terminal-based dungeon crawler roguelike and provides development guidelines for Cascade agents.

Focus for PoC: 1–2 floors, basic movement, simple turn-based combat, random events, class selection.

## 1. Player Agent

The only agent directly controlled by the user.

### Core Attributes
- `name`                (str) – player's chosen name
- `class_type`          (str) – "Warrior", "Rogue", or "Mage"
- `max_hp` / `current_hp` (int)
- `attack`              (int) – base damage before defense reduction
- `defense`             (int) – flat damage reduction
- `position`            (tuple[int, int]) – (x, y) on current floor
- `inventory`           (list) – items (strings for PoC: "Potion", "Sword", etc.)
- `floor`               (int) – current dungeon level (starts at 1)

### Starting Stats (PoC values)

| Class    | HP   | Attack | Defense | Special (PoC)             |
|----------|------|--------|---------|---------------------------|
| Warrior  | 120  | 15     | 10      | +20% damage when HP < 30% |
| Rogue    | 80   | 20     | 5       | 25% chance to evade attack|
| Mage     | 90   | 18     | 7       | +5 magic damage (future)  |

### Behaviors (PoC scope)
- Move: ↑ ↓ ← → (WASD or arrow keys)
- Attack (when adjacent to monster)
- Use item from inventory
- Take stairs → next floor (when found)

## 2. Monster Agents

Hostile NPCs that fight the player.

### Core Attributes
- `type`                (str) – "Goblin", "Skeleton", "Troll", etc.
- `max_hp` / `current_hp`
- `attack`
- `defense`
- `position`            (tuple[int, int])
- `symbol`              (str) – terminal display char (e.g. 'g', 'S', 'T')

### Difficulty Scaling Formula (PoC)
stat = base + (floor - 1) × multiplier

### Monster Types & Base Stats (PoC)

| Type      | Base HP | HP Multi | Base Atk | Atk Multi | Base Def | Def Multi | Symbol | Notes                     |
|-----------|---------|----------|----------|-----------|----------|-----------|--------|---------------------------|
| Goblin    | 50      | ×12      | 10       | ×2        | 5        | ×1        | g      | Fast, weak                |
| Skeleton  | 60      | ×15      | 12       | ×2.5      | 6        | ×1.5      | S      | Slightly tougher          |
| Troll     | 100     | ×20      | 15       | ×3        | 8        | ×2        | T      | Floor 2+ only, dangerous  |

### AI Behavior (very simple for PoC)
1. If player is adjacent → attack
2. Else if player is visible (within 6–8 tiles manhattan distance) → move toward player
3. Else → random valid move or stay still

## 3. Random Event "Agents" (non-persistent)

These are lightweight, fire-and-forget interactions triggered mostly during movement.

### Possible Events (PoC pool)

| Event             | Approx. Chance | Effect                                                                 |
|-------------------|----------------|------------------------------------------------------------------------|
| Nothing           | ~65%           | —                                                                      |
| Find Health Potion| ~15–18%        | +30–50 HP (capped at max_hp)                                           |
| Find Weapon       | ~6–8%          | +3 to +7 permanent attack boost                                        |
| Trap (spikes)     | ~5%            | 10–25 damage                                                           |
| Ambush!           | ~6–9%          | Spawn 1 random monster adjacent or nearby                              |

## Quick Class Design Summary (for reference)

```python
class Agent:
    def __init__(self, hp, atk, def_, symbol="?"):
        self.max_hp = self.current_hp = hp
        self.attack = atk
        self.defense = def_
        self.position = (0, 0)
        self.symbol = symbol

class Player(Agent):
    def __init__(self, class_type):
        if class_type == "Warrior":
            super().__init__(120, 15, 10, "@")
        elif class_type == "Rogue":
            super().__init__(80, 20, 5, "@")
        elif class_type == "Mage":
            super().__init__(90, 18, 7, "@")
        self.class_type = class_type
        self.inventory = []
        self.floor = 1

class Monster(Agent):
    # initialized with floor-adjusted stats
    pass
```

---

## Cascade Agent Development Guidelines

### Implementation Priorities (POC Order)
1. **Core Agent Classes** - Implement Player, Monster, and base Agent classes
2. **Map System** - Basic grid-based dungeon with walls, floors, and stairs
3. **Movement System** - WASD/arrow key input with collision detection
4. **Combat System** - Simple turn-based combat with damage calculation
5. **UI Rendering** - Terminal display using curses or blessed
6. **Random Events** - Movement-triggered events as specified above

### Code Style Requirements
- **Type Hints**: Required for all method signatures and class attributes
- **Docstrings**: Use Google-style docstrings for all classes and methods
- **Error Handling**: Validate player input and game state changes
- **Modular Design**: Separate concerns (UI, game logic, data structures)

### Terminal UI Guidelines
- **Minimum Size**: Support 80x24 terminal size
- **Display Symbols**: Use the symbols defined in agent specifications
- **Color Support**: Optional but should work without colors
- **Performance**: Real-time response for user input

### Key Implementation Notes

#### Player Class Implementation
```python
class Player(Agent):
    def __init__(self, name: str, class_type: str):
        # Set stats based on class_type
        # Initialize empty inventory
        # Set starting position to (1, 1) or map spawn point
        pass
    
    def move(self, dx: int, dy: int, game_map) -> bool:
        # Check boundaries and collisions
        # Update position if valid
        return True/False
    
    def attack(self, target: 'Monster') -> int:
        # Calculate damage: attack - target.defense
        # Apply class special abilities
        return damage_dealt
```

#### Monster AI Implementation
```python
class Monster(Agent):
    def __init__(self, monster_type: str, floor: int, position: tuple):
        # Apply floor scaling to base stats
        pass
    
    def take_turn(self, player: Player, game_map) -> str:
        # Simple AI: move toward player if visible, attack if adjacent
        return action_taken
```

### Game Loop Structure
```python
def main_game_loop():
    # Initialize game objects
    # Main loop:
    #   1. Get player input
    #   2. Process player action
    #   3. Handle random events
    #   4. Process monster turns
    #   5. Update UI
    #   6. Check win/lose conditions
```

### Testing Requirements
- Unit tests for each agent class
- Integration tests for combat and movement
- Manual testing for terminal rendering
- Edge case testing (boundary conditions, invalid inputs)

### Common Pitfalls to Avoid
- **Hardcoded map sizes** - Use configurable dimensions
- **Blocking input** - Use non-blocking keyboard input
- **Memory leaks** - Proper cleanup of game objects
- **State inconsistency** - Validate all game state changes

### File Organization Suggested
```
dungeonpy/
├── agents.py          # Agent classes (Player, Monster)
├── map.py             # Map generation and management
├── combat.py          # Combat system
├── ui.py              # Terminal rendering
├── events.py          # Random event system
├── game.py            # Main game loop
└── utils.py           # Helper functions
```

### Performance Considerations
- Use efficient data structures for map representation
- Minimize screen redraws - only update changed areas
- Cache frequently accessed calculations
- Consider frame rate limiting for smooth gameplay

---
*This guide should be referenced by Cascade agents for all development decisions. Update this file as the architecture evolves.*