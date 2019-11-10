import pygame

from road.constants import world_coords_to_grid_index


def mouse_coords_to_grid_index(tile_width, tile_height):
    x, y = pygame.mouse.get_pos()
    return world_coords_to_grid_index(x, y)
