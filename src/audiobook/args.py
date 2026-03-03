"""CLI args for audiobook-tool"""

from argparse import ArgumentParser, Namespace
from typing import Optional
from pathlib import Path
from audiobook.common import AutoRepr


class AudiobookArgs(AutoRepr):
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
        m_audible.add_argument(
            "-l",
            "--locale",
            help="Audiobook locale for Audible (can be `com`, `co.uk`, `fr`, `de`)",
        )
        m_audible.add_argument(
            "-c",
            "--cover",
            action="store_true",
            help="Save cover locally",
        )

        # Build
        m_build = subparsers.add_parser(
            "build", help="Build MP3 files to M4B (include forge command)"
        )
        m_build.add_argument("source_directory", help="Source directory")
        m_build.add_argument(
            "-c",
            "--clear",
            action="store_true",
            help="Clear old M4B audiobook if present, remove MP3 covers too",
        )
        m_build.add_argument(
            "-a",
            "--asin",
            help="Fetch metadata from Audible",
        )
        m_build.add_argument(
            "-l",
            "--locale",
            help="Audiobook locale for Audible (can be `com`, `co.uk`, `fr`, `de`)",
        )
        m_build.add_argument(
            "-o",
            "--output-path",
            help="Specify a path to save the M4B file (default is same as MP3 source)",
        )
        m_build.add_argument(
            "-s",
            "--structured",
            action="store_true",
            help="Store audiobook with template: `author/series/series.volume.title/audiobook.m4b`",
        )
        m_build.add_argument(
            "-u",
            "--unified",
            action="store_true",
            help="Skip splitting M4B into mutliple parts",
        )
        m_build.add_argument(
            "-p",
            "--part-size",
            help="Size in MB of each part (can be set into `.env` for global settings)",
        )

        # Clean
        m_clean = subparsers.add_parser("clean", help="Clean MP3 files from silences")
        m_clean.add_argument("source_directory", help="Source directory")

        # Extract
        m_extract = subparsers.add_parser("extract", help="Extract MP3 files from M4B")
        m_extract.add_argument("m4b_directory", help="Source directory")
        m_extract.add_argument(
            "-t",
            "--type",
            help="Specify an audio type: `mp3` or `m4a` (default is `m4a`)",
        )

        # Forge
        m_forge = subparsers.add_parser(
            "forge",
            help="Forge MP3 file to unified M4B (use `build` command for full features)",
        )
        m_forge.add_argument("source_directory", help="Source directory")
        m_forge.add_argument(
            "-o",
            "--output-path",
            help="Specify a path to save the M4B file (default is same as MP3 source)",
        )

        # Fusion
        m_fusion = subparsers.add_parser("fusion", help="Add MP3 files to existing M4B")
        m_fusion.add_argument(
            "audiobook_directory",
            help="Directory with current audiobook, if audiobook as only one part use parent directory",
        )
        m_fusion.add_argument(
            "source_directory", help="Directory with new chapters as MP3/M4A"
        )

        # Parse
        m_parse = subparsers.add_parser(
            "parse", help="Parse audio file to get metadata"
        )
        m_parse.add_argument(
            "audio_to_parse",
            help="Path of audio file",
        )

        args: Namespace = parser.parse_args()
        self.command: str = args.command

        # path
        self.source_directory: Optional[str] = getattr(args, "source_directory", None)
        self.output_path: Optional[str] = getattr(args, "output_path", None)
        self.m4b_directory: Optional[str] = getattr(args, "m4b_directory", None)
        self.audio_to_parse: Optional[str] = getattr(args, "audio_to_parse", None)

        # bool
        self.clear: bool = getattr(args, "clear", False)
        self.structured: bool = getattr(args, "structured", False)
        self.unified: bool = getattr(args, "unified", False)
        self.cover: bool = getattr(args, "cover", False)

        # misc
        self.asin: Optional[str] = getattr(args, "asin", None)
        self.locale: Optional[str] = getattr(args, "locale", None)
        self.part_size: Optional[int] = getattr(args, "part_size", None)
        self.audio_type: Optional[str] = getattr(args, "type", None)

        if self.source_directory:
            self.source_directory = self._path_absolute(self.source_directory)
        if self.output_path:
            self.output_path = self._path_absolute(self.output_path)
        if self.m4b_directory:
            self.m4b_directory = self._path_absolute(self.m4b_directory)
        if self.audio_to_parse:
            self.audio_to_parse = self._path_absolute(self.audio_to_parse)

        if self.command in ["audible"] and self.asin is None:
            parser.error(
                f"L'argument 'asin' est requis pour la commande {self.command}"
            )

        if (
            self.command in ["build", "clean", "forge", "fusion"]
            and self.source_directory is None
        ):
            parser.error(
                f"L'argument 'source_directory' est requis pour la commande {self.command}"
            )

        if self.command in ["extract"] and self.m4b_directory is None:
            parser.error(
                f"L'argument 'm4b_directory' est requis pour la commande {self.command}"
            )

        if self.command in ["fusion"] and self.source_directory is None:
            parser.error(
                f"L'argument 'source_directory' est requis pour la commande {self.command}"
            )

    def _path_absolute(self, path: str) -> str:
        return str(Path(path).resolve())
