import os
import logging
from typing import List, Tuple, Dict, Any, Optional, cast
import yaml

logger = logging.getLogger("audiobook.metadata")


class MetadataManager:
    @staticmethod
    def load_yaml(directory: str) -> Dict[str, Any]:
        path = os.path.join(directory, "metadata.yml")
        if not os.path.exists(path):
            logger.info("No metadata.yml found, using defaults.")
            return {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
                if isinstance(content, dict):
                    logger.info("Successfully loaded metadata.yml")
                    return cast(Dict[str, Any], content)
                return {}
        except Exception as e:
            logger.warning(f"Could not parse metadata.yml: {e}")
            return {}

    @staticmethod
    def create_ffmpeg_meta_file(
        data: Dict[str, Any], chapters: List[Tuple[str, float]], directory: str
    ) -> str:
        logger.info("Generating FFmpeg metadata header...")
        lines = [";FFMETADATA1"]
        default_title = os.path.basename(directory.rstrip(os.sep))

        mapping: Dict[str, Optional[Any]] = {
            "title": data.get("title") or default_title,
            "album": data.get("title") or default_title,
            "artist": data.get("authors") or "Unknown Author",
            "album_artist": data.get("authors") or "Unknown Author",
            "composer": data.get("narrators"),
            "comment": data.get("description"),
            "genre": data.get("genres") or "Audiobook",
            "date": str(data.get("year", "")) if data.get("year") else None,
        }

        for key, value in mapping.items():
            if value is not None:
                clean_value = str(value).replace("\n", " ").strip()
                if clean_value:
                    lines.append(f"{key}={clean_value}")

        curr_ms: float = 0
        for title, dur in chapters:
            start = int(curr_ms)
            end = int(curr_ms + (dur * 1000))
            lines.extend(
                [
                    "[CHAPTER]",
                    "TIMEBASE=1/1000",
                    f"START={start}",
                    f"END={end}",
                    f"title={title}",
                ]
            )
            curr_ms = end

        return "\n".join(lines)
