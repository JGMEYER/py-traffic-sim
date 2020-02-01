import pygame
import sys

import input
from road import graphics as road_gfx
from road.common import TILE_WIDTH as tw, TILE_HEIGHT as th
from road.network import RoadNetwork
from settings import GameSettings

# Create width and height constants
WINDOW_WIDTH = tw * GameSettings.GRID_WIDTH
WINDOW_HEIGHT = th * GameSettings.GRID_HEIGHT

"""
This is the main file for game logic. Code here may be messy and break good
practices, like variable encapsulation, in favor of fast iteration while
testing.
"""


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


# DEMO
STRESS_TEST = False


##############
# Game Logic #
##############

def game_loop(window, clock):
    """Game loop"""

    # Create road network
    network = RoadNetwork(
        GameSettings.GRID_WIDTH,
        GameSettings.GRID_HEIGHT,
        vehicle_stop_wait_time=GameSettings.VEHICLE_STOP_WAIT_TIME,
        intersection_clear_time=GameSettings.INTERSECTION_CLEAR_TIME,
    )

    # Create road screen (for rendering)
    road_screen = road_gfx.RoadScreen(
        network,
        display_travel_edges=GameSettings.DISPLAY_TRAVEL_EDGES,
        randomize_vehicle_color=GameSettings.RANDOMIZE_VEHICLE_COLOR,
    )
    road_screen.clear(window, road_screen.bg.image)

    # DEMO
    if STRESS_TEST:
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
        network.add_road(network.h//2, network.w//2,
                         restrict_to_neighbors=False)

    while 1:
        # Get loop time, convert milliseconds to seconds
        tick = clock.tick(60)/1000

        # Process user and window inputs
        # IMPORTANT: do not remove -- this enables us to close the game
        process_input(window, network)

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

def process_input(window, network):
    """Loop through all active events and process accordingly"""
    for event in pygame.event.get():
        # Close the program if the user presses the 'X'
        if event.type == pygame.QUIT:
            exit()
        # Add new road tile when user presses and holds mouse button
        elif ((event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)
              or (event.type == pygame.MOUSEMOTION and event.buttons[0] == 1)):
            process_mouse_button_down(window, network)


def process_mouse_button_down(window, network):
    """Place new tile on grid"""
    r, c = input.mouse_coords_to_grid_index(tw, th)
    road_added = network.add_road(r, c)

    # DEMO
    if not STRESS_TEST:
        import random
        if road_added and random.random() < 0.5:
            node = random.choice(list(network.graph.G.nodes))
            network.traffic.add_vehicle(node)


# BROKEN
def display_tile_cursor(window):
    """Highlights tile underneath mouse"""
    r, c = input.mouse_coords_to_grid_index(tw, th)
    x = c * tw
    y = r * th
    rect = pygame.Rect(x, y, tw, th)
    pygame.draw.rect(window, (0, 255, 255), rect)


if __name__ == "__main__":
    game_window, clock = init()
    game_loop(game_window, clock)
    exit()
