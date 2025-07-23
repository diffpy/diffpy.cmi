import argparse

from diffpy.cmi.version import __version__


def main():
    parser = argparse.ArgumentParser(
        prog="diffpy-cmi",
        description=(
            "Welcome to diffpy-CMI, a complex modeling infrastructure "
            "for multi-modal analysis of scientific data.\n\n"
            "Docs: https://www.diffpy.org/diffpy.cmi"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show the program's version number and exit",
    )
    args = parser.parse_args()
    if args.version:
        print(f"diffpy.cmi {__version__}")
    else:
        # Default behavior when no arguments are given
        parser.print_help()


if __name__ == "__main__":
    main()
