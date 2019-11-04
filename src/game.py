import pygame
import sys

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


def game_loop(game_window):
    """Game loop"""
    game_running = True

    grid = road_grid.random_grid(GRID_WIDTH, GRID_HEIGHT)

    while game_running:
        # Loop through all active events
        for event in pygame.event.get():
            # Close the program if the user presses the 'X'
            if event.type == pygame.QUIT:
                game_running = False

        # Content here
        game_window.fill((255, 255, 255))

        # Render random road
        road_graphics.render_grid(game_window, grid)

        # Update our display
        pygame.display.update()


def exit():
    """Exit game"""
    # Uninitialize all pygame modules and quit the program
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    game_window = init()
    game_loop(game_window)
    exit()
