"""CLI implementation of the helloworld program.

This module intentionally separates:
- Boundary concerns: argv parsing, logging configuration, exit-code mapping
- Flow concerns: a reusable 'HelloWorldFlow' that performs the program's work

This structure keeps the behavior easy to extend and debug over time.
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from typing import Optional, Sequence

import helloworld
from helloworld.logging_utils import configure_logging


@dataclass(frozen=True)
class HelloWorldRequest:
    """Validated inputs for the HelloWorld flow."""

    # Today the flow has no behavioral inputs besides logging/observability settings,
    # but this request object creates a stable extension point for future flags.
    pass


@dataclass(frozen=True)
class HelloWorldResult:
    """Result object for the HelloWorld flow.

    Attributes:
      message: The greeting printed to stdout.
    """

    message: str


def _build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser (kept in a function for testability/reuse)."""
    parser = argparse.ArgumentParser(
        description="A simple example program to print a friendly greeting."
    )
    parser.add_argument(
        "--version",
        action="version",
        version="helloworld " + helloworld.__version__,
        help="Show the package version and exit.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging (equivalent to --log-level DEBUG).",
    )
    parser.add_argument(
        "--log-level",
        default=None,
        help=(
            "Set the logging level for the CLI. "
            "Allowed: DEBUG, INFO, WARNING, ERROR, CRITICAL. "
            "Overrides HELLOWORLD_LOG_LEVEL."
        ),
    )
    return parser


def _run_hello_world_flow(*, logger: logging.Logger, request: HelloWorldRequest) -> HelloWorldResult:
    """Run the reusable HelloWorld flow.

    Contract:
      Inputs:
        - logger: A configured logger for observability.
        - request: Validated request data (currently empty).
      Outputs:
        - HelloWorldResult with the greeting message.
      Errors:
        - May raise unexpected exceptions; these should be caught at the CLI boundary.
      Side effects:
        - Prints a greeting to stdout.
    """
    _ = request  # reserved for future use
    message = "Hello, world"
    print(message)
    return HelloWorldResult(message=message)


# PUBLIC_INTERFACE
def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entrypoint for the `helloworld_in_python` console script.

    Contract:
      Inputs:
        - argv: full argv list (including program name). If None, uses sys.argv.
      Outputs:
        - Exit code integer. 0 on success, 2 on invalid arguments, 1 on unexpected errors.
      Errors:
        - Does not raise (acts as a boundary); unexpected errors are logged and mapped to exit code 1.
      Side effects:
        - Configures logging, parses CLI args, prints greeting, logs execution summary.
    """
    if argv is None:
        argv = sys.argv

    parser = _build_parser()

    try:
        args = parser.parse_args(list(argv)[1:])
    except SystemExit as e:
        # argparse uses SystemExit(2) for invalid args; keep standard CLI behavior.
        return int(e.code) if isinstance(e.code, int) else 2

    try:
        logger = configure_logging(verbose=bool(args.verbose), log_level=args.log_level)
    except ValueError as e:
        # Invalid log level string (either from --log-level or env var)
        sys.stderr.write(f"error: {e}\n")
        return 2

    logger.info(
        "HelloWorldFlow start",
        extra={
            "argv_len": len(list(argv)),
            "version": helloworld.__version__,
        },
    )

    try:
        request = HelloWorldRequest()
        result = _run_hello_world_flow(logger=logger, request=request)
    except Exception:
        logger.exception("HelloWorldFlow failed")
        return 1

    logger.info("HelloWorldFlow success", extra={"message": result.message})
    return 0
