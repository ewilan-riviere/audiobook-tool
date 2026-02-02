import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional
import audiobook.utils as utils


class Extractor:
    def __init__(self, input_folder: str, output_folder: str | None = None):
        self.input_folder = Path(input_folder)
        if output_folder:
            self.output_folder = Path(output_folder)
        else:
            self.output_folder = Path(utils.path_join(str(self.input_folder), "output"))
        self.m4b_files: List[Path] = sorted(list(self.input_folder.glob("*.m4b")))

        if not self.m4b_files:
            raise FileNotFoundError(f"Aucun fichier M4B trouvé dans {input_folder}")

        if not self.output_folder.exists():
            self.output_folder.mkdir(parents=True)

    def get_chapters(self, file_path: Path) -> List[Dict]:  # type: ignore
        """Extrait les chapitres d'un fichier via ffprobe."""
        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_chapters",
            str(file_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)

        return data.get("chapters", [])

    def sanitize_filename(self, filename: str) -> str:
        """Nettoie le nom de fichier pour éviter les caractères interdits."""
        return "".join(
            [c for c in filename if c.isalnum() or c in (" ", ".", "_", "-")]
        ).strip()

    def convert_and_split(self) -> None:
        """Parcourt les fichiers, extrait les chapitres et découpe en MP3."""
        print(f"Traitement de {len(self.m4b_files)} fichier(s)...")

        for file_index, m4b_file in enumerate(self.m4b_files):
            chapters = self.get_chapters(m4b_file)  # type: ignore
            print(f"Chapters: {len(chapters)}")  # type: ignore

            if not chapters:
                print(
                    f"⚠️ Aucun chapitre trouvé dans {m4b_file.name}. Conversion globale."
                )
                self._export_segment(m4b_file, "Full_Book", None, None)
                continue

            for chap in chapters:  # type: ignore
                # Récupération des données du chapitre
                title = chap.get("tags", {}).get("title", f"Chapter_{chap['id']}")  # type: ignore
                start_time = chap["start_time"]  # type: ignore
                end_time = chap["end_time"]  # type: ignore

                # Formatage du nom : "01 - Titre du Chapitre.mp3"
                clean_title = self.sanitize_filename(title)  # type: ignore
                output_name = (
                    f"{file_index + 1:02d}_{chap['id'] + 1:02d}_{clean_title}.mp3"
                )

                print(f"Extraction : {output_name} ({start_time}s -> {end_time}s)")
                self._export_segment(m4b_file, output_name, start_time, end_time)  # type: ignore

    def _export_segment(
        self,
        input_file: Path,
        output_name: str,
        start: Optional[str],
        end: Optional[str],
    ) -> None:
        """Exécute la commande FFmpeg pour l'extraction."""
        output_path = self.output_folder / output_name

        # Commande FFmpeg : -ss (début), -to (fin), -i (entrée)
        # On encode en MP3 (libmp3lame) avec un bitrate variable (V2 est souvent suffisant)
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(input_file)]

        if start is not None and end is not None:
            cmd.extend(["-ss", start, "-to", end])

        cmd.extend(["-codec:a", "libmp3lame", "-q:a", "2", str(output_path)])

        subprocess.run(cmd, check=True)
