"""Cut silences and clean MP3 files"""

import subprocess
from pathlib import Path
from typing import List, Tuple
import json
import audiobook.utils as utils


class CleanSilences:
    """Cut silences and clean MP3 files"""

    def __init__(self, mp3_directory: str):
        """
        :param file_paths: Liste des chemins vers les fichiers .mp3
        """

        print("Cut silences...")
        self.mp3_list = utils.get_files(mp3_directory, "mp3")
        self.file_paths: List[Path] = [Path(p) for p in self.mp3_list]
        # On garde trace des paires (original, temporaire) pour le remplacement final
        self._processed_files: List[Tuple[Path, Path]] = []

    def remove_silences(
        self, min_silence_len: int = 2000, silence_thresh: int = -40
    ) -> None:
        """Crée des fichiers _clean.mp3 pour chaque original."""
        print("\n--- Analyse et retrait des silences ---")
        self._processed_files = []  # Reset de la liste de suivi

        for path in self.file_paths:
            clean_path = path.with_name(f"{path.stem}_clean.mp3")

            success = self._cut_silence_logic(
                path, clean_path, min_silence_len, silence_thresh
            )

            if success:
                self._processed_files.append((path, clean_path))

    def finalize(self) -> None:
        """Remplace les fichiers originaux par les versions clean et nettoie."""
        if not self._processed_files:
            print("Aucun fichier à remplacer.")
            return

        print("\n--- Finalisation : Remplacement des originaux ---")
        for original, clean in self._processed_files:
            try:
                # On supprime l'original et on renomme le clean
                original.unlink()
                clean.rename(original)
                print(f"✓ Mis à jour : {original.name}")
            except Exception as e:
                print(f"× Erreur lors du remplacement de {original.name} : {e}")

    def _get_bitrate(self, path: Path) -> str:
        """Extrait le bitrate du fichier original."""
        try:
            command = [
                "ffprobe",
                "-v",
                "quiet",
                "-select_streams",
                "a:0",
                "-show_entries",
                "stream=bit_rate",
                "-of",
                "json",
                str(path),
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)

            # Le bitrate est retourné en bits/s (ex: 320000)
            bitrate_bps = int(data["streams"][0]["bit_rate"])
            return f"{bitrate_bps}"  # FFmpeg accepte la valeur brute en bits/s
        except (subprocess.CalledProcessError, KeyError, IndexError, ValueError):
            # Valeur de secours si l'extraction échoue (192k est un standard safe)
            return "192k"

    def _cut_silence_logic(
        self,
        chemin_entree: Path,
        chemin_sortie: Path,
        min_silence_len: int,
        silence_thresh: int,
    ) -> bool:
        try:
            print(f"Handle {chemin_entree}")
            duration_secs = min_silence_len / 1000.0

            # 1. On récupère le bitrate de l'original
            original_bitrate = self._get_bitrate(chemin_entree)

            silence_filter = (
                f"silenceremove=stop_periods=-1:"
                f"stop_duration={duration_secs}:"
                f"stop_threshold={silence_thresh}dB"
            )

            # 2. On adapte la commande
            command = [
                "ffmpeg",
                "-y",
                "-i",
                str(chemin_entree),
                "-af",
                silence_filter,
                "-codec:a",
                "libmp3lame",
                "-b:a",
                original_bitrate,  # On force le bitrate identique
                "-map_metadata",
                "0",  # On préserve les tags (Artiste, Album...)
                str(chemin_sortie),
            ]

            subprocess.run(
                command,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True

        except subprocess.CalledProcessError as e:
            print(f"Erreur sur {chemin_entree.name} : code {e.returncode}")
            return False
