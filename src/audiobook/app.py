"""audiobook-tool main"""

import argparse
import sys
import logging
import importlib_metadata
from audiobook.args import AudiobookArgs
from audiobook.env import python_check, LOGGER_LEVEL
from .command import (
    CommandAudible,
    CommandBuild,
    # CommandClean,
    CommandExtract,
    CommandForge,
    CommandFusion,
    CommandParse,
    CommandTemplate,
)


logging.basicConfig(
    level=LOGGER_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


def main() -> None:
    """audiobook-tool main"""
    version = importlib_metadata.version("audiobook-cli")
    parser = argparse.ArgumentParser(
        prog="audiobook-tool",
        description=f"Ultimate Python CLI to handle audiobooks, v{version}",
    )

    args = AudiobookArgs(parser)
    python_check()

    try:
        if args.command == "parse":
            CommandParse(args)
        elif args.command == "audible":
            CommandAudible(args)
        elif args.command == "build":
            CommandBuild(args)
        elif args.command == "clean":
            raise Exception("clean is not implemented yet")
            # CommandClean(args)
        elif args.command == "extract":
            CommandExtract(args)
        elif args.command == "forge":
            CommandForge(args)
        elif args.command == "fusion":
            CommandFusion(args)
        elif args.command == "parse":
            CommandParse(args)
        elif args.command == "template":
            CommandTemplate(args)
    except Exception as e:  # pylint: disable=broad-exception-caught
        logging.getLogger("audiobook.cli").error("Error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
