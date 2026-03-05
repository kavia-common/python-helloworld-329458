"""Logging utilities for the helloworld package.

This module defines a small, reusable logging configuration flow that can be used by:
- The console_script entrypoint (helloworld.main)
- The repo root script (helloworld.py)
- Any future modules needing consistent logging behavior

Design goals:
- Keep configuration at the boundary (CLI) rather than deep modules.
- Provide deterministic, debuggable output with consistent formatting.
- Avoid one-off logging setup scattered across call sites.
"""

from __future__ import annotations

import logging
import os
from typing import Optional


_LOGGER_NAME = "helloworld"


def _parse_log_level(value: str) -> int:
    """Parse a log level string into a logging module level.

    Accepts common names (DEBUG, INFO, WARNING, ERROR, CRITICAL) and is case-insensitive.
    Raises ValueError for unknown values so the boundary can report a clear message.
    """
    normalized = value.strip().upper()
    mapping = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "WARN": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
    }
    if normalized not in mapping:
        raise ValueError(
            f"Unsupported log level {value!r}. "
            "Use one of: DEBUG, INFO, WARNING, ERROR, CRITICAL."
        )
    return mapping[normalized]


# PUBLIC_INTERFACE
def configure_logging(
    *,
    verbose: bool = False,
    log_level: Optional[str] = None,
) -> logging.Logger:
    """Configure package logging and return the package logger.

    Contract:
      Inputs:
        - verbose: If True, set log level to DEBUG (unless overridden by log_level).
        - log_level: Optional explicit log level string. If omitted, will use:
            1) HELLOWORLD_LOG_LEVEL env var, else
            2) DEBUG if verbose, else INFO
      Outputs:
        - Returns the canonical `logging.Logger` for the package ("helloworld").
      Errors:
        - Raises ValueError if a provided/derived log_level is invalid.
      Side effects:
        - Configures the root logging system via `logging.basicConfig(...)` if it has not
          already been configured by the host application.
        - Sets this package logger level and ensures it propagates to root handlers.

    Notes:
      - We use a stable, readable format suitable for CLI output.
      - We avoid adding handlers directly to the package logger; instead we rely on root
        handlers to keep behavior consistent for embedding applications.
    """
    # Derive level preference: explicit argument > env var > verbose > default.
    env_level = os.getenv("HELLOWORLD_LOG_LEVEL")
    chosen_level_str = log_level or env_level
    if chosen_level_str is not None:
        level = _parse_log_level(chosen_level_str)
    else:
        level = logging.DEBUG if verbose else logging.INFO

    # basicConfig is a no-op if handlers are already configured on the root logger.
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = True

    logger.debug(
        "Logging configured",
        extra={
            "verbose": verbose,
            "log_level": chosen_level_str or logging.getLevelName(level),
            "env_HELLOWORLD_LOG_LEVEL": env_level,
        },
    )
    return logger
