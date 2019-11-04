import pygame
import sys

import input
from road import grid as road_grid  # TODO fix imports / names
from road import graphics as road_graphics  # TODO fix imports / names

GRID_WIDTH = 30
GRID_HEIGHT = 25

# Create width and height constants
WINDOW_WIDTH = road_graphics.TILE_WIDTH * GRID_WIDTH
WINDOW_HEIGHT = road_graphics.TILE_HEIGHT * GRID_HEIGHT


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
    # grid = road_grid.random_grid(GRID_WIDTH, GRID_HEIGHT)
    grid = road_grid.TileGrid(GRID_WIDTH, GRID_HEIGHT)
    # Add starting tile from which all roads will connect
    grid.add_tile(GRID_WIDTH//2, GRID_HEIGHT//2, restrict_to_neighbors=False)

    while 1:
        # Process user and window inputs
        # IMPORTANT: do not remove -- this enables us to close the game
        process_input(grid)

        # Set background
        window.fill((255, 255, 255))

        # Render mouse grid cursor
        display_tile_cursor(window)

        # Render random road
        road_graphics.render_grid(window, grid)

        # Update our display
        pygame.display.update()


def process_input(grid):
    # Loop through all active events
    for event in pygame.event.get():
        print(event)
        # Close the program if the user presses the 'X'
        if event.type == pygame.QUIT:
            exit()
        # Add new road tile when user presses and holds mouse button
        elif ((event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)
              or (event.type == pygame.MOUSEMOTION and event.buttons[0] == 1)):
            process_mouse_button_down(grid)


def process_mouse_button_down(grid):
    """Place new tile on grid"""
    r, c = input.mouse_coord_to_grid_coord(road_graphics.TILE_WIDTH,
                                           road_graphics.TILE_HEIGHT)
    grid.add_tile(r, c)


def display_tile_cursor(window):
    """Highlights tile underneath mouse"""
    r, c = input.mouse_coord_to_grid_coord(road_graphics.TILE_WIDTH,
                                           road_graphics.TILE_HEIGHT)
    x = c * road_graphics.TILE_WIDTH
    y = r * road_graphics.TILE_HEIGHT
    rect = pygame.Rect(x, y, road_graphics.TILE_WIDTH,
                       road_graphics.TILE_HEIGHT)
    pygame.draw.rect(window, (0, 255, 255), rect)


if __name__ == "__main__":
    game_window = init()
    game_loop(game_window)
    exit()
