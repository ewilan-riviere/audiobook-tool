import os
import glob
import logging
import subprocess
from typing import List, Tuple, Optional
from .utils import FFmpegWrapper, natural_sort_key
from .metadata import MetadataManager

logger = logging.getLogger("audiobook.core")


class Processor:
    def merge(self, directory: str, output_path: Optional[str] = None) -> str:
        logger.info(f"Analyzing folder: {directory}")
        files = sorted(
            glob.glob(os.path.join(directory, "*.mp3")), key=natural_sort_key
        )

        if not files:
            raise FileNotFoundError(f"No MP3 files in {directory}")

        if not output_path:
            output_path = f"{os.path.basename(directory.rstrip(os.sep))}.m4b"

        if os.path.dirname(output_path):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

        chapters: List[Tuple[str, float]] = []
        temp_list = "temp_list.txt"

        with open(temp_list, "w", encoding="utf-8") as f:
            for file in files:
                info = FFmpegWrapper.get_info(file)
                duration = float(info["format"]["duration"])
                title = os.path.splitext(os.path.basename(file))[0]
                chapters.append((title, duration))
                safe_path = os.path.abspath(file).replace("'", "'\\''")
                f.write(f"file '{safe_path}'\n")

        meta_data = MetadataManager.load_yaml(directory)
        meta_content = MetadataManager.create_ffmpeg_meta_file(
            meta_data, chapters, directory
        )
        temp_meta = "temp_meta.txt"

        with open(temp_meta, "w", encoding="utf-8") as f:
            f.write(meta_content)

        cover = next(
            (
                os.path.join(directory, f"cover.{ext}")
                for ext in ["jpg", "png", "jpeg"]
                if os.path.exists(os.path.join(directory, f"cover.{ext}"))
            ),
            None,
        )

        try:
            FFmpegWrapper.run_concat(temp_list, temp_meta, output_path, cover)
        finally:
            for f in [temp_list, temp_meta]:
                if os.path.exists(f):
                    os.remove(f)

        return output_path

    def split_by_size(
        self,
        input_path: str,
        min_mb: int = 400,
        max_mb: int = 600,
        output_dir: Optional[str] = None,
    ) -> None:
        logger.info(f"Splitting file: {input_path}")
        info = FFmpegWrapper.get_info(input_path)
        chapters = info.get("chapters", [])

        if not chapters:
            logger.error("Cannot split: No chapters found in source.")
            return

        total_size = os.path.getsize(input_path)
        bytes_per_sec = total_size / float(info["format"]["duration"])
        min_bytes, max_bytes = min_mb * 1024**2, max_mb * 1024**2

        output_dir = output_dir or os.path.dirname(input_path) or "."
        os.makedirs(output_dir, exist_ok=True)

        cuts: List[Tuple[float, float]] = []
        start_t, current_size = 0.0, 0.0

        for i, chap in enumerate(chapters):
            c_start, c_end = float(chap["start_time"]), float(chap["end_time"])
            chap_size = (c_end - c_start) * bytes_per_sec
            current_size += chap_size

            next_size = 0.0
            if i < len(chapters) - 1:
                nc = chapters[i + 1]
                next_size = (
                    float(nc["end_time"]) - float(nc["start_time"])
                ) * bytes_per_sec

            if i == len(chapters) - 1 or (
                current_size >= min_bytes and (current_size + next_size) > max_bytes
            ):
                cuts.append((start_t, c_end))
                start_t, current_size = c_end, 0.0

        base = os.path.splitext(os.path.basename(input_path))[0]
        for idx, (s, e) in enumerate(cuts, 1):
            out = os.path.join(output_dir, f"{base}_part{idx:02d}.m4b")
            logger.info(f"Creating part {idx}...")
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    input_path,
                    "-ss",
                    str(s),
                    "-to",
                    str(e),
                    "-c",
                    "copy",
                    "-map_metadata",
                    "0",
                    "-movflags",
                    "use_metadata_tags",
                    out,
                ],
                capture_output=True,
                check=True,
            )
