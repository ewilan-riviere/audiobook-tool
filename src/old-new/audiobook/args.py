from argparse import ArgumentParser


class AudiobookArgs:
    def __init__(self, parser: ArgumentParser):
        subparsers = parser.add_subparsers(dest="command", required=True)

        # Merge
        m = subparsers.add_parser("merge", help="Merge MP3s to M4B")
        m.add_argument("dir", help="Source directory")
        m.add_argument("-o", "--output", help="Output file path")

        # Split
        s = subparsers.add_parser("split", help="Split M4B by chapters")
        s.add_argument("input", help="M4B file to split")
        s.add_argument("-o", "--output-dir", help="Target directory")
        s.add_argument("--min", type=int, default=400)
        s.add_argument("--max", type=int, default=600)

        args = parser.parse_args()

        self.mp3_directory: str = args.dir
        self.m4b_output: str | None = args.output
