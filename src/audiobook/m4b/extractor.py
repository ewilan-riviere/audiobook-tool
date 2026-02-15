"""Extract chapters from M4B files and convert to M4A/MP3"""

import subprocess
from pathlib import Path
from audiobook import utils
from audiobook.audio.writer.main import AudioWriter
from audiobook.common.chapter import AudioChapter
from audiobook.models import ContainerAudiobook


class M4bExtractor:
    """Extract chapters from M4B files and convert to M4A/MP3"""

    def __init__(self, container: ContainerAudiobook):
        self.container = container
        self.output_dir = container.audiobook_path / "extracted_chapters"
        self.total_chapters: int = 0

        utils.remove_directory(self.output_dir)
        utils.make_directory(self.output_dir)

        self.total_chapters: int = len(self.container.chapters)

    def to_m4a(self) -> Path:
        """
        Extract chapters directly to M4A (Very fast).
        """
        self._start(
            mode="M4A extraction (Stream Copy)",
        )

        current_m4b_index = 0

        for i, chapter in enumerate(self.container.chapters):
            if i > 0 and chapter.id == 0:
                current_m4b_index += 1

            input_file = self.container.m4b_files[current_m4b_index]
            output_path = self._handle_chapter(chapter, i, "m4a")
            self._progress(i, output_path)

            self._ffmpeg_m4a(
                input_file,
                chapter.start_time,
                chapter.end_time,
                output_path,
            )

            self._handle_chapter_tag(chapter, i, output_path)

        return self._end()

    def to_mp3(self, high_fidelity: bool = True) -> Path:
        """
        Extract chapters directly to MP3 (Quite slow).
            :param high_fidelity: `True`: V0 mode (Top Quality) /
                `False`: aligns with the source bitrate
        """
        self._start(
            mode="MP3 re-encoding",
            subtitle=f"📈 STRATEGY : {'HIFI (V0)' if high_fidelity else 'Match Source Bitrate'}",
        )

        current_m4b_index = 0

        for i, chapter in enumerate(self.container.chapters):
            if i > 0 and chapter.id == 0:
                current_m4b_index += 1

            input_file = self.container.m4b_files[current_m4b_index]
            output_path = self._handle_chapter(chapter, i, "mp3")
            self._progress(i, output_path)

            if high_fidelity:
                audio_params = ["-q:a", "0"]
            else:
                audio_params = self._find_m4b_bitrate(input_file)

            self._ffmpeg_mp3(
                input_file,
                chapter.start_time,
                chapter.end_time,
                output_path,
                audio_params,
            )

            self._handle_chapter_tag(chapter, i, output_path)

        return self._end()

    def _handle_chapter(self, chapter: AudioChapter, i: int, extension: str):
        raw_title = chapter.tags.get("title", f"Chapter_{i}")
        clean_title = "".join(
            [c for c in raw_title if c.isalnum() or c in (" ", "-", "_")]
        ).strip()

        return self.output_dir / f"{i + 1:02d} - {clean_title}.{extension}"

    def _handle_chapter_tag(self, chapter: AudioChapter, i: int, output_path: Path):
        title = chapter.tags.get("title", f"Chapter_{i}")
        writer = AudioWriter(output_path)
        writer.set_tag("title", title)

    def _start(self, mode: str, subtitle: str | None = None):
        divider = "=" * 60

        print(f"\n{divider}")
        print(f"🚀 MODE: {mode}")
        if subtitle:
            print(subtitle)
        print(f"🔢 Chapters to be covered: {self.total_chapters}")
        print(f"{divider}\n")

    def _progress(self, i: int, output_path: Path):
        progress = ((i + 1) / self.total_chapters) * 100
        print(f"[{progress:6.2f}%] 🛠  Convert: {output_path.name}")

    def _end(self) -> Path:
        print(f"\n✅ Done! Files in: {self.output_dir}")

        return self.output_dir

    def _find_m4b_bitrate(self, m4b_path: Path) -> list[str]:
        """Recovers the source bitrate of M4B file to adapt it to MP3 (+20% margin)"""
        try:
            cmd = [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=bit_rate",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(m4b_path),
            ]
            res = subprocess.run(cmd, check=True, capture_output=True, text=True)
            source_br = int(res.stdout.strip())

            # We boost the bitrate a little because MP3 is less efficient than AAC
            target_kbps = min(int(source_br * 1.2) // 1000, 320)
            return ["-b:a", f"{target_kbps}k"]
        except Exception:
            # Fallback
            return ["-q:a", "4"]

    def _ffmpeg_m4a(self, input_path: Path, start: str, end: str, output_path: Path):
        """Cuts and stream copy each M4B file to M4A"""
        command = [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-ss",
            str(start),
            "-to",
            str(end),
            "-i",
            str(input_path),
            "-map",
            "0:a:0",  # Only audio
            "-c",
            "copy",
            "-map_metadata",
            "-1",  # Avoid ghost chapter
            "-vn",
            "-sn",
            "-dn",  # No video/subtitles/data
            str(output_path),
        ]
        subprocess.run(command, check=True)

    def _ffmpeg_mp3(
        self,
        input_path: Path,
        start: str,
        end: str,
        output_path: Path,
        audio_params: list[str],
    ):
        """Cuts and converts each M4B file to MP3"""
        command = [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-ss",
            str(start),
            "-to",
            str(end),
            "-i",
            str(input_path),
            "-map",
            "0:a:0",  # Pure audio extraction only
            "-codec:a",
            "libmp3lame",  # Direct conversion to MP3
            *audio_params,  # Implementation of the quality strategy
            "-map_metadata",
            "-1",  # Cleaning corrupted metadata
            str(output_path),
        ]
        subprocess.run(command, check=True)
