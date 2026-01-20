"""audiobook-tool main"""

import argparse
import sys
import logging
from .args import AudiobookArgs
from .command import (
    CommandBuild,
    CommandClean,
    CommandExtract,
    CommandForge,
    CommandFusion,
)
from .env import python_check

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

    print(f"Execute command {args.command}...\n")

    try:
        if args.command == "build":
            CommandBuild(args)
        elif args.command == "clean":
            CommandClean(args)
        elif args.command == "extract":
            CommandExtract(args)
        elif args.command == "forge":
            CommandForge(args)
        elif args.command == "fusion":
            CommandFusion(args)
    except Exception as e:
        logging.getLogger("audiobook.cli").error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
