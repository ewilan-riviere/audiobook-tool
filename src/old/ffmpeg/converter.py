from pathlib import Path
import os
import shutil

# pylint: disable=no-name-in-module
from concurrent.futures import ProcessPoolExecutor
import ffmpeg  # type: ignore


class FfmpegConverter:
    """
    files: liste de chemins MP3
    clear_output_dir: True pour supprimer le dossier m4b existant
    quality: 1 (max qualité) → 5 (voix / livre audio optimisé)
    """

    def __init__(
        self, files: list[str], clear_output_dir: bool = True, quality: int = 5
    ):
        # Convertir en Path et filtrer les MP3 valides
        self.files = [Path(f) for f in files if Path(f).suffix.lower() == ".mp3"]
        self.quality = quality
        self.m4b_files: list[str] = []

        if not self.files:
            raise ValueError("Aucun fichier MP3 valide fourni.")

        # Crée un dossier m4b dans le dossier parent du premier fichier
        self.output_dir = self.files[0].parent / "m4b"
        if clear_output_dir and self.output_dir.exists():
            print(f"Suppression du dossier existant : {self.output_dir}")
            shutil.rmtree(self.output_dir)

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _convert_file(self, input_path: Path) -> str:
        output_path = self.output_dir / input_path.with_suffix(".m4b").name
        try:
            print(f"Conversion de `{input_path.name}`...")
            stream = ffmpeg.input(str(input_path))  # type: ignore
            stream = ffmpeg.output(  # type: ignore
                stream,  # type: ignore
                str(output_path),
                acodec="aac",
                audio_bitrate="192k",
            )
            stream = stream.global_args("-threads", "0")  # type: ignore
            ffmpeg.run(stream, overwrite_output=True, quiet=True)  # type: ignore
            print(f"Terminé : {output_path.name}")
            return str(output_path)
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode(errors="ignore") if e.stderr else str(e)  # type: ignore
            print(f"FFmpeg error sur {input_path.name}: {error_msg}")
            return ""  # ou None si erreur

    def convert_all(self):
        with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
            results = executor.map(self._convert_file, self.files)
            # Récupérer tous les fichiers générés dans self.m4b_files
            self.m4b_files = [r for r in results if r]
