import os
from pathlib import Path
import subprocess
import audiobook.utils as utils
from audiobook.common import AutoRepr
from audiobook.audio import AudioReader
from audiobook.common import AudioChapter


class M4bSplitter(AutoRepr):
    """Split M4B into multiple parts"""

    FFMPEG_LOG_LEVEL: str = "error"

    _m4b_file: Path
    _working_directory: Path
    _part_size: int = 500
    _reader: AudioReader
    _plan: list[list[AudioChapter]] = []
    _parts: int = 0
    _m4b_files: list[Path] = []

    def __init__(
        self,
        m4b_file: str | Path,
        working_directory: Path,
        part_size: int,
    ):
        self._m4b_file = Path(m4b_file)
        self._working_directory = working_directory
        self._part_size = part_size
        if not self._m4b_file.exists():
            raise FileNotFoundError(f"{self._m4b_file} not exists")

        self._reader = AudioReader(self._m4b_file)
        self._plan = self._handle_split_plan()
        self._parts = len(self._plan)

    @property
    def m4b_files(self) -> list[Path]:
        """Get M4B files"""
        return self._m4b_files

    def _handle_split_plan(self) -> list[list[AudioChapter]]:
        """Calculate which chapters go in which section based on the target size"""
        plan: list[list[AudioChapter]] = []
        chapters = self._reader.tags.chapters

        file_size_mb = os.path.getsize(self._m4b_file) / (1024 * 1024)
        last_chapter = chapters[-1]

        total_duration = float(last_chapter.end_time)
        mb_per_second = file_size_mb / total_duration

        current_part: list[AudioChapter] = []
        current_part_size = 0.0

        for chapter in chapters:
            duration = float(chapter.end_time) - float(chapter.start_time)
            chapter_size_mb = duration * mb_per_second

            size = current_part_size + chapter_size_mb > self._part_size
            if size and current_part:
                plan.append(current_part)
                current_part = []
                current_part_size = 0.0

            current_part.append(chapter)
            current_part_size += chapter_size_mb

        if current_part:
            plan.append(current_part)

        return plan

    def run(self):
        """Run ffmpeg to split M4B"""
        # temporary_dir = Path(self._working_directory.name)
        generated_files: list[Path] = []

        for i, part_chapters in enumerate(self._plan, 1):
            first_chapter = part_chapters[0]
            last_chapter = part_chapters[-1]
            start_t = float(first_chapter.start_time)
            end_t = float(last_chapter.end_time)
            duration = end_t - start_t

            file_name = f"{self._m4b_file.stem} - Part {i:02}.m4b"
            output_file = self._working_directory / file_name

            # --- Step 1: Create the metadata file ---
            meta_file = self._working_directory / f"metadata_part_{i}.txt"
            with open(meta_file, "w", encoding="utf-8") as f:
                f.write(";FFMETADATA1\n")
                for chapter in part_chapters:
                    c_start = int((float(chapter.start_time) - start_t) * 1000)
                    c_end = int((float(chapter.end_time) - start_t) * 1000)
                    f.write("\n[CHAPTER]\nTIMEBASE=1/1000\n")
                    f.write(f"START={c_start}\n")
                    f.write(f"END={c_end}\n")
                    f.write(f"title={chapter.title}\n")

            # --- Step 2: Run FFmpeg (Essential before calculating the size) ---
            cmd = [
                "ffmpeg",
                "-loglevel",
                self.FFMPEG_LOG_LEVEL,
                "-ss",
                str(start_t),
                "-to",
                str(end_t),
                "-i",
                str(self._m4b_file),
                "-i",
                str(meta_file),
                "-map",
                "0:a",
                "-map_metadata",
                "0",
                "-map_metadata",
                "1",
                "-map_chapters",
                "1",
                "-c",
                "copy",
                "-movflags",
                "+faststart",
                "-y",
                str(output_file),
            ]

            subprocess.run(cmd, check=True)

            # --- Step 3: Now that the file exists, we retrieve its size ---
            size = utils.get_file_size(output_file)
            size_hr = utils.size_human_readable(size)
            duration_str = utils.format_duration(duration, short=True)

            print(
                f"  ✅ Generate Part {i:02} `{output_file.name}` "
                f"({duration_str} / {len(part_chapters)} chap.) / {size_hr}"
            )

            generated_files.append(output_file.resolve())

        self._m4b_files = [Path(p) for p in generated_files]

        return self
