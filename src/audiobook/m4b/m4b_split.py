"""Split M4B into multiple parts"""

from typing import List
from pathlib import Path
import os
import subprocess
from audiobook.config import ConfigBuild
from audiobook.metadata import MetadataChapter
import audiobook.utils as utils
from audiobook.env import PART_SIZE


class M4bSplit:
    """Split M4B into multiple parts"""

    FFMPEG_LOG_LEVEL: str = "error"

    def __init__(self, config: ConfigBuild):
        self._config = config
        self._m4b_path = config.m4b_forge_path
        self._temp_directory = config.temporary_directory
        self.m4b_split_paths: list[str] = []

        if config.m4b_forge_metadata:
            self._chapters = config.m4b_forge_metadata.chapters
            self._split_plan = self._handle_split_plan()

    def run(self):
        """Run ffmpeg to split M4B"""
        temporary_dir = Path(self._temp_directory.name)
        generated_files: List[Path] = []

        for i, part_chapters in enumerate(self._split_plan, 1):
            first_chapter = part_chapters[0]
            last_chapter = part_chapters[-1]
            start_t = float(first_chapter.start_time)
            end_t = float(last_chapter.end_time)
            duration = end_t - start_t

            output_file = (
                temporary_dir / f"{Path(str(self._m4b_path)).stem} - Part {i:02}.m4b"
            )

            # --- ÉTAPE 1: Créer le fichier de métadonnées ---
            meta_file = temporary_dir / f"metadata_part_{i}.txt"
            with open(meta_file, "w", encoding="utf-8") as f:
                f.write(";FFMETADATA1\n")
                for chap in part_chapters:
                    c_start = int((float(chap.start_time) - start_t) * 1000)
                    c_end = int((float(chap.end_time) - start_t) * 1000)
                    f.write("\n[CHAPTER]\nTIMEBASE=1/1000\n")
                    f.write(f"START={c_start}\n")
                    f.write(f"END={c_end}\n")
                    f.write(f"title={chap.title}\n")

            # --- ÉTAPE 2: Exécuter FFmpeg (Indispensable AVANT de calculer la taille) ---
            cmd = [
                "ffmpeg",
                "-loglevel",
                self.FFMPEG_LOG_LEVEL,
                "-ss",
                str(start_t),
                "-to",
                str(end_t),
                "-i",
                str(self._m4b_path),
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

            # --- ÉTAPE 3: Maintenant que le fichier existe, on récupère sa taille ---
            size = utils.get_file_size(str(output_file))
            raw_size = utils.size_human_readable(size)
            if isinstance(raw_size, tuple):
                size_hr = f"{raw_size[0]} {raw_size[1]}"
            else:
                size_hr = str(raw_size)

            # Affichage du log de succès
            print(
                f"  ✅ Generate Part {i:02} `{output_file.name}` "
                f"({utils.format_duration(duration)} / {len(part_chapters)} chap.) / {size_hr}"
            )

            generated_files.append(output_file.resolve())
            meta_file.unlink()  # Nettoyage

        self.m4b_split_paths = [str(p) for p in generated_files]
        return self

    def _handle_split_plan(self) -> List[List[MetadataChapter]]:
        """Calculate which chapters go in which section based on the target size"""
        plan: List[List[MetadataChapter]] = []

        if not self._m4b_path:
            print("Error: no M4B file")
            return plan

        file_size_mb = os.path.getsize(self._m4b_path) / (1024 * 1024)
        last_chapter = self._chapters[-1]
        total_duration = float(last_chapter.end_time)
        mb_per_second = file_size_mb / total_duration

        current_part: List[MetadataChapter] = []
        current_part_size = 0.0

        for chapter in self._chapters:
            duration = float(chapter.end_time) - float(chapter.start_time)
            chapter_size_mb = duration * mb_per_second

            size = current_part_size + chapter_size_mb > PART_SIZE
            if size and current_part:
                plan.append(current_part)
                current_part = []
                current_part_size = 0.0

            current_part.append(chapter)
            current_part_size += chapter_size_mb

        if current_part:
            plan.append(current_part)

        return plan
