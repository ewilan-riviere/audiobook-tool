"""Compile MP3 files into M4B"""

import os
from pathlib import Path
from concurrent.futures import as_completed, Future
from concurrent.futures.process import ProcessPoolExecutor
from audiobook.audio import AudioReader
from audiobook.common import AutoRepr
import audiobook.utils as utils
from .modules import BlacksmithChapter, BlacksmithRunner, BlacksmithFixer


class AudiobookBlacksmith(AutoRepr):
    """Compile MP3 files into M4B"""

    def __init__(self, directory_path: str):
        self.directory = Path(directory_path).resolve()
        self.mp3_files: list[Path] = []
        self.chapters: list[BlacksmithChapter] = []
        self.target_bitrate: str = "128k"
        self.output_path = Path(
            utils.path_join(self.directory, f"{self.directory.name}.m4b")
        )
        self.metadata_txt = Path(utils.path_join(self.directory, "metadata.txt"))
        self.inputs_txt = Path(utils.path_join(self.directory, "inputs.txt"))

        if Path(self.output_path).exists():
            os.remove(self.output_path)

        self._prepare_data()

    def _prepare_data(self) -> None:
        """Initializes the chapter list, calculates the bitrate, and extracts titles from tags."""
        self.mp3_files = utils.get_files_path(self.directory, "mp3")
        if not self.mp3_files:
            raise FileNotFoundError(f"No MP3 files found into {self.directory}")

        total_bitrate: int = 0
        file_count = len(self.mp3_files)

        for mp3 in self.mp3_files:
            reader = AudioReader(mp3)
            mp3_bitrate = reader.properties.bit_rate or 128000
            total_bitrate += mp3_bitrate

            title_tag = (reader.tags.title or "Unknown").strip()
            chapter_title = title_tag
            if reader.tags.chapters:
                chapter_title = (reader.tags.chapters[0].title or title_tag).strip()
            if not chapter_title:
                chapter_title = reader.container.basename

            chapter = BlacksmithChapter(
                source_path=mp3,
                temp_aac_path=mp3.with_suffix(".m4a"),
                title=chapter_title,
                duration_ms=reader.properties.duration_ms,
            )
            self.chapters.append(chapter)

        # avg_bitrate = int(total_bitrate / file_count)
        avg_bitrate = min(int(total_bitrate / file_count), 192000)
        self.target_bitrate = f"{int(avg_bitrate / 1000)}k"

        print(f"🔍 Analyze: {file_count} files. Average bitrate: {self.target_bitrate}")

    def _write_assets(self) -> None:
        """Generates metadata based on the actual duration of encoded files"""
        metadata_lines = [";FFMETADATA1"]
        current_time_ms = 0

        with open(self.inputs_txt, "w", encoding="utf-8") as f_list:
            for chapter in self.chapters:
                # 💡 CALCULER LA DURÉE SUR LE FICHIER AAC TEMP, PAS LE MP3
                # Le format AAC/ADTS n'a pas toujours de header de durée
                reader = AudioReader(chapter.temp_aac_path)
                metadata_lines.append(
                    f"\n[CHAPTER]\nTIMEBASE=1/1000\nSTART={current_time_ms}"
                )
                current_time_ms += reader.properties.duration_ms
                metadata_lines.append(f"END={current_time_ms}\ntitle={chapter.title}")
                escaped_name = chapter.temp_aac_path.name.replace("'", "'\\''")
                f_list.write(f"file '{escaped_name}'\n")

        self.metadata_txt.write_text("\n".join(metadata_lines), encoding="utf-8")

    def _cleanup(self) -> None:
        """Clean temporary files"""
        for path in [self.metadata_txt, self.inputs_txt]:
            if path.exists():
                path.unlink()
        for chap in self.chapters:
            if chap.temp_aac_path.exists():
                chap.temp_aac_path.unlink()

    def process(self) -> None:
        """Start parallel encoding and final merging."""
        try:
            total = len(self.chapters)
            print(f"🚀 Encoding of {total} files on {os.cpu_count()} cores...")

            future_to_file: dict[Future[str], str] = {}

            with ProcessPoolExecutor() as executor:
                for c in self.chapters:
                    future = executor.submit(
                        BlacksmithRunner.encode_to_aac,
                        c.source_path,
                        c.temp_aac_path,
                        self.target_bitrate,
                    )
                    future_to_file[future] = c.source_path.name

                # Suivi de l'avancement en temps réel
                completed = 0
                for future in as_completed(future_to_file):
                    filename = future_to_file[future]
                    try:
                        future.result()
                        completed += 1
                        print(f"  ✅ [{completed}/{total}] Done: {filename}")
                    except Exception as e:
                        print(f"  ❌ Error on {filename}: {e}")
                        raise

            print("📦 Final merger and creation of chapters...")
            self._write_assets()
            BlacksmithRunner.merge_to_m4b(
                self.inputs_txt,
                self.metadata_txt,
                self.output_path,
            )
            print(f"✨ Successfully completed: {self.output_path.name}")

        except Exception as e:
            print(f"\n💥 Process failure : {e}")
        finally:
            print("🧹 Cleaning temporary files...")
            self._cleanup()
            BlacksmithFixer(self.output_path)
