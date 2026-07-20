"""Application entry point for the Medieval Village Simulation.

This module is the outermost layer of the application. Its only responsibilities
are to:

1. Parse command-line arguments.
2. Delegate dependency wiring to the composition root (:mod:`core.bootstrap`).
3. Start the simulation/rendering loop (:mod:`core.engine`).

It deliberately contains **no** simulation logic. All domain behavior lives in
the dedicated packages (``agents``, ``world``, ``ai``, ``economy`` ...).

Run with::

    python main.py
"""

from __future__ import annotations

import argparse
import sys

# NOTE: Imports are kept local to :func:`main` where practical so that importing
# this module for testing/tooling stays cheap and side-effect free.


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Optional argument vector (defaults to ``sys.argv``).

    Returns:
        The parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        prog="medieval-village",
        description="Run the Medieval Village Simulation.",
    )
    # TODO: Add real CLI options (e.g. --headless, --steps, --seed, --config).
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without the Pygame rendering layer.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Bootstrap and run the application.

    Args:
        argv: Optional argument vector (defaults to ``sys.argv``).

    Returns:
        A process exit code (``0`` on success).
    """
    args = parse_args(argv)

    # Imports deferred so importing this module for tooling stays side-effect free.
    from config.settings import get_settings  # noqa: PLC0415
    from core.bootstrap import bootstrap  # noqa: PLC0415

    application = bootstrap(headless=args.headless)
    application.engine.run(get_settings().max_steps)

    return 0


if __name__ == "__main__":
    sys.exit(main())
