import argparse
import logging
import json
from audiobook.args import AudiobookArgs
from audiobook.package import AudiobookForge
from .m4b import M4bSplit, chapter_print, M4bChapters, M4bTagger
from audiobook.metadata import MetadataLoader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


def main() -> None:
    print("audiobook-tool")
    parser = argparse.ArgumentParser(prog="audiobook-tool")
    args = AudiobookArgs(parser)

    forge = AudiobookForge(args.mp3_directory).execute()
    chapters = M4bChapters(forge.m4b_file).get_chapters()
    # for chapter in chapters:
    #     chapter_print(chapter)
    loader = MetadataLoader(args.mp3_directory)
    # print(loader)

    split = M4bSplit(forge.m4b_file, chapters)
    # print(json.dumps(split.get_split_plan(), indent=4, ensure_ascii=False))
    parts = split.run()

    tagger = M4bTagger(parts, loader.metadata)
    tagger.run()
    # split.execute()

    # os.remove(forge.m4b_file)


if __name__ == "__main__":
    main()
