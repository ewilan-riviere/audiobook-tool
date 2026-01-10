from typing import List, Tuple, Optional
import logging
import glob
import os
from audiobook.utils import FFmpegWrapper, natural_sort_key
from audiobook.metadata.loader import MetadataLoader
from audiobook.ffmpeg import FfmpegConverter, M4bCompiler
from audiobook.ffmpeg.builder import AudiobookBuilder

logger = logging.getLogger("audiobook.core")


class AudiobookMerge:
    def __init__(self, directory: str, output_path: Optional[str] = None):
        self.directory = directory
        self.output_path = output_path
        self.files: list[str] = []
        self.chapters: List[Tuple[str, float]] = []
        self.cover = None

        self.__handle_path()
        builder = AudiobookBuilder(self.files)
        builder.build()
        print("Fichier final M4B :", builder.m4b_file)

        # self.__handle_chapters()
        # self.__handle_metadata()
        # self.__handle_covers()
        # self.__handle_files()

    def __handle_path(self):
        logger.info("Analyzing folder: %s", self.directory)
        self.files = sorted(
            glob.glob(os.path.join(self.directory, "*.mp3")), key=natural_sort_key
        )

        if not self.files:
            raise FileNotFoundError(f"No MP3 files in {self.directory}")

        if not self.output_path:
            self.output_path = f"{os.path.basename(self.directory.rstrip(os.sep))}.m4b"

        if os.path.dirname(self.output_path):
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

    def __handle_chapters(self):
        temp_chapters = "temp_chapters.txt"

        with open(temp_chapters, "w", encoding="utf-8") as f:
            for file in self.files:
                info = FFmpegWrapper.get_info(file)
                duration = float(info["format"]["duration"])
                title = os.path.splitext(os.path.basename(file))[0]
                self.chapters.append((title, duration))
                safe_path = os.path.abspath(file).replace("'", "'\\''")
                f.write(f"file '{safe_path}'\n")

    def __handle_metadata(self):
        MetadataLoader(self.directory, self.chapters)
        # print(loader.ffmpeg)
        # meta_content = MetadataManager.create_ffmpeg_meta_file(
        #     meta_data, chapters, directory
        # )
        # temp_meta = "temp_meta.txt"

        # with open(temp_meta, "w", encoding="utf-8") as f:
        #     f.write(meta_content)
        return self

    def __handle_covers(self):
        self.cover = next(
            (
                os.path.join(self.directory, f"cover.{ext}")
                for ext in ["jpg", "png", "jpeg"]
                if os.path.exists(os.path.join(self.directory, f"cover.{ext}"))
            ),
            None,
        )

    def __handle_files(self):
        converter = FfmpegConverter(self.files)
        converter.convert_all()

        compiler = M4bCompiler(converter.m4b_files)
        compiler.compile()
