"""Split M4B into multiple parts"""

import os
import subprocess
from pathlib import Path
import shutil
from typing import List, Dict, Any
from .m4b_chapter import M4bChapter, format_duration


class M4bSplit:
    """Split M4B into multiple parts"""

    DEFAULT_TARGET_SIZE_MB: int = 600
    FFMPEG_LOG_LEVEL: str = "error"
    OUTPUT_FOLDER_SUFFIX: str = "_parts"

    def __init__(self, m4b_file: str, chapters: List[M4bChapter]):
        self.m4b_file = Path(m4b_file)
        self.chapters = chapters
        self.yml_data: Dict[str, Any] = {}

    def get_split_plan(self) -> List[List[M4bChapter]]:
        """Calcule quels chapitres vont dans quelle partie selon la taille cible."""
        file_size_mb = os.path.getsize(self.m4b_file) / (1024 * 1024)
        total_duration = float(self.chapters[-1]["end_time"])
        mb_per_second = file_size_mb / total_duration

        plan: List[List[M4bChapter]] = []
        current_part: List[M4bChapter] = []
        current_part_size = 0.0

        for chapter in self.chapters:
            duration = float(chapter["end_time"]) - float(chapter["start_time"])
            chapter_size_mb = duration * mb_per_second

            size = current_part_size + chapter_size_mb > self.DEFAULT_TARGET_SIZE_MB
            if size and current_part:
                plan.append(current_part)
                current_part = []
                current_part_size = 0.0

            current_part.append(chapter)
            current_part_size += chapter_size_mb

        if current_part:
            plan.append(current_part)
        return plan

    def _prepare_output_dir(self) -> Path:
        """Create output dir (remove it before if exists)"""
        output_path = self.m4b_file.parent / (
            self.m4b_file.stem + self.OUTPUT_FOLDER_SUFFIX
        )
        if output_path.exists():
            shutil.rmtree(output_path)

        output_path.mkdir(parents=True, exist_ok=True)

        return output_path

    def run(self) -> List[Path]:
        """Lance le processus de découpage et retourne la liste des chemins absolus."""
        print(f"Fichier source : {self.m4b_file.name}")
        plan = self.get_split_plan()
        output_dir = self._prepare_output_dir()

        # Initialisation de la liste des résultats
        generated_files: List[Path] = []

        print(f"Plan de split : {len(plan)} parties détectées.\n")

        for i, part_chapters in enumerate(plan, 1):
            start_t = part_chapters[0]["start_time"]
            end_t = part_chapters[-1]["end_time"]
            duration = float(end_t) - float(start_t)

            output_file = output_dir / f"{self.m4b_file.stem} - Part {i:02}.m4b"

            print(
                f"Génération Part {i:02} | {format_duration(duration)} | {output_file.name}"
            )

            cmd = [
                "ffmpeg",
                "-loglevel",
                self.FFMPEG_LOG_LEVEL,
                "-i",
                str(self.m4b_file),
                "-ss",
                str(start_t),
                "-to",
                str(end_t),
                "-c",
                "copy",
                "-map_chapters",
                "0",  # Changed from -1 to 0
                "-y",
                str(output_file),
            ]

            subprocess.run(cmd, check=True)

            # On ajoute le chemin absolu à la liste
            generated_files.append(output_file.resolve())

        print(f"\nTerminé ! {len(generated_files)} fichiers générés.")
        return generated_files
