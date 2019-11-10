#!/bin/bash

# More information on getopts at:
# https://pubs.opengroup.org/onlinepubs/9699919799/utilities/getopts.html

print_usage() {
  printf "Usage: $0 [-s]"
}

exec=true

while getopts ':s' flag; do
  case "${flag}" in
    s)
      # -s : skip game execution
      exec=false ;;
    \?)
      print_usage
      exit 1
      ;;
  esac
done

if [ "$exec" = true ] ; then
  # Run game and generate profile
  pipenv run python -m cProfile -o program.prof src/game.py &&
  pipenv run snakeviz program.prof
else
  # View profile
  pipenv run snakeviz program.prof
fi
