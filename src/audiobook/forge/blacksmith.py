"""Compile MP3 files into M4B"""

import os
from pathlib import Path
from concurrent.futures import as_completed
from concurrent.futures.process import ProcessPoolExecutor
from audiobook.audio.fixer.main import AudioFixer
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
        self._needs_encoding: bool = True

    @property
    def output_path(self):
        """Get output path"""
        return self._output_path

    def _get_reader(self, path: Path):
        # pylint: disable=import-outside-toplevel
        from audiobook.audio import AudioReader

        return AudioReader(path)

    def _prepare_data(self) -> None:
        """Initializes the chapter list, calculates the bitrate, and extracts titles from tags."""
        self._source_files = utils.get_files(self._source_path, "mp3")
        if not self._source_files:
            self._source_files = utils.get_files(self._source_path, "m4a")
            self._needs_encoding = False

        if not self._source_files:
            raise FileNotFoundError(f"No MP3 or M4A files found in {self._source_path}")

        print("📏 Try to fix source files if needed...")
        for _source_file in self._source_files:
            AudioFixer(_source_file).run(replace_original=True)

        total_bitrate: int = 0
        file_count = len(self._source_files)

        print("🔧 Parse source files to create chapters...")
        for source_file in self._source_files:
            reader = self._get_reader(source_file)
            source_file_bitrate = reader.properties.bit_rate or 128000
            total_bitrate += source_file_bitrate

            title_tag = (reader.tags.title or "Unknown").strip()
            chapter_title = title_tag
            if reader.tags.chapters:
                chapter_title = (reader.tags.chapters[0].title or title_tag).strip()
            if not chapter_title:
                chapter_title = reader.container.basename

            m4a_path = (
                self._working_directory / f"{source_file.stem}.m4a"
                if self._needs_encoding
                else source_file
            )

            chapter = BlacksmithChapter(
                source_path=source_file,
                temp_aac_path=m4a_path,
                file_name=source_file.stem,
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

        mode = "Encoding (MP3 -> AAC)" if self._needs_encoding else "Direct Link (M4A)"
        print(
            f"🔍 Analyze: {file_count} files found. Mode: {mode}. Bitrate: {self._target_bitrate}"
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

    def _encoding(self):
        total = len(self._chapters)
        print(f"🚀 Encoding of {total} files on {os.cpu_count()} cores...")
        try:
            with ProcessPoolExecutor() as executor:
                futures = {
                    executor.submit(
                        BlacksmithRunner.encode_to_aac,
                        c.source_path,
                        c.temp_aac_path,
                        self._target_bitrate,
                    ): c.source_path.name
                    for c in self._chapters
                }
                for i, future in enumerate(as_completed(futures), 1):
                    future.result()
                    print(f"  ✅ [{i}/{total}] Done: {futures[future]}")
        except Exception as e:
            print(f"\n💥 Encoding failure: {e}")

    def _merging(self):
        try:
            print("📦 Final merger and creation of chapters...")
            self._write_assets()

            m4b_path = BlacksmithRunner.merge_to_m4b(
                self._inputs_txt_path,
                self._metadata_txt_path,
                self._working_directory / "final_m4b.m4b",
            )
            self._output_path = m4b_path

        except Exception as e:
            print(f"\n💥 Merging failure: {e}")

    def run(self):
        """Start process."""
        self._prepare_data()

        if self._needs_encoding:
            self._encoding()
        else:
            print("⏭️  Skipping encoding: Files are already in M4A format.")

        self._merging()
        self._final_check()

        return self

    def _final_check(self):
        """Check M4B output file"""
        if self._output_path and self._output_path.exists():
            reader = self._get_reader(self._output_path)
            if reader.properties.bit_rate:
                print("✨ Successfully completed!")
                return
        print("❌ Failed to validate final M4B file.")
