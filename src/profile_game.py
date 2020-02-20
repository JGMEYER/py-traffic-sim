import cProfile
import os

import game


def profile_game(prof_path):
    game_window, clock = game.init()

    with cProfile.Profile() as pr:
        try:
            game.game_loop(game_window, clock)
        except KeyboardInterrupt:
            pass
        except Exception:
            raise

    pr.dump_stats(prof_path)


if __name__ == "__main__":
    prof_path = os.path.join(os.getcwd(), "program.prof")
    profile_game(prof_path)
