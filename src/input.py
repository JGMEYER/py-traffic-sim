import pygame

from road import grid


def mouse_coords_to_grid_index(tile_width, tile_height):
    x, y = pygame.mouse.get_pos()
    return grid.world_coords_to_grid_index(x, y)
