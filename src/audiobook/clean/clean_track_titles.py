"""Clean track titles from M4B files"""

import os
import subprocess
import re
from typing import List, Optional
import json
import audiobook.utils as utils


class CleanTrackTitles:
    """Clean track titles from M4B files"""

    def __init__(self, m4b_directory: str):
        self.m4b_directory = m4b_directory
        self.m4b_list = utils.get_files(self.m4b_directory, "m4b")

    def _get_title(self, file_path: str) -> Optional[str]:
        """
        Utilise ffprobe pour extraire le titre actuel des métadonnées.
        """
        command: List[str] = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            file_path,
        ]

        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            return None

        data = json.loads(result.stdout)
        # Récupère le titre dans les tags, retourne None si absent
        return data.get("format", {}).get("tags", {}).get("title")

    def _clean_audio_title(self, title: str) -> str:
        # Motif : début de chaîne (^), deux chiffres (\d{2}), un ou plusieurs espaces (\s+)
        pattern: str = r"^\d{2}\s+"

        # re.sub remplace le motif trouvé par une chaîne vide ''
        # Si le motif n'est pas trouvé, il renvoie la chaîne originale intacte
        cleaned_title: str = re.sub(pattern, "", title)

        return cleaned_title

    def edit(self) -> None:
        """
        Modifie le titre des fichiers M4B dans un répertoire donné.
        """
        for filename in self.m4b_list:
            input_path: str = os.path.join(self.m4b_directory, filename)
            output_path: str = os.path.join(self.m4b_directory, f"temp_{filename}")

            original_title: Optional[str] = self._get_title(input_path)
            if original_title:
                new_title: str = f"{original_title}"

                if " _ " in original_title:
                    new_title = new_title.replace(" _ ", " : ")

            else:
                new_title = os.path.splitext(filename)[0]

            new_title = self._clean_audio_title(new_title)

            command: List[str] = [
                "ffmpeg",
                "-y",
                "-i",
                input_path,
                "-map_metadata",
                "0",
                "-metadata",
                f"title={new_title}",
                "-c",
                "copy",
                output_path,
            ]

            try:
                print(f"Modification de '{original_title}' -> '{new_title}'")
                subprocess.run(command, check=True, capture_output=True)
                os.replace(output_path, input_path)
            except subprocess.CalledProcessError as e:
                print(f"Erreur sur {filename}: {e.stderr}")
