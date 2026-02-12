"""M4B chapter reader"""

from typing import List, cast, Union
from pathlib import Path
import subprocess
import json
import mutagen
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from audiobook.common import AudioChapter, AutoRepr


class ChapterReader(AutoRepr):
    """M4B chapter reader"""

    def __init__(self, file_path: Path, use_mutagen: bool = False):
        self._file_path = file_path
        self._mode = "ffprobe"
        if use_mutagen:
            self._mode = "mutagen"

        if self._mode == "ffprobe":
            self._chapters = self._with_ffprobe()
        elif self._mode == "mutagen":
            self._chapters = self._with_mutagen()

    @property
    def chapters(self) -> List[AudioChapter]:
        """Get chapters"""
        return self._chapters

    def _with_ffprobe(self) -> List[AudioChapter]:
        """Get M4B chapters (ffprobe is more accurate)"""
        chapters: List[AudioChapter] = []

        cmd = [
            "ffprobe",
            "-i",
            str(self._file_path),
            "-print_format",
            "json",
            "-show_chapters",
            "-loglevel",
            "error",
        ]

        res = subprocess.check_output(cmd)
        data = json.loads(res)
        chapters_json = data.get("chapters", [])

        for c in chapters_json:
            chapter_obj = AudioChapter(
                id=int(c.get("id", 0)),
                time_base=str(c.get("time_base", "1/44100")),
                start=int(c.get("start", 0)),
                start_time=str(c.get("start_time", "0.000000")),
                end=int(c.get("end", 0)),
                end_time=str(c.get("end_time", "0.000000")),
                tags=c.get("tags", {}),  # On récupère tout le dict des tags
            )
            chapters.append(chapter_obj)

        return chapters

    def _with_mutagen(self) -> List[AudioChapter]:
        """Get M4B chapters (mutagen is less accurate)"""
        data = mutagen.File(str(self._file_path))  # type: ignore
        audio = cast(Union[MP3, MP4], data)

        chapters: list[AudioChapter] = []

        if not isinstance(audio, MP4):
            return []

        # The audio sample rate is used as the time reference (time base)
        sample_rate = audio.info.sample_rate  # type: ignore
        total_length_sec = audio.info.length

        # Mutagen extracts chapters (normalized in ms by Mutagen)
        raw_chapters = getattr(audio, "chapters", [])

        for i, chap in enumerate(raw_chapters):
            # Conversion of Mutagen milliseconds to float seconds
            start_time_sec = float(chap.start) / 1000.0

            # Determining the end of the chapter
            if i + 1 < len(raw_chapters):
                end_time_sec = float(raw_chapters[i + 1].start) / 1000.0
            else:
                end_time_sec = float(total_length_sec)

            # Synchronizing samples with time (The ffprobe logic)
            # We round to the nearest integer to avoid sample shifts
            start_sample = int(round(start_time_sec * sample_rate))  # type: ignore
            end_sample = int(round(end_time_sec * sample_rate))  # type: ignore

            chapters.append(
                AudioChapter(
                    id=i,
                    time_base=f"1/{sample_rate}",
                    start=start_sample,
                    start_time=f"{start_time_sec:.6f}",
                    end=end_sample,
                    end_time=f"{end_time_sec:.6f}",
                    tags={
                        "title": chap.title,
                    },
                )
            )

        return chapters
