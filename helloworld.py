#!/usr/bin/env python

"""Top-level script to invoke the helloworld CLI implementation.

This file supports running the project without installation:
    python helloworld.py [--verbose] [--log-level INFO] [--version]

It intentionally delegates all behavior (including logging) to `helloworld.main:main`
to keep a single canonical runtime flow.
"""

import sys

import helloworld.main


if __name__ == "__main__":
    sys.exit(helloworld.main.main())
