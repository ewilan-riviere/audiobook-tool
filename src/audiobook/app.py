"""audiobook-tool main"""

import argparse
import sys
import logging
from audiobook.args import AudiobookArgs
from audiobook.env import python_check
from .command import (
    # CommandAudible,
    # CommandBuild,
    # CommandClean,
    # CommandExtract,
    # CommandForge,
    # CommandFusion,
    CommandParse,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


def main() -> None:
    """audiobook-tool main"""
    parser = argparse.ArgumentParser(
        prog="audiobook-tool",
        description="CLI to handle audiobooks",
    )

    args = AudiobookArgs(parser)
    python_check()

    print(parser.prog)
    print(parser.description)
    print(f"Execute command {args.command}...\n")

    try:
        if args.command == "parse":
            CommandParse(args)
        # if args.command == "audible":
        #     CommandAudible(args)
        # elif args.command == "build":
        #     CommandBuild(args)
        # elif args.command == "clean":
        #     CommandClean(args)
        # elif args.command == "extract":
        #     CommandExtract(args)
        # elif args.command == "forge":
        #     CommandForge(args)
        # elif args.command == "fusion":
        #     CommandFusion(args)
        # elif args.command == "parse":
        #     CommandParse(args)
    except Exception as e:  # pylint: disable=broad-exception-caught
        logging.getLogger("audiobook.cli").error("Error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
