import subprocess
import re
import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger("audiobook.utils")


class FFmpegWrapper:
    @staticmethod
    def get_info(path: str) -> Dict[str, Any]:
        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_chapters",
            path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        import json

        return json.loads(result.stdout)

    @staticmethod
    def run_concat(
        list_path: str,
        meta_path: str,
        output_path: str,
        cover_path: Optional[str] = None,
    ) -> None:
        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            list_path,
            "-i",
            meta_path,
        ]

        if cover_path:
            cmd.extend(["-i", cover_path])
            cmd.extend(
                [
                    "-map",
                    "0:a",
                    "-map",
                    "2:v",
                    "-map_metadata",
                    "1",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "128k",
                    "-c:v",
                    "mjpeg",
                    "-disposition:v",
                    "attached_pic",
                ]
            )
        else:
            cmd.extend(
                ["-map", "0:a", "-map_metadata", "1", "-c:a", "aac", "-b:a", "128k"]
            )

        cmd.extend(["-movflags", "use_metadata_tags", output_path])

        logger.info(f"Encoding to {os.path.basename(output_path)}...")

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        )
        time_re = re.compile(r"time=(\d{2}:\d{2}:\d{2}.\d{2})")

        for line in process.stdout:  # type: ignore
            match = time_re.search(line)
            if match:
                print(f"\r[FFmpeg] Progress: {match.group(1)}", end="", flush=True)

        process.wait()
        print("")

        if process.returncode != 0:
            logger.error("FFmpeg error detected. Check your source files.")
            raise subprocess.CalledProcessError(process.returncode, cmd)

        logger.info("Process completed successfully.")


def natural_sort_key(s: str):
    import re

    return [
        int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", s)
    ]
