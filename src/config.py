from dynaconf import settings, Validator

settings.validators.register(
    # Grid
    Validator("TILE_WIDTH", condition=lambda x: x % 2 == 0),
    Validator("TILE_HEIGHT", condition=lambda x: x % 2 == 0),
    Validator("TILE_HEIGHT", eq=settings.TILE_WIDTH),
    Validator("ROAD_WIDTH", condition=lambda x: x % 2 == 0),
)

settings.validators.validate()

config = settings
