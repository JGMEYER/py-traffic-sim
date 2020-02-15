import pygame
import sys

from config import config

import input
from road import graphics as road_gfx
from road.network import RoadNetwork

"""
This is the main file for game logic. Code here may be messy and break good
practices, like variable encapsulation, in favor of fast iteration while
testing.
"""

WINDOW_WIDTH = config.TILE_WIDTH * config.GRID_WIDTH
WINDOW_HEIGHT = config.TILE_HEIGHT * config.GRID_HEIGHT


def init():
    """Initialize game window"""
    # Initialise all the pygame modules
    pygame.init()

    # Create a game window
    game_window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    # Set title
    pygame.display.set_caption("Traffic Simulator")

    # Initialize clock
    clock = pygame.time.Clock()

    return game_window, clock


def exit():
    """Exit game"""
    # Uninitialize all pygame modules and quit the program
    pygame.quit()
    sys.exit()


##############
# Game Logic #
##############


def game_loop(window, clock):
    """Game loop"""

    # Create road network
    network = RoadNetwork(config, config.GRID_WIDTH, config.GRID_HEIGHT)

    # Create road screen (for rendering)
    road_screen = road_gfx.RoadScreen(config, network)
    road_screen.clear(window, road_screen.bg.image)

    # DEMO
    if config.STRESS_TEST:
        import random

        network.add_road(0, 0, restrict_to_neighbors=False)
        # Fill entire network grid
        for r in range(network.h):
            for c in range(network.w):
                network.add_road(r, c, restrict_to_neighbors=True)
        # Add a bunch of vehicles
        for n in range(1000):
            node = random.choice(list(network.graph.G.nodes))
            network.traffic.add_vehicle(node)
    else:
        network.add_road(
            network.h // 2, network.w // 2, restrict_to_neighbors=False
        )

    while 1:
        # Get loop time, convert milliseconds to seconds
        tick = clock.tick(60) / 1000

        # Process user and window inputs
        # IMPORTANT: do not remove -- this enables us to close the game
        process_input(config, window, network)

        # # Render mouse grid cursor
        # display_tile_cursor(window)

        # Step road network one tick
        network.step(tick)

        # DEMO
        randomize_vehicle_paths(window, network)

        # Update our display
        road_screen.update()
        rects = road_screen.draw(window)
        pygame.display.update(rects)


# DEMO
def randomize_vehicle_paths(window, network):
    # Send our sim vehicles on random errands
    import random

    if not list(network.graph.G.nodes):
        return
    for v in network.traffic.vehicles:
        if not v._path:
            random_node = random.choice(list(network.graph.G.nodes))
            path = network.graph.shortest_path(v._last_t_node, random_node)
            v.set_path(path)


#########
# Input #
#########


def process_input(config, window, network):
    """Loop through all active events and process accordingly"""
    for event in pygame.event.get():
        # Close the program if the user presses the 'X'
        if event.type == pygame.QUIT:
            exit()
        # Add new road tile when user presses and holds mouse button
        elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or (
            event.type == pygame.MOUSEMOTION and event.buttons[0] == 1
        ):
            process_mouse_button_down(config, window, network)


def process_mouse_button_down(config, window, network):
    """Place new tile on grid"""
    r, c = input.mouse_coords_to_grid_index(
        config.TILE_WIDTH, config.TILE_HEIGHT
    )
    road_added = network.add_road(r, c)

    # DEMO
    if not config.STRESS_TEST:
        import random

        if road_added and random.random() < 0.5:
            node = random.choice(list(network.graph.G.nodes))
            network.traffic.add_vehicle(node)


# BROKEN
def display_tile_cursor(window):
    """Highlights tile underneath mouse"""
    r, c = input.mouse_coords_to_grid_index(
        config.TILE_WIDTH, config.TILE_HEIGHT
    )
    x = c * config.TILE_WIDTH
    y = r * config.TILE_HEIGHT
    rect = pygame.Rect(x, y, config.TILE_WIDTH, config.TILE_HEIGHT)
    pygame.draw.rect(window, (0, 255, 255), rect)


if __name__ == "__main__":
    game_window, clock = init()
    game_loop(game_window, clock)
    exit()
