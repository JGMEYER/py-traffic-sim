"""Usage: profile_game.py [--runtime=<sec>]

Options:
  --runtime=<sec>  Time before terminating profile [default: 100]
"""

import cProfile
import errno
import os
import signal
from functools import wraps
from pathlib import Path

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


def profile_game(runtime) -> cProfile.Profile:
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

    return pr


def output_stats(pr: cProfile.Profile, filepath):
    print(f"Writing results to {filepath}.")
    pr.dump_stats(filepath)


if __name__ == "__main__":
    arguments = docopt(__doc__)
    runtime = int(arguments["--runtime"])

    output_dir = os.path.join(os.getcwd(), "profiles")
    Path(output_dir).mkdir(exist_ok=True)

    prof_path = os.path.join(output_dir, "profile.prof")
    pstats_path = os.path.join(output_dir, "profile.pstats")

    pr = profile_game(runtime)

    output_stats(pr, prof_path)
    output_stats(pr, pstats_path)
