import getopt
import sys


def usage():
    """Print short help message."""
    print(
        """\
diffpy.cmi – Complex Modeling Infrastructure

DiffPy-CMI is our complex modeling framework. It is a highly flexible library
of Python modules for robust modeling of nanostructures in crystals,
nanomaterials, and amorphous materials.

Docs: https://www.diffpy.org/diffpy.cmi

Usage:
    diffpy-cmi [--version] [--help]

Options:
    -V, --version     Show version and exit
    -h, --help        Show this message and exit
"""
    )


def version():
    from diffpy.cmi.version import __version__

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
