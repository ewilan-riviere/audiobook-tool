import subprocess
import tempfile
import os
from pathlib import Path
from typing import List
from audiobook.common import AudioChapter


class ChapterWriter:
    def __init__(self, file_path: str | Path):
        self.path = Path(file_path)

    def write_chapters(self, chapters: List["AudioChapter"]) -> None:
        """Injecte uniquement les chapitres."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f_meta:
            meta_path = f_meta.name
            f_meta.write(";FFMETADATA1\n")
            f_meta.write(self._generate_ffmetadata_block(chapters))

        try:
            temp_output = self.path.with_suffix(".tmp" + self.path.suffix)

            extension = self.path.suffix.lower()
            muxer_flags = []

            if extension in [".m4b", ".m4a", ".mp4"]:
                muxer_flags = ["-f", "mp4", "-movflags", "+faststart"]

            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(self.path),
                "-i",
                meta_path,
                "-map_metadata",
                "0",
                "-map_chapters",
                "1",
                "-map",
                "0",
                "-codec",
                "copy",
                *muxer_flags,  # On injecte les flags si nécessaire
                str(temp_output),
                "-loglevel",
                "error",
            ]
            subprocess.run(cmd, check=True)
            temp_output.replace(self.path)
        finally:
            if os.path.exists(meta_path):
                os.remove(meta_path)

    def _generate_ffmetadata_block(self, chapters: List[AudioChapter]) -> str:
        """Génère les blocs [CHAPTER] et normalise les objets Chapter en place."""
        lines = []
        for chap in chapters:
            # 1. Calculer le ratio de conversion
            # On passe de 1/44100 (ou autre) à 1/1000
            try:
                old_num, old_den = map(int, chap.time_base.split("/"))
            except (ValueError, AttributeError):
                old_num, old_den = 1, 44100

            # 2. Conversion en millisecondes (ms)
            # Formule : (valeur * num / den) * 1000
            start_ms = int(round(chap.start * (old_num / old_den) * 1000))
            end_ms = int(round(chap.end * (old_num / old_den) * 1000))

            # 3. MISE À JOUR DE L'OBJET (Normalisation pour tes tests)
            # On remplace les anciennes valeurs par les nouvelles en base 1/1000
            chap.start = start_ms
            chap.end = end_ms
            chap.time_base = "1/1000"
            # On recalcule les strings de temps pour être cohérent au millionième
            chap.start_time = f"{(start_ms / 1000):.6f}"
            chap.end_time = f"{(end_ms / 1000):.6f}"

            # 4. Écriture pour le fichier FFMETADATA
            lines.append("[CHAPTER]")  # type: ignore
            lines.append(f"TIMEBASE={chap.time_base}")  # type: ignore
            lines.append(f"START={chap.start}")  # type: ignore
            lines.append(f"END={chap.end}")  # type: ignore

            if chap.tags and "title" in chap.tags:
                # Échappement des caractères pour FFmpeg
                title = (
                    str(chap.tags["title"])
                    .replace("\\", "\\\\")
                    .replace("=", "\\=")
                    .replace(";", "\\;")
                    .replace("#", "\\#")
                )
                lines.append(f"title={title}")  # type: ignore

        return "\n".join(lines)  # type: ignore
