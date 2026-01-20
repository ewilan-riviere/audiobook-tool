from argparse import ArgumentParser, Namespace
from typing import Optional


class AudiobookArgs:
    """CLI args for audiobook-tool"""

    def __init__(self, parser: ArgumentParser):
        subparsers = parser.add_subparsers(dest="command", required=True)

        # Audible
        m_audible = subparsers.add_parser(
            "audible", help="Fetch Audible to get metadata"
        )
        m_audible.add_argument(
            "asin",
            help="ASIN of Audible book like `B008Y43GBY` (available in Audible book's URL)",
        )

        # Build
        m_build = subparsers.add_parser(
            "build", help="Build MP3 files to M4B (include forge command)"
        )
        m_build.add_argument("mp3_directory", help="Source directory")
        m_build.add_argument(
            "-c",
            "--clear",
            action="store_true",
            help="Clear old M4B audiobook if present.",
        )
        m_build.add_argument(
            "-r",
            "--rust",
            action="store_true",
            help="Use Rust with audiobook-forge crate to forge M4B",
        )
        m_build.add_argument("-o", "--output")

        # Clean
        m_clean = subparsers.add_parser("clean", help="Clean MP3 files from silences")
        m_clean.add_argument("mp3_directory", help="Source directory")

        # Extract
        m_extract = subparsers.add_parser("extract", help="Extract MP3 files from M4B")
        m_extract.add_argument("m4b_directory", help="Source directory")

        # Forge
        m_forge = subparsers.add_parser("forge", help="Forge MP3 file to M4B")
        m_forge.add_argument("mp3_directory", help="Source directory")

        # Fusion
        m_fusion = subparsers.add_parser("fusion", help="Add MP3 files to existing M4B")
        m_fusion.add_argument(
            "m4b_directory", help="Directory with current audiobook (multiparts)"
        )
        m_fusion.add_argument("mp3_directory", help="Directory with new chapters")

        args: Namespace = parser.parse_args()
        self.command: str = args.command

        self.mp3_directory: Optional[str] = getattr(args, "mp3_directory", None)
        self.m4b_output: Optional[str] = getattr(args, "output", None)
        self.clear_old_m4b: bool = getattr(args, "clear", False)
        self.use_rust: bool = getattr(args, "rust", False)
        self.m4b_directory: Optional[str] = getattr(args, "m4b_directory", None)
        self.asin: Optional[str] = getattr(args, "asin", None)

        if self.command in ["audible"] and self.asin is None:
            parser.error(
                f"L'argument 'asin' est requis pour la commande {self.command}"
            )

        if (
            self.command in ["build", "clean", "forge", "fusion"]
            and self.mp3_directory is None
        ):
            parser.error(
                f"L'argument 'mp3_directory' est requis pour la commande {self.command}"
            )

        if self.command in ["extract"] and self.m4b_directory is None:
            parser.error(
                f"L'argument 'm4b_directory' est requis pour la commande {self.command}"
            )

        if self.command in ["fusion"] and self.mp3_directory is None:
            parser.error(
                f"L'argument 'mp3_directory' est requis pour la commande {self.command}"
            )
