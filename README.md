# Py-traffic-sim

[![Code Style Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black/)

## About

A program to simulate vehicle traffic patterns using Python and pygame.

## Installing and running the program

1. Install [pipenv](https://pipenv-fork.readthedocs.io/en/latest/basics.html).
1. Run $ `pipenv install --dev`.
1. Run $ `pipenv run pre-commit install` to configure git pre-commit hooks.
1. From the project directory run: $ `pipenv run python src/game.py`

## Running tests

$ `pipenv run pytest`

You can include `-vv` for higher verbosity.

## Profiling

```NOTE: Check out src/profile_game.py for available cli args.```

## snakeviz

1. Create a profile.prof and visualize the results with snakeviz:

    $ `pipenv run python src/profile_game.py && pipenv run snakeviz profiles/profile.prof`

## gprof2dot

1. Install graphviz. This will give you the `dot` cli tool.

    $ `brew install graphviz`

1. Create a profile.pstats and visualize the results with gprof2dot:

    $ `pipenv run python src/profile_game.py && pipenv run gprof2dot -f pstats profiles/profile.pstats | dot -Tpng -o /tmp/prof_output.png && open /tmp/prof_output.png`

## Modifying Settings

All settings can be found in `src/settings.toml`. By default, `src/.env` is set to the `development` environment, so the game will run using the settings in `[default]` with any overrides from `[development]`.

Setting values can be validated in `src/config.py`, e.g. to keep an integer value between a certain range. If adding/modifying a setting, be sure to make any necessary modifications to the setting's `Validator`, or add a new `Validator` if needed.

Check out the [dynaconf](https://github.com/rochacbruno/dynaconf) repo for additional documentation.

## Gameplay basics

In the game window, you'll see a single black square representing the "root" road segment. Click and drag beside this element to begin building a road. The program will randomly populate vehicles as segments are added.

For now, all new road segments need to be built from the existing road segment.

Example road:

![Example Road](/images/road-example.png)

Example road with `GameSettings.DISPLAY_TRAVEL_EDGES` enabled:

![Example Travel Edges](/images/travel-edges-example.png)

## Vision

This project was designed as a fun way to learn how to architect graphical Python applications and explore how bad intersection traffic rules can cause traffic problems elsewhere in a street grid.

The goal of the project is very open ended and items are added on as I come up with ideas that seem both interesting and fun to implement.

## Roadmap

While no feature or timeline is set in stone, here is a tentative sense of direction of the project.

### v0.1 - Base logic

- **Vehicle collisions:** Vehicles should follow vehicles in front of them and not overlap
- **4-way stops:** Intersections should operate as 4-way stops, where new vehicles yield to existing stopped vehicles and progress in a circular pattern as the intersection builds a queue.
- **UI elements base:** A solid base for creating and extending UI elements that can be manipulated by the user in-game.
- **In-game settings adjustments:** The user should be able to adjust things like vehicle speed, traffic graph display, etc. from within the game via a simple UI. v0 because this will be vital in future debugging/tests.

### v0.2 - Objectives

- **Vehicle objectives:** Vehicles should be given randomized, but logical objectives to simulate realistic patterns. e.g. car leaves house to go to grocery store, car returns back home.
- **Roadside buildings:** Buildings should be placeable as objectives along the roadside for Vehicles to travel to.
- **Load / Save:** Players should be able to save and load map files.

### v0.3 - Timed traffic lights

- **Traffic lights:** In addition to 4-way stops, automated traffic lights should be added to all intersections.
- **Timed traffic lights:** User should have the ability to control traffic light timings in-game via a UI.
- **Editable traffic light patterns:** User should ahve the ability to control which lanes are active and inactive during a time traffic light phase.

### v0.4 - Additional road types

- **3,4-lane roads:** Larger road types should logically connect to roads of smaller/larger lane width. Selection should be choosable from the UI.
