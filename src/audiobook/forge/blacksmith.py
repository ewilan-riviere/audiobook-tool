"""Compile MP3 files into M4B"""

import os
from pathlib import Path
from concurrent.futures import as_completed, Future
from concurrent.futures.process import ProcessPoolExecutor
from audiobook.common import AutoRepr
import audiobook.utils as utils
from .modules import BlacksmithChapter, BlacksmithRunner


class AudiobookBlacksmith(AutoRepr):
    """Compile MP3 files into M4B"""

    def __init__(self, source_path: Path, working_directory: Path):
        self._source_path = source_path
        self._working_directory = working_directory
        self._metadata_txt_path = self._working_directory / "metadata.txt"
        self._inputs_txt_path = self._working_directory / "inputs.txt"

        self._chapters: list[BlacksmithChapter] = []
        self._target_bitrate: str = "128k"
        self._output_path: Path | None = None
        self._source_files: list[Path] = []

    @property
    def output_path(self):
        """Get output path"""
        return self._output_path

    def _get_reader(self, path: Path):
        """Helper centralisé pour éviter les redéfinitions et les cycles"""
        # pylint: disable=import-outside-toplevel
        from audiobook.audio import AudioReader

        return AudioReader(path)

    def _prepare_data(self) -> None:
        """Initializes the chapter list, calculates the bitrate, and extracts titles from tags."""
        self._source_files = utils.get_files(self._source_path, "mp3")
        if not self._source_files:
            raise FileNotFoundError(f"No MP3 files found into {self._source_path}")

        total_bitrate: int = 0
        file_count = len(self._source_files)

        for mp3 in self._source_files:
            reader = self._get_reader(mp3)
            mp3_bitrate = reader.properties.bit_rate or 128000
            total_bitrate += mp3_bitrate

            title_tag = (reader.tags.title or "Unknown").strip()
            chapter_title = title_tag
            if reader.tags.chapters:
                chapter_title = (reader.tags.chapters[0].title or title_tag).strip()
            if not chapter_title:
                chapter_title = reader.container.basename

            m4a_path = self._working_directory / f"{mp3.stem}.m4a"
            chapter = BlacksmithChapter(
                source_path=mp3,
                temp_aac_path=m4a_path,
                file_name=mp3.stem,
                title=chapter_title,
                track=reader.tags.track_int,
                duration_ms=reader.properties.duration_ms,
            )
            self._chapters.append(chapter)

        self._chapters.sort(
            key=lambda x: (
                x.track if x.track is not None else float("inf"),
                x.file_name,
            )
        )

        # avg_bitrate = int(total_bitrate / file_count)
        avg_bitrate = min(int(total_bitrate / file_count), 192000)
        self._target_bitrate = f"{int(avg_bitrate / 1000)}k"

        print(
            f"🔍 Analyze: {file_count} files. Average bitrate: {self._target_bitrate}"
        )

    def _write_assets(self) -> None:
        """Generates metadata based on the actual duration of encoded files"""
        metadata_lines = [";FFMETADATA1"]
        current_time_ms = 0

        with open(self._inputs_txt_path, "w", encoding="utf-8") as input_txt:
            for chapter in self._chapters:
                # 💡 CALCULER LA DURÉE SUR LE FICHIER AAC TEMP, PAS LE MP3
                # Le format AAC/ADTS n'a pas toujours de header de durée
                reader = self._get_reader(chapter.temp_aac_path)
                metadata_lines.append(
                    f"\n[CHAPTER]\nTIMEBASE=1/1000\nSTART={current_time_ms}"
                )
                current_time_ms += reader.properties.duration_ms
                metadata_lines.append(f"END={current_time_ms}\ntitle={chapter.title}")
                path_str = str(chapter.temp_aac_path).replace("'", "'\\''")
                input_txt.write(f"file '{path_str}'\n")

        self._metadata_txt_path.write_text("\n".join(metadata_lines), encoding="utf-8")

    def run(self):
        """Start parallel encoding and final merging."""
        self._prepare_data()

        try:
            total = len(self._chapters)
            print(f"🚀 Encoding of {total} files on {os.cpu_count()} cores...")

            future_to_file: dict[Future[str], str] = {}

            with ProcessPoolExecutor() as executor:
                for c in self._chapters:
                    future = executor.submit(
                        BlacksmithRunner.encode_to_aac,
                        c.source_path,
                        c.temp_aac_path,
                        self._target_bitrate,
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
            m4b_path = BlacksmithRunner.merge_to_m4b(
                self._inputs_txt_path,
                self._metadata_txt_path,
                self._working_directory / "final_m4b.m4b",
            )
            self._output_path = m4b_path
        except Exception as e:
            print(f"\n💥 Process failure : {e}")
        finally:
            if self._output_path:
                reader = self._get_reader(self._output_path)
                if reader.properties.bit_rate:
                    print("✨ Successfully completed!")
                else:
                    print("Failed on AudioReader!")
            else:
                print("Failed on AudioReader!")

        return self
