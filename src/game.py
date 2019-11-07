import pygame
import sys

import input
from road import graphics as road_gfx
from road.constants import TILE_WIDTH, TILE_HEIGHT
from road.network import RoadNetwork

GRID_WIDTH = 30
GRID_HEIGHT = 25

# Create width and height constants
WINDOW_WIDTH = TILE_WIDTH * GRID_WIDTH
WINDOW_HEIGHT = TILE_HEIGHT * GRID_HEIGHT


def init():
    """Initialize game window"""
    # Initialise all the pygame modules
    pygame.init()
    # Create a game window
    game_window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    # Set title
    pygame.display.set_caption("Traffic Simulator")
    return game_window


def exit():
    """Exit game"""
    # Uninitialize all pygame modules and quit the program
    pygame.quit()
    sys.exit()


##############
# Game Logic #
##############

def game_loop(window):
    """Game loop"""

    # Create road network
    network = RoadNetwork(GRID_WIDTH, GRID_HEIGHT)

    # # DEMO
    # for i in range(10):
    #     r, c = network.seed_pos
    #     network.traffic.add_vehicle(r, c)

    while 1:
        # Process user and window inputs
        # IMPORTANT: do not remove -- this enables us to close the game
        process_input(window, network)

        # Set background
        window.fill((255, 255, 255))

        # Render mouse grid cursor
        display_tile_cursor(window)

        # Step road network one tick
        network.step()

        # Render road network
        road_gfx.render_road_network(window, network)

        # DEMO
        randomize_vehicle_paths(window, network)

        # Update our display
        pygame.display.update()


def randomize_vehicle_paths(window, network):
    """DEMO: Send our single sim vehicle on errands"""
    import random

    # To seem more organic, only have sims travel to leaf nodes
    G = network.graph.G
    leaf_nodes = [x for x in G.nodes() if G.degree(x) == 1]

    for v in network.traffic.vehicles:
        if not v.path and leaf_nodes:
            random_node = random.choice(leaf_nodes)
            r, c = random_node
            v.set_destination(network.graph, r, c)


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
    r, c = input.mouse_coords_to_grid_index(TILE_WIDTH, TILE_HEIGHT)
    network.add_road((r, c))


def display_tile_cursor(window):
    """Highlights tile underneath mouse"""
    r, c = input.mouse_coords_to_grid_index(TILE_WIDTH, TILE_HEIGHT)
    x = c * TILE_WIDTH
    y = r * TILE_HEIGHT
    rect = pygame.Rect(x, y, TILE_WIDTH, TILE_HEIGHT)
    pygame.draw.rect(window, (0, 255, 255), rect)


if __name__ == "__main__":
    game_window = init()
    game_loop(game_window)
    exit()
