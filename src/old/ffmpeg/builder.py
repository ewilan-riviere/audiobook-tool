from pathlib import Path
import os
import shutil
import tempfile

# pylint: disable=no-name-in-module
from concurrent.futures import ProcessPoolExecutor, as_completed
import ffmpeg  # type: ignore


class AudiobookBuilder:
    """
    Convertit une liste de MP3 en un M4B final, proche du workflow audiobook-forge.
    """

    def __init__(self, mp3_files: list[str], output_file: str | None = None):
        self.mp3_files = [
            Path(f) for f in mp3_files if Path(f).suffix.lower() == ".mp3"
        ]
        if not self.mp3_files:
            raise ValueError("Aucun fichier MP3 valide fourni.")

        # Dossier temporaire pour les M4A intermédiaires
        self.temp_dir = Path(tempfile.mkdtemp(prefix="audiobook_"))

        # Fichier M4B final
        if output_file is None:
            self.output_file = self.mp3_files[0].parent / "final_book.m4b"
        else:
            self.output_file = Path(output_file)

        # Liste des fichiers intermédiaires et final
        self.m4a_files: list[str] = []
        self.m4b_file: str | None = None

    def _convert_mp3_to_m4a(self, mp3_path: Path) -> str:
        """Convertit un MP3 en M4A AAC 192kbps."""
        output_path = self.temp_dir / mp3_path.with_suffix(".m4a").name
        try:
            print(f"Conversion: {mp3_path.name} → {output_path.name}")
            stream = ffmpeg.input(str(mp3_path))  # type: ignore
            stream = ffmpeg.output(  # type: ignore
                stream,  # type: ignore
                str(output_path),
                acodec="aac",
                audio_bitrate="192k",  # bitrate constant
            )
            stream = stream.global_args("-threads", "0")  # threads auto # type: ignore
            ffmpeg.run(stream, overwrite_output=True, quiet=True)  # type: ignore
            return str(output_path)
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode(errors="ignore") if e.stderr else str(e)  # type: ignore
            print(f"Erreur FFmpeg sur {mp3_path.name}: {error_msg}")
            return ""

    def convert_all(self):
        """Convertit tous les MP3 en M4A en parallèle."""
        with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures = [
                executor.submit(self._convert_mp3_to_m4a, f) for f in self.mp3_files
            ]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    self.m4a_files.append(result)

        print(f"Conversion terminée : {len(self.m4a_files)} fichiers M4A générés.")

    def compile_m4b(self):
        """Concatène tous les M4A en un seul M4B final."""
        if not self.m4a_files:
            raise ValueError("Aucun fichier M4A pour la compilation.")

        list_file = self.temp_dir / "concat.txt"
        with open(list_file, "w", encoding="utf-8") as f:
            for m4a in self.m4a_files:
                f.write(f"file '{Path(m4a).resolve()}'\n")

        if self.output_file.exists():
            print(f"Suppression de l'ancien fichier : {self.output_file}")
            self.output_file.unlink()

        try:
            print(
                f"Compilation de {len(self.m4a_files)} fichiers en {self.output_file.name} ..."
            )
            stream = ffmpeg.input(str(list_file), format="concat", safe=0)  # type: ignore
            stream = ffmpeg.output(stream, str(self.output_file), c="copy")  # type: ignore
            ffmpeg.run(stream, overwrite_output=True, quiet=True)  # type: ignore
            self.m4b_file = str(self.output_file)
            print(f"Compilation terminée : {self.output_file}")
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode(errors="ignore") if e.stderr else str(e)  # type: ignore
            print(f"Erreur FFmpeg compilation: {error_msg}")
        finally:
            # Nettoyage du fichier concat
            if list_file.exists():
                list_file.unlink()

    def clean_temp(self):
        """Supprime le dossier temporaire contenant les M4A intermédiaires."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            print(f"Dossier temporaire supprimé : {self.temp_dir}")

    def build(self):
        """Pipeline complet : conversion MP3 → M4A → compilation M4B → nettoyage."""
        self.convert_all()
        self.compile_m4b()
        self.clean_temp()
