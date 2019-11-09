import pygame
import sys

import input
from road import graphics as road_gfx
from road.constants import TILE_WIDTH as tw, TILE_HEIGHT as th
from road.network import RoadNetwork

GRID_WIDTH = 25
GRID_HEIGHT = 15

# Create width and height constants
WINDOW_WIDTH = tw * GRID_WIDTH
WINDOW_HEIGHT = th * GRID_HEIGHT


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

    # Create road screen (for rendering)
    road_screen = road_gfx.RoadScreen(network)
    road_screen.clear(window, road_screen.bg.image)

    # DEMO
    stress_test = True
    if stress_test:
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
    # from road.grid import RoadSegmentNode
    # from road.constants import RoadNodeType, Direction
    # node_a = RoadSegmentNode((0, 0), Direction.RIGHT, RoadNodeType.EXIT)
    # node_b = RoadSegmentNode((GRID_HEIGHT-1, GRID_WIDTH-1),
    #                          Direction.RIGHT, RoadNodeType.EXIT)
    # network.graph.G.add_edge(node_a, node_b)
    # v = network.traffic.add_vehicle(node_a)
    # v.path = [node_b, node_a, node_b, node_a]

    while 1:
        # Process user and window inputs
        # IMPORTANT: do not remove -- this enables us to close the game
        process_input(window, network)

        # Set background
        # window.fill((255, 255, 255))

        # # Render mouse grid cursor
        # display_tile_cursor(window)

        # Step road network one tick
        network.step()

        # # Render road network
        # road_gfx.render_road_network(window, network, edges=True, nodes=True)

        # DEMO
        randomize_vehicle_paths(window, network)

        # Update our display
        # window.blit(road_screen.bg.image, (0, 0))
        road_screen.update()
        rects = road_screen.draw(window)
        # if rects:
        #     print(rects)
        pygame.display.update(rects)


# DEMO
def randomize_vehicle_paths(window, network):
    # Send our sim vehicles on random errands
    import random
    if not list(network.graph.G.nodes):
        return
    for v in network.traffic.vehicles:
        if not v.path:
            random_node = random.choice(list(network.graph.G.nodes))
            path = network.graph.shortest_path(v.last_node, random_node)
            v.set_path(path)
        # road_gfx.render_path(window, v.path)


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
    network.add_road(r, c)

    # # DEMO
    # import random
    # if road_added and random.random() < 0.3:
    #     node = random.choice(list(network.graph.G.nodes))
    #     network.traffic.add_vehicle(node)


def display_tile_cursor(window):
    """Highlights tile underneath mouse"""
    r, c = input.mouse_coords_to_grid_index(tw, th)
    x = c * tw
    y = r * th
    rect = pygame.Rect(x, y, tw, th)
    pygame.draw.rect(window, (0, 255, 255), rect)


if __name__ == "__main__":
    game_window = init()
    game_loop(game_window)
    exit()
