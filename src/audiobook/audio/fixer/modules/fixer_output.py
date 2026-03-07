from pathlib import Path
import subprocess

from audiobook import utils
from audiobook.audio.reader import AudioType


class FixerOutput:
    def __init__(
        self,
        input_path: Path,
        output_path: Path,
        audio_type: AudioType,
    ) -> None:
        self.input_path = input_path
        self.output_path = output_path
        self.audio_type = audio_type

    def run(self) -> bool:
        if self.audio_type == AudioType.MP3:
            self._m4a_to_mp3()
        elif self.audio_type == AudioType.M4B:
            utils.copy_file(self.input_path, self.output_path)
        elif self.audio_type == AudioType.M4A:
            utils.copy_file(self.input_path, self.output_path)

        return self.output_path.exists()

    def _m4a_to_mp3(self) -> bool:
        """
        Convertit M4A vers MP3 avec option de nettoyage des métadonnées.
        """

        cmd = [
            "ffmpeg",
            "-y",  # Écrase le fichier de sortie s'il existe
            "-v",
            "error",  # N'affiche que les erreurs critiques
            "-i",
            str(self.input_path),
            "-c:a",
            "libmp3lame",
            "-q:a",
            "2",  # VBR Haute qualité (~170-210 kbps)
            "-map_metadata",
            "-1",
            "-map_chapters",
            "-1",
            "-vn",
            str(self.output_path),
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            print("--- Erreur de conversion ---")
            print(f"Source : {self.input_path}")
            print(f"Détails : {e.stderr.strip()}")

            # Cas spécifique du 'moov atom not found'
            if "moov atom not found" in e.stderr:
                print("Conseil : Le fichier source semble corrompu ou incomplet.")

        return False
