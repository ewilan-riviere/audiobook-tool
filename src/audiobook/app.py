"""main script of audiobook-tool"""

import argparse
import sys
import logging
from .args import AudiobookArgs
from .command import CommandBuild, CommandClean, CommandFusion

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


def main() -> None:
    """audiobook-tool main def"""
    print("audiobook-tool")
    parser = argparse.ArgumentParser(prog="audiobook-tool")
    args = AudiobookArgs(parser)
    print(args.command)

    try:
        if args.command == "build":
            CommandBuild(args)
        elif args.command == "clean":
            CommandClean(args)
        elif args.command == "fusion":
            CommandFusion(args)
    except Exception as e:
        logging.getLogger("audiobook.cli").error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
