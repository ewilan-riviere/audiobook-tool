"""M4B chapter reader"""

from typing import List, cast, Union
import subprocess
import json
import mutagen
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from audiobook.utils import AutoRepr
from .chapter import Chapter


class ChapterReader(AutoRepr):
    """M4B chapter reader"""

    def __init__(self, path: str):
        self._path = path
        data = mutagen.File(str(path))  # type: ignore
        self.audio = cast(Union[MP3, MP4], data)

    def with_ffprobe(self) -> List[Chapter]:
        """Get M4B chapters (use ffprobe for precision)"""
        chapters: List[Chapter] = []

        cmd = [
            "ffprobe",
            "-i",
            str(self._path),
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
            chapter_obj = Chapter(
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

    def with_mutagen(self) -> List[Chapter]:
        """Extracts the mirrored chapters from the ffprobe logic"""
        chapters: list[Chapter] = []

        if not isinstance(self.audio, MP4):
            return []

        # The audio sample rate is used as the time reference (time base)
        sample_rate = self.audio.info.sample_rate  # type: ignore
        total_length_sec = self.audio.info.length

        # Mutagen extracts chapters (normalized in ms by Mutagen)
        raw_chapters = getattr(self.audio, "chapters", [])

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
                Chapter(
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
