"""Map generation and management for the dungeon crawler roguelike."""

import random
from enum import Enum
from typing import List, Tuple, Optional, Dict, Any


class TileType(Enum):
    """Enum representing different types of tiles in the dungeon."""
    WALL = "#"
    FLOOR = "."
    STAIRS_DOWN = ">"
    STAIRS_UP = "<"


class TileProperties:
    """Properties associated with each tile type."""
    
    PROPERTIES: Dict[TileType, Dict[str, Any]] = {
        TileType.WALL: {"walkable": False, "transparent": False, "symbol": "#"},
        TileType.FLOOR: {"walkable": True, "transparent": True, "symbol": "."},
        TileType.STAIRS_DOWN: {"walkable": True, "transparent": True, "symbol": ">"},
        TileType.STAIRS_UP: {"walkable": True, "transparent": True, "symbol": "<"},
    }
    
    @classmethod
    def is_walkable(cls, tile_type: TileType) -> bool:
        """Check if a tile type is walkable."""
        return cls.PROPERTIES[tile_type]["walkable"]
    
    @classmethod
    def is_transparent(cls, tile_type: TileType) -> bool:
        """Check if a tile type is transparent."""
        return cls.PROPERTIES[tile_type]["transparent"]
    
    @classmethod
    def get_symbol(cls, tile_type: TileType) -> str:
        """Get the display symbol for a tile type."""
        return cls.PROPERTIES[tile_type]["symbol"]


class Room:
    """Represents a rectangular room in the dungeon."""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        """Initialize a room with position and dimensions.
        
        Args:
            x: Left coordinate of the room.
            y: Top coordinate of the room.
            width: Width of the room.
            height: Height of the room.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    @property
    def center(self) -> Tuple[int, int]:
        """Get the center coordinates of the room."""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def intersects(self, other: 'Room') -> bool:
        """Check if this room intersects with another room."""
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)
    
    def contains_point(self, x: int, y: int) -> bool:
        """Check if a point is inside this room (including walls)."""
        return (self.x <= x < self.x + self.width and
                self.y <= y < self.y + self.height)
    
    def get_inner_area(self) -> List[Tuple[int, int]]:
        """Get all tiles inside the room (excluding walls)."""
        tiles = []
        for y in range(self.y + 1, self.y + self.height - 1):
            for x in range(self.x + 1, self.x + self.width - 1):
                tiles.append((x, y))
        return tiles


class GameMap:
    """Represents a single floor/map of the dungeon."""
    
    def __init__(self, width: int, height: int, floor_number: int = 1):
        """Initialize a new game map.
        
        Args:
            width: Width of the map in tiles.
            height: Height of the map in tiles.
            floor_number: The floor number this map represents.
        """
        self.width = width
        self.height = height
        self.floor_number = floor_number
        self.tiles: List[List[TileType]] = []
        self.rooms: List[Room] = []
        self.stairs_position: Optional[Tuple[int, int]] = None
        self.spawn_point: Optional[Tuple[int, int]] = None
        
        # Initialize with all walls
        self.tiles = [[TileType.WALL for _ in range(width)] for _ in range(height)]
    
    def generate_map(self) -> None:
        """Generate a complete dungeon map with rooms and corridors."""
        self._generate_rooms()
        self._connect_rooms()
        self._place_stairs()
        self._set_spawn_point()
    
    def _generate_rooms(self) -> None:
        """Generate random rooms on the map."""
        min_rooms = 6
        max_rooms = 12
        min_room_size = 5
        max_room_size = 15
        
        num_rooms = random.randint(min_rooms, max_rooms)
        
        for _ in range(num_rooms):
            room_width = random.randint(min_room_size, max_room_size)
            room_height = random.randint(min_room_size, max_room_size)
            
            # Ensure rooms fit within map boundaries
            max_x = self.width - room_width - 1
            max_y = self.height - room_height - 1
            
            if max_x <= 1 or max_y <= 1:
                continue
                
            room_x = random.randint(1, max_x)
            room_y = random.randint(1, max_y)
            
            new_room = Room(room_x, room_y, room_width, room_height)
            
            # Check if room overlaps with existing rooms
            if any(new_room.intersects(existing_room) for existing_room in self.rooms):
                continue
            
            # Carve out the room
            self._carve_room(new_room)
            self.rooms.append(new_room)
    
    def _carve_room(self, room: Room) -> None:
        """Carve out a room on the map (replace walls with floors)."""
        for y in range(room.y + 1, room.y + room.height - 1):
            for x in range(room.x + 1, room.x + room.width - 1):
                self.tiles[y][x] = TileType.FLOOR
    
    def _connect_rooms(self) -> None:
        """Connect all rooms with corridors."""
        if len(self.rooms) < 2:
            return
        
        # Connect each room to the next one
        for i in range(len(self.rooms) - 1):
            room1 = self.rooms[i]
            room2 = self.rooms[i + 1]
            self._create_corridor(room1.center, room2.center)
    
    def _create_corridor(self, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        """Create an L-shaped corridor between two points."""
        start_x, start_y = start
        end_x, end_y = end
        
        # Randomly choose whether to go horizontal first or vertical first
        if random.random() < 0.5:
            # Horizontal first, then vertical
            self._create_horizontal_tunnel(start_x, end_x, start_y)
            self._create_vertical_tunnel(start_y, end_y, end_x)
        else:
            # Vertical first, then horizontal
            self._create_vertical_tunnel(start_y, end_y, start_x)
            self._create_horizontal_tunnel(start_x, end_x, end_y)
    
    def _create_horizontal_tunnel(self, x_start: int, x_end: int, y: int) -> None:
        """Create a horizontal tunnel."""
        for x in range(min(x_start, x_end), max(x_start, x_end) + 1):
            if 0 < x < self.width - 1 and 0 < y < self.height - 1:
                self.tiles[y][x] = TileType.FLOOR
    
    def _create_vertical_tunnel(self, y_start: int, y_end: int, x: int) -> None:
        """Create a vertical tunnel."""
        for y in range(min(y_start, y_end), max(y_start, y_end) + 1):
            if 0 < x < self.width - 1 and 0 < y < self.height - 1:
                self.tiles[y][x] = TileType.FLOOR
    
    def _place_stairs(self) -> None:
        """Place stairs in a random room (not the first one)."""
        if len(self.rooms) < 2:
            return
        
        # Choose a random room (not the first one for spawn point)
        stair_room = random.choice(self.rooms[1:])
        
        # Place stairs in a random floor tile in the room
        floor_tiles = stair_room.get_inner_area()
        if floor_tiles:
            stairs_pos = random.choice(floor_tiles)
            self.stairs_position = stairs_pos
            x, y = stairs_pos
            self.tiles[y][x] = TileType.STAIRS_DOWN
    
    def _set_spawn_point(self) -> None:
        """Set the player spawn point in the first room."""
        if not self.rooms:
            return
        
        spawn_room = self.rooms[0]
        floor_tiles = spawn_room.get_inner_area()
        if floor_tiles:
            self.spawn_point = random.choice(floor_tiles)
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if a position is within map boundaries."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a position is walkable."""
        if not self.is_valid_position(x, y):
            return False
        return TileProperties.is_walkable(self.tiles[y][x])
    
    def get_tile(self, x: int, y: int) -> Optional[TileType]:
        """Get the tile type at a position."""
        if not self.is_valid_position(x, y):
            return None
        return self.tiles[y][x]
    
    def set_tile(self, x: int, y: int, tile_type: TileType) -> bool:
        """Set the tile type at a position."""
        if not self.is_valid_position(x, y):
            return False
        self.tiles[y][x] = tile_type
        return True
    
    def has_line_of_sight(self, x1: int, y1: int, x2: int, y2: int, max_range: int = 8) -> bool:
        """Check if there's line of sight between two points using Manhattan distance."""
        distance = abs(x1 - x2) + abs(y1 - y2)
        if distance > max_range:
            return False
        
        # Simple line-of-sight check using Bresenham's algorithm
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        
        while x != x2 or y != y2:
            if not self.is_valid_position(x, y):
                return False
            if not TileProperties.is_transparent(self.tiles[y][x]):
                return False
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        
        return True


class Dungeon:
    """Manages multiple floors of the dungeon."""
    
    def __init__(self, map_width: int = 80, map_height: int = 24):
        """Initialize the dungeon.
        
        Args:
            map_width: Width of each map floor.
            map_height: Height of each map floor.
        """
        self.map_width = map_width
        self.map_height = map_height
        self.floors: Dict[int, GameMap] = {}
        self.current_floor = 1
        self.max_floors = 2  # PoC: 1-2 floors
    
    def get_current_floor(self) -> GameMap:
        """Get the current floor map."""
        if self.current_floor not in self.floors:
            self._generate_floor(self.current_floor)
        return self.floors[self.current_floor]
    
    def _generate_floor(self, floor_number: int) -> GameMap:
        """Generate a specific floor."""
        game_map = GameMap(self.map_width, self.map_height, floor_number)
        game_map.generate_map()
        self.floors[floor_number] = game_map
        return game_map
    
    def go_down_stairs(self) -> bool:
        """Move to the next floor down."""
        if self.current_floor >= self.max_floors:
            return False
        
        self.current_floor += 1
        return True
    
    def go_up_stairs(self) -> bool:
        """Move to the next floor up."""
        if self.current_floor <= 1:
            return False
        
        self.current_floor -= 1
        return True
    
    def reset_dungeon(self) -> None:
        """Reset the entire dungeon."""
        self.floors.clear()
        self.current_floor = 1


class AgentManager:
    """Manages agent positions and interactions on the map."""
    
    def __init__(self, game_map: GameMap):
        """Initialize the agent manager.
        
        Args:
            game_map: The game map to manage agents on.
        """
        self.game_map = game_map
        self.agents: Dict[Tuple[int, int], List[Any]] = {}
    
    def place_agent(self, agent: Any, x: int, y: int) -> bool:
        """Place an agent at a specific position.
        
        Args:
            agent: The agent to place.
            x: X coordinate.
            y: Y coordinate.
            
        Returns:
            True if placement was successful, False otherwise.
        """
        if not self.game_map.is_walkable(x, y):
            return False
        
        pos = (x, y)
        if pos not in self.agents:
            self.agents[pos] = []
        self.agents[pos].append(agent)
        
        # Update agent's position if it has the attribute
        if hasattr(agent, 'position'):
            agent.position = pos
        
        return True
    
    def remove_agent(self, agent: Any) -> bool:
        """Remove an agent from the map.
        
        Args:
            agent: The agent to remove.
            
        Returns:
            True if removal was successful, False otherwise.
        """
        for pos, agent_list in self.agents.items():
            if agent in agent_list:
                agent_list.remove(agent)
                if not agent_list:
                    del self.agents[pos]
                return True
        return False
    
    def move_agent(self, agent: Any, new_x: int, new_y: int) -> bool:
        """Move an agent to a new position.
        
        Args:
            agent: The agent to move.
            new_x: New X coordinate.
            new_y: New Y coordinate.
            
        Returns:
            True if move was successful, False otherwise.
        """
        if not self.game_map.is_walkable(new_x, new_y):
            return False
        
        # Remove from old position
        old_pos = getattr(agent, 'position', None)
        if old_pos and old_pos in self.agents:
            if agent in self.agents[old_pos]:
                self.agents[old_pos].remove(agent)
                if not self.agents[old_pos]:
                    del self.agents[old_pos]
        
        # Add to new position
        new_pos = (new_x, new_y)
        if new_pos not in self.agents:
            self.agents[new_pos] = []
        self.agents[new_pos].append(agent)
        
        # Update agent's position
        if hasattr(agent, 'position'):
            agent.position = new_pos
        
        return True
    
    def get_agents_at(self, x: int, y: int) -> List[Any]:
        """Get all agents at a specific position.
        
        Args:
            x: X coordinate.
            y: Y coordinate.
            
        Returns:
            List of agents at the position.
        """
        return self.agents.get((x, y), [])
    
    def is_position_occupied(self, x: int, y: int) -> bool:
        """Check if a position is occupied by any agent.
        
        Args:
            x: X coordinate.
            y: Y coordinate.
            
        Returns:
            True if position is occupied, False otherwise.
        """
        return len(self.get_agents_at(x, y)) > 0
    
    def can_move_to(self, x: int, y: int, exclude_agent: Any = None) -> bool:
        """Check if an agent can move to a position.
        
        Args:
            x: X coordinate.
            y: Y coordinate.
            exclude_agent: Agent to exclude from occupation check.
            
        Returns:
            True if movement is possible, False otherwise.
        """
        if not self.game_map.is_walkable(x, y):
            return False
        
        agents_at_pos = self.get_agents_at(x, y)
        if exclude_agent:
            agents_at_pos = [a for a in agents_at_pos if a != exclude_agent]
        
        return len(agents_at_pos) == 0
    
    def get_all_agents(self) -> List[Any]:
        """Get all agents on the map.
        
        Returns:
            List of all agents.
        """
        all_agents = []
        for agent_list in self.agents.values():
            all_agents.extend(agent_list)
        return all_agents
    
    def clear_all_agents(self) -> None:
        """Remove all agents from the map."""
        self.agents.clear()


class MapRenderer:
    """Handles rendering of the map for terminal display."""
    
    def __init__(self, game_map: GameMap, agent_manager: AgentManager):
        """Initialize the map renderer.
        
        Args:
            game_map: The game map to render.
            agent_manager: The agent manager for entity positions.
        """
        self.game_map = game_map
        self.agent_manager = agent_manager
    
    def render_map(self, viewport_width: int = None, viewport_height: int = None, 
                   center_x: int = None, center_y: int = None) -> List[str]:
        """Render the map as a list of strings for terminal display.
        
        Args:
            viewport_width: Width of the viewport (defaults to map width).
            viewport_height: Height of the viewport (defaults to map height).
            center_x: X coordinate to center viewport on.
            center_y: Y coordinate to center viewport on.
            
        Returns:
            List of strings representing the rendered map.
        """
        if viewport_width is None:
            viewport_width = self.game_map.width
        if viewport_height is None:
            viewport_height = self.game_map.height
        
        # Calculate viewport bounds
        if center_x is not None and center_y is not None:
            start_x = max(0, center_x - viewport_width // 2)
            start_y = max(0, center_y - viewport_height // 2)
            end_x = min(self.game_map.width, start_x + viewport_width)
            end_y = min(self.game_map.height, start_y + viewport_height)
        else:
            start_x, start_y = 0, 0
            end_x = min(self.game_map.width, viewport_width)
            end_y = min(self.game_map.height, viewport_height)
        
        rendered_lines = []
        
        for y in range(start_y, end_y):
            line = ""
            for x in range(start_x, end_x):
                # Check for agents first (they override tiles)
                agents = self.agent_manager.get_agents_at(x, y)
                if agents:
                    # Use the first agent's symbol if available
                    agent = agents[0]
                    if hasattr(agent, 'symbol'):
                        line += agent.symbol
                        continue
                
                # Otherwise use the tile symbol
                tile = self.game_map.get_tile(x, y)
                if tile:
                    line += TileProperties.get_symbol(tile)
                else:
                    line += " "
            
            rendered_lines.append(line)
        
        return rendered_lines
    
    def get_map_info(self) -> str:
        """Get information about the current map.
        
        Returns:
            String containing map information.
        """
        info = f"Floor {self.game_map.floor_number}\n"
        info += f"Map size: {self.game_map.width}x{self.game_map.height}\n"
        info += f"Rooms: {len(self.game_map.rooms)}\n"
        if self.game_map.stairs_position:
            info += f"Stairs at: {self.game_map.stairs_position}\n"
        if self.game_map.spawn_point:
            info += f"Spawn point: {self.game_map.spawn_point}\n"
        return info
