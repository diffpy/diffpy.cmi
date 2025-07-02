import argparse
import sys

from diffpy.cmi.version import __version__


def usage():
    """Print full help message."""
    print(
        """\

Welcome to diffpy-CMI, a complex modeling infrastructure
designed for multi-modal analysis of scientific data.
While broadly applicable to a wide range of problems,
including those beyond materials science, diffpy-CMI currently
provides robust tools for modeling atomic structure based on
Pair Distribution Function (PDF) and Small-Angle Scattering (SAS) data.
Its modular Python architecture enables extensible workflows,
with additional capabilities continually being developed.

Docs: https://www.diffpy.org/diffpy.cmi

Usage:
    diffpy-cmi [--version] [--help]

Options:
    --version         Show version and exit
    -h, --help        Show this message and exit
"""
    )


def short_usage():
    """Print brief usage message for invalid input."""
    print(
        "Usage: diffpy-cmi [--version] [--help]\nUse --help to see more.",
        file=sys.stderr,
    )


def print_version():
    print(f"diffpy-cmi {__version__}")


def main():
    parser = argparse.ArgumentParser(
        prog="diffpy-cmi",
        add_help=False,
    )
    parser.add_argument(
        "--version", action="store_true", help="Show version and exit"
    )
    parser.add_argument(
        "-h", "--help", action="store_true", help="Show this message and exit"
    )
    args, unknown = parser.parse_known_args()
    if unknown:
        print(
            f"Error: unrecognized arguments: {' '.join(unknown)}",
            file=sys.stderr,
        )
        short_usage()
        sys.exit(1)
    if args.help:
        usage()
        return
    if args.version:
        print_version()
        return
    # Default behavior (no args)
    usage()


if __name__ == "__main__":
    main()
