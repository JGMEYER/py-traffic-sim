# TODO Add validation here: https://dynaconf.readthedocs.io/en/latest/guides/validation.html
# e.g. ensure constraints in common.py are met

from dynaconf import settings, Validator

settings.validators.register(
    # Grid
    Validator("TILE_WIDTH", condition=lambda x: x % 2 == 0),
    Validator("TILE_HEIGHT", condition=lambda x: x % 2 == 0),
)

settings.validators.validate()


# class GameSettings:
#     """Game settings"""

#     # Traffic
#     VEHICLE_STOP_WAIT_TIME = 0.5  # sec
#     INTERSECTION_CLEAR_TIME = 0.35  # sec

#     # Graphics
#     DISPLAY_TRAVEL_EDGES = True
#     RANDOMIZE_VEHICLE_COLOR = True

#     # Game window size
#     GRID_WIDTH = 25
#     GRID_HEIGHT = 15
