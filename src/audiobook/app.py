import argparse
import logging
from audiobook.args import AudiobookArgs
from audiobook.package import AudiobookForge
from audiobook.core import SplitM4b, MetadataLoader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


def main() -> None:
    parser = argparse.ArgumentParser(prog="audiobook-tool")
    args = AudiobookArgs(parser)

    forge = AudiobookForge(args.mp3_directory)
    loader = MetadataLoader(args.mp3_directory)

    forge.execute()
    print(forge.m4b_file)
    print(forge.size_human)

    split = SplitM4b(forge.m4b_file, loader.metadata)
    split.execute()


if __name__ == "__main__":
    main()
