#!/usr/bin/env python3
"""Test script to verify the map generation system."""

from map import GameMap, Dungeon, AgentManager, MapRenderer


def test_basic_map_generation():
    """Test basic map generation functionality."""
    print("Testing basic map generation...")
    
    # Create a small test map
    game_map = GameMap(40, 20, 1)
    game_map.generate_map()
    
    print(f"Generated map with {len(game_map.rooms)} rooms")
    print(f"Stairs position: {game_map.stairs_position}")
    print(f"Spawn point: {game_map.spawn_point}")
    
    # Test map validation
    assert game_map.is_valid_position(0, 0)
    assert game_map.is_valid_position(39, 19)
    assert not game_map.is_valid_position(-1, 0)
    assert not game_map.is_valid_position(40, 0)
    
    # Test walkability
    assert not game_map.is_walkable(0, 0)  # Wall at edge
    if game_map.spawn_point:
        x, y = game_map.spawn_point
        assert game_map.is_walkable(x, y)  # Spawn should be walkable
    
    print("✓ Basic map generation test passed\n")


def test_agent_management():
    """Test agent placement and movement."""
    print("Testing agent management...")
    
    game_map = GameMap(40, 20, 1)
    game_map.generate_map()
    
    agent_manager = AgentManager(game_map)
    
    # Create a simple test agent
    class TestAgent:
        def __init__(self, symbol):
            self.symbol = symbol
            self.position = None
    
    player = TestAgent("@")
    monster = TestAgent("g")
    
    # Test agent placement
    if game_map.spawn_point:
        x, y = game_map.spawn_point
        assert agent_manager.place_agent(player, x, y)
        assert agent_manager.is_position_occupied(x, y)
        
        # Test getting agents at position
        agents = agent_manager.get_agents_at(x, y)
        assert len(agents) == 1
        assert agents[0] == player
    
    # Test movement
    if game_map.spawn_point:
        x, y = game_map.spawn_point
        # Try to move to adjacent floor tile
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = x + dx, y + dy
            if game_map.is_walkable(new_x, new_y):
                assert agent_manager.move_agent(player, new_x, new_y)
                assert agent_manager.get_agents_at(x, y) == []
                assert len(agent_manager.get_agents_at(new_x, new_y)) == 1
                break
    
    print("✓ Agent management test passed\n")


def test_dungeon_floors():
    """Test multi-floor dungeon functionality."""
    print("Testing multi-floor dungeon...")
    
    dungeon = Dungeon(40, 20)
    
    # Test floor generation
    floor1 = dungeon.get_current_floor()
    assert floor1.floor_number == 1
    
    # Test going down stairs
    assert dungeon.go_down_stairs()
    floor2 = dungeon.get_current_floor()
    assert floor2.floor_number == 2
    assert floor1 != floor2  # Should be different maps
    
    # Test going up stairs
    assert dungeon.go_up_stairs()
    assert dungeon.get_current_floor().floor_number == 1
    
    # Test boundaries
    assert dungeon.go_down_stairs()  # Go to floor 2
    assert not dungeon.go_down_stairs()  # Can't go past floor 2
    assert dungeon.go_up_stairs()  # Back to floor 1
    assert not dungeon.go_up_stairs()  # Can't go above floor 1
    
    print("✓ Multi-floor dungeon test passed\n")


def test_map_rendering():
    """Test map rendering functionality."""
    print("Testing map rendering...")
    
    game_map = GameMap(20, 10, 1)
    game_map.generate_map()
    agent_manager = AgentManager(game_map)
    renderer = MapRenderer(game_map, agent_manager)
    
    # Test basic rendering
    rendered = renderer.render_map()
    assert len(rendered) == game_map.height
    assert len(rendered[0]) == game_map.width
    
    # Test viewport rendering
    viewport = renderer.render_map(viewport_width=10, viewport_height=5)
    assert len(viewport) <= 5  # May be less if map is smaller
    assert len(viewport[0]) <= 10  # May be less if map is smaller
    
    # Test centered viewport
    if game_map.spawn_point:
        x, y = game_map.spawn_point
        centered = renderer.render_map(viewport_width=10, viewport_height=5, 
                                     center_x=x, center_y=y)
        assert len(centered) <= 5  # May be less if map is smaller
        assert len(centered[0]) <= 10  # May be less if map is smaller
    
    # Test map info
    info = renderer.get_map_info()
    assert "Floor 1" in info
    assert "Map size: 20x10" in info
    
    print("✓ Map rendering test passed\n")


def test_line_of_sight():
    """Test line of sight calculation."""
    print("Testing line of sight...")
    
    game_map = GameMap(20, 10, 1)
    game_map.generate_map()
    
    # Test line of sight within spawn room
    if game_map.spawn_point:
        x, y = game_map.spawn_point
        # Should be able to see nearby tiles in the same room
        assert game_map.has_line_of_sight(x, y, x + 1, y)
        assert game_map.has_line_of_sight(x, y, x, y + 1)
        
        # Should not be able to see through walls
        assert not game_map.has_line_of_sight(x, y, 0, 0)
        
        # Test range limitation
        assert not game_map.has_line_of_sight(x, y, x + 10, y, max_range=5)
    
    print("✓ Line of sight test passed\n")


def main():
    """Run all tests."""
    print("Running map system tests...\n")
    
    try:
        test_basic_map_generation()
        test_agent_management()
        test_dungeon_floors()
        test_map_rendering()
        test_line_of_sight()
        
        print("🎉 All tests passed!")
        
        # Show a sample map
        print("\nSample generated map:")
        game_map = GameMap(40, 20, 1)
        game_map.generate_map()
        agent_manager = AgentManager(game_map)
        renderer = MapRenderer(game_map, agent_manager)
        
        rendered_map = renderer.render_map()
        for line in rendered_map:
            print(line)
        
        print(f"\n{renderer.get_map_info()}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
