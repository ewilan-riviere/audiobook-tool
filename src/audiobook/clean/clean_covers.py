"""Clean covers from MP3 files"""

import subprocess
import os
from pathlib import Path
from typing import List, Tuple
import audiobook.utils as utils


class CleanCovers:
    """Clean covers from MP3 files"""

    def __init__(self, mp3_directory: str):
        """
        :param file_paths: Liste des chemins vers les fichiers .mp3
        """

        print("Clean covers...")
        self.mp3_list = utils.get_files(mp3_directory, "mp3")
        self.file_paths: List[Path] = [Path(p) for p in self.mp3_list]
        # On garde trace des paires (original, temporaire) pour le remplacement final
        self._processed_files: List[Tuple[Path, Path]] = []

    def remove_covers(self) -> None:
        """Supprime les covers via FFmpeg sans réencoder."""
        print("--- Nettoyage des covers ---")
        for path in self.file_paths:
            if not path.exists():
                continue

            temp_file = path.with_suffix(".nocover.mp3")
            try:
                command = [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(path),
                    "-map",
                    "0:a",
                    "-codec",
                    "copy",
                    "-map_metadata",
                    "0",
                    str(temp_file),
                ]
                subprocess.run(command, check=True, capture_output=True)
                os.replace(temp_file, path)
                print(f"✓ Cover retirée : {path.name}")
            except subprocess.CalledProcessError:
                print(f"× Erreur FFmpeg sur {path}")
