import pygame
import sys

# Create width and height constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


def init():
    # Initialise all the pygame modules
    pygame.init()
    # Create a game window
    game_window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    # Set title
    pygame.display.set_caption("Traffic Simulator")

    return game_window


def game_loop(game_window):
    """ Game Loop """
    game_running = True

    while game_running:
        # Loop through all active events
        for event in pygame.event.get():
            # Close the program if the user presses the 'X'
            if event.type == pygame.QUIT:
                game_running = False

        # Content here
        game_window.fill((255, 255, 255))

        filled_rect = pygame.Rect(100, 100, 30, 30)
        pygame.draw.rect(game_window, (0, 0, 0), filled_rect)

        # Update our display
        pygame.display.update()


def exit():
    # Uninitialize all pygame modules and quit the program
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    game_window = init()
    game_loop(game_window)
    exit()
