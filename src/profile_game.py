"""Usage: profile_game.py [--runtime=<sec>]

Options:
  --runtime=<sec>  Time before terminating profile [default: 100]
"""

import cProfile
import errno
import os
import signal
from functools import wraps

from docopt import docopt

import game


def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


def profile_game(prof_path, runtime):
    game_window, clock = game.init()

    @timeout(runtime)
    def run_game(game_window, clock):
        game.game_loop(game_window, clock, stress_test=True)

    with cProfile.Profile() as pr:
        try:
            run_game(game_window, clock)
        except TimeoutError:
            pass
        except Exception:
            raise

    print(f"Writing results to {prof_path}.")
    pr.dump_stats(prof_path)


if __name__ == "__main__":
    arguments = docopt(__doc__)
    runtime = int(arguments["--runtime"])

    prof_path = os.path.join(os.getcwd(), "program.prof")
    profile_game(prof_path, runtime)
