from argparse import ArgumentParser, Namespace
from typing import Optional


class AudiobookArgs:
    """CLI args for audiobook-tool"""

    def __init__(self, parser: ArgumentParser):
        subparsers = parser.add_subparsers(dest="command", required=True)

        # Build
        m_build = subparsers.add_parser("build", help="Build MP3s to M4B")
        m_build.add_argument("dir", help="Source directory")
        m_build.add_argument("-c", "--clear", action="store_true")
        m_build.add_argument("-o", "--output")

        # Clean
        m_clean = subparsers.add_parser("clean", help="Clean MP3s")
        m_clean.add_argument("dir", help="Source directory")

        args: Namespace = parser.parse_args()
        self.command: str = args.command

        self.mp3_directory: Optional[str] = getattr(args, "dir", None)
        self.m4b_output: Optional[str] = getattr(args, "output", None)
        self.clear_old_m4b: bool = getattr(args, "clear", False)

        if self.command in ["build", "clean"] and self.mp3_directory is None:
            parser.error(f"L'argument 'dir' est requis pour la commande {self.command}")
