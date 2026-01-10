import argparse

# import sys
import logging

# from audiobook.core import AudiobookMerge
from audiobook.package import AudiobookForge
from audiobook.metadata import SplitM4b

# from .core import Processor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


def main() -> None:
    parser = argparse.ArgumentParser(prog="audiobook-tool")
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
    # proc = Processor()

    mp3_directory: str = args.dir
    m4b_output: str = args.output

    # AudiobookMerge(args.dir, args.output)
    forge = AudiobookForge(mp3_directory)
    forge.execute()
    print(forge.m4b_file)
    print(forge.size_human)

    split = SplitM4b(forge.m4b_file)
    split.execute()

    # try:
    #     if args.command == "merge":
    #         proc.merge(args.dir, args.output)
    #     elif args.command == "split":
    #         proc.split_by_size(args.input, args.min, args.max, args.output_dir)
    # except Exception as e:
    #     logging.getLogger("audiobook.cli").error(f"Error: {e}")
    #     sys.exit(1)


if __name__ == "__main__":
    main()
