import getopt
import sys

from diffpy.cmi.version import __version__


def usage():
    """Print short help message."""
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
    -V, --version     Show version and exit
    -h, --help        Show this message and exit
"""
    )


def version():
    print(f"diffpy-cmi {__version__}")


def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "hV", ["help", "version"])
    except getopt.GetoptError as err:
        print(f"Error: {err}", file=sys.stderr)
        usage()
        sys.exit(1)

    for opt, _ in opts:
        if opt in ("-h", "--help"):
            usage()
            return
        elif opt in ("-V", "--version"):
            version()
            return

    # Default behavior (if no arguments)
    usage()


if __name__ == "__main__":
    main()
