import pygame


def mouse_coord_to_grid_coord(tile_width, tile_height):
    x, y = pygame.mouse.get_pos()
    return (y // tile_height, x // tile_width)  # (row, column)
