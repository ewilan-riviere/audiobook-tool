import subprocess
import os
from typing import List
import audiobook.utils as utils


class M4bChapterEditor:
    def __init__(self, filepath: str, mp3_directory: str):
        self.mp3_directory = mp3_directory
        self.filepath: str = filepath
        self.filename: str = os.path.basename(filepath)
        self.meta_file: str = "temp_metadata.txt"
        self.temp_output: str = f"{os.path.splitext(filepath)[0]}_mod.m4b"

        self.original_titles: List[str] = []
        self.new_titles: List[str] = []

    def _extract_metadata(self) -> List[str]:
        result = subprocess.run(
            ["ffmpeg", "-i", self.filepath, "-f", "ffmetadata", "-"],
            check=True,
            capture_output=True,
        )

        return result.stdout.decode("utf-8", errors="replace").splitlines()

    def _process_lines(self, lines: List[str]) -> List[str]:
        new_lines: List[str] = []
        self.original_titles = []
        self.new_titles = []
        is_inside_chapter = False

        for line in lines:
            if line.strip() == "[CHAPTER]":
                is_inside_chapter = True
                new_lines.append(line)
                continue

            if is_inside_chapter and line.startswith("title="):
                old_title = line.split("=", 1)[1].strip()
                self.original_titles.append(old_title)

                mp3_file = os.path.join(self.mp3_directory, f"{old_title}.mp3")

                # Récupération du titre via votre utilitaire
                try:
                    mp3_title = utils.get_mp3_title(mp3_file)
                    new_title = f"{mp3_title}"
                except Exception:
                    new_title = old_title  # Fallback si le MP3 n'est pas trouvé

                self.new_titles.append(new_title)
                new_lines.append(f"title={new_title}")
                is_inside_chapter = False
            else:
                new_lines.append(line)

        return new_lines

    def _apply_metadata_with_ffmpeg(self) -> None:
        """Injecte les métadonnées et gère les erreurs de décodage des logs."""
        result = subprocess.run(
            [
                "ffmpeg",
                "-i",
                self.filepath,
                "-i",
                self.meta_file,
                "-map",
                "0:a",  # Audio
                "-map",
                "0:v?",  # Cover
                "-map_metadata",
                "1",
                "-map_chapters",
                "1",
                "-c",
                "copy",
                "-disposition:v:0",
                "attached_pic",
                self.temp_output,
                "-y",
            ],
            capture_output=True,
            # On ne met PAS text=True ici pour éviter que Python tente de décoder
            # automatiquement avec le mauvais codec.
        )

        # Si FFmpeg a échoué (code de sortie != 0)
        if result.returncode != 0:
            # On décode manuellement avec "replace" pour voir l'erreur sans planter
            error_msg = result.stderr.decode("utf-8", errors="replace")
            raise Exception(f"FFmpeg Error (Code {result.returncode}): {error_msg}")

    def run(self):
        try:
            print(f"Traitement de : {self.filename}...")
            lines = self._extract_metadata()

            updated_lines = self._process_lines(lines)

            if not self.original_titles:
                print("❌ Aucun chapitre trouvé.")
                return

            # Sauvegarde avec encodage explicite
            with open(self.meta_file, "w", encoding="utf-8", errors="replace") as f:
                f.write("\n".join(updated_lines) + "\n")

            print("Application des changements et conservation de la pochette...")
            self._apply_metadata_with_ffmpeg()

            # Remplacement du fichier
            os.remove(self.filepath)
            os.rename(self.temp_output, self.filepath)

            self._print_summary()

        except Exception as e:
            print(f"❌ Erreur : {e}")
        finally:
            if os.path.exists(self.meta_file):
                os.remove(self.meta_file)

    def _print_summary(self):
        print(f"\n✅ Succès ! {len(self.original_titles)} chapitres renommés.")
