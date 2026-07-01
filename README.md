# Overview

This is a collection of tools, utilities, and scripts that have been developed under the guidance of Jillian Bellovary
at the American Museum of Natural History to aid in the research and analysis of cosmological phenomena with a special
focus on black holes.

**Note:** These instructions are valid for Linux and MacOS based machines. This app has **not** been tested or evaluated
on
Windows based machines.

## Pre-reqs

- [Python 3.14+](https://www.python.org/downloads/release/python-3140/)
- [uv](https://docs.astral.sh/uv/) (recommended)

## Setup

Clone the repository and move to the directory:

- `git clone https://github.com/firephreek/bangertools`
- `cd bangertools`

If `uv` is not available in your environment, you can run

- `pip install -r requirements.txt`

Otherwise, if uv is installed, you can run the following:

- `uv sync`

## Build

If `uv` is installed, you can activate your environment using `source .venv/bin/activate` from your
project root directory. Once active, `uv build` will build and 'install' the tool allowing you to simply execute
`banger` to run the application. If developing new features or working with the code, changes should be picked up
automatically meaning `uv build` will *not* need to be run to incorporate those changes into your version of the tool
in your environment. Note however, that `banger` will only be available when you are actively in your uv environment.

To exit your uv virtual environment, simply run `deactivate`. You can always use `which python3` to verify which
python interpreter is currently being used in your environment.

## Usage

Regardless if uv was used to build the project or not the first run may take a few minutes to start while packages are
loading. If uv *was* used to build the app, it should be available by just running `banger`. Otherwise, use will
need to run `python3 path/to/main.py`. In either case, passing `--help` will show a list of commands and their
descriptions


