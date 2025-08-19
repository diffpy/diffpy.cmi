#!/usr/bin/env python
##############################################################################
#
# (c) 2025 The Trustees of Columbia University in the City of New York.
# All rights reserved.
#
# File coded by: Tieqiong Zhang and members of the Billinge Group.
#
# See GitHub contributions for a more detailed list of contributors.
# https://github.com/diffpy/diffpy.cmi/graphs/contributors
#
# See LICENSE.rst for license information.
#
##############################################################################
"""Centralized logging utilities for the CMI package.

This module exposes a single package logger :data:`plog` and helpers to
switch between a concise *user* mode and a verbose *debug* mode.

Modes
-----
user
    Only ``INFO`` and ``ERROR/CRITICAL`` records are shown. ``WARNING`` and
    ``DEBUG`` are hidden.
debug
    All levels are shown.

Notes
-----
Use :func:`set_log_mode` in the CLI to toggle visibility. The logger itself
always emits at ``DEBUG`` level; a handler-side filter controls what is shown.
"""

import logging

__all__ = ["plog", "set_log_mode", "get_log_mode", "is_debug"]

# Package logger
plog = logging.getLogger("diffpy.cmi")


class _AllowLevels(logging.Filter):
    """Filter that allows only a chosen set of levels."""

    def __init__(self, *levels: int):
        super().__init__()
        self._allowed = set(levels)

    def set_allowed(self, *levels: int) -> None:
        """Set the allowed levels for this filter."""
        self._allowed = set(levels)

    def filter(self, record: logging.LogRecord) -> bool:
        """Return True if the record's level is allowed."""
        return (not self._allowed) or (record.levelno in self._allowed)


# Global mode flag
_mode: str = "user"

# Configure a default handler on first import
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
plog.setLevel(
    logging.DEBUG
)  # logger always emits; filter/handler decide visibility
plog.propagate = False
plog.handlers.clear()
plog.addHandler(_handler)

# In user mode, suppress WARNING/DEBUG; in debug mode, show everything
_plog_filter = _AllowLevels(logging.INFO, logging.ERROR, logging.CRITICAL)
_handler.addFilter(_plog_filter)


def set_log_mode(mode: "str | bool" = "user") -> None:
    """Set visible logging mode.

    Parameters
    ----------
    mode : {"user","debug"} or bool, optional
        - ``"user"`` (``False``): ``INFO`` and ``ERROR`` are visible
        - ``"debug"`` (``True``): all levels visible.
    """
    global _mode
    if isinstance(mode, bool):
        m = "debug" if mode else "user"
    elif isinstance(mode, str):
        m = (mode or "user").strip().lower()
    else:
        m = "user"
    if m not in {"user", "debug"}:
        m = "user"
    if m == "debug":
        _plog_filter.set_allowed()
        _mode = "debug"
        plog.debug("log mode set to debug")
    else:
        _plog_filter.set_allowed(logging.INFO, logging.ERROR, logging.CRITICAL)
        _mode = "user"


def get_log_mode() -> str:
    """Return ``"user"`` or ``"debug"``."""
    return _mode


def is_debug() -> bool:
    """Return ``True`` when debug/verbose mode is active."""
    return _mode == "debug"
