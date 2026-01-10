import os
import subprocess
from typing import Any, List
from pathlib import Path
import shutil
from audiobook.metadata import MetadataAudiobook


class M4bTagger:
    def __init__(self, parts: List[Path], metadata: MetadataAudiobook, cover: str):
        self.parts = parts
        self.metadata = metadata
        self.cover = cover

    def run(self) -> list[str]:
        files: list[str] = []

        i = 1
        for part in self.parts:
            tags = self.__handle_tags(self.metadata.tags_standard(i))
            input_file = self.__tag_file(part, tags)
            self.__cover_file(input_file, self.cover)
            files.append(input_file)
            i = i + 1

        return files

    def __handle_tags(self, tags: dict[str, Any]):
        items: list[str] = []
        for k, v in tags.items():
            item = self.__add_tag(k, v)
            if item:
                items.extend(item)

        return items

    def __add_tag(self, key: str, value: Any):
        if value:
            return ["-metadata", f"{key}={str(value)}"]

    def __cover_file(self, input_file: str, cover_image: str):
        """
        Applique une cover et remplace le fichier original.
        """
        input_path = Path(input_file)
        cover_path = Path(cover_image)
        # On crée un nom temporaire pour le travail de FFmpeg
        temp_output = input_path.with_suffix(".tmp.m4b")

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-i",
            str(cover_path),
            "-map",
            "0:a",
            "-map",
            "1:v",
            "-c",
            "copy",
            "-disposition:v:0",
            "attached_pic",
            "-map_chapters",
            "0",
            str(temp_output),
        ]

        try:
            # 1. Exécution de FFmpeg
            subprocess.run(cmd, check=True, capture_output=True)

            # 2. Remplacer l'original par le nouveau fichier
            temp_output.replace(input_path)
            print(f"Cover mise à jour pour : {input_path.name}")

        except subprocess.CalledProcessError as e:
            if temp_output.exists():
                temp_output.unlink()  # Nettoyage en cas d'échec
            print(f"Erreur lors de l'ajout de la cover : {e.stderr.decode()}")
            raise

    def __tag_file(self, file_path: Path, tags: list[str]) -> str:
        """
        Combine FFmpeg (pour la structure) et Mutagen (pour les tags spéciaux).
        """

        target_path = f"{file_path}.tagged.m4b"
        # target_path = output_path if output_path else f"{self.input_path}.tagged.m4b"
        # is_inplace = output_path is None

        cmd: list[str] = [
            "ffmpeg",
            "-y",
            "-i",
            str(file_path),
            "-map_metadata",
            "0",
            "-c",
            "copy",
        ]
        cmd.extend(tags)
        cmd.append(target_path)

        try:
            subprocess.run(
                cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            # if is_inplace and os.path.exists(target_path):
            #     os.remove(target_path)
            if os.path.exists(target_path):
                os.remove(target_path)
            raise RuntimeError(f"FFmpeg failed: {e.stderr.decode()}")

        # 5. Remplacement si in-place
        # if is_inplace:
        shutil.move(target_path, file_path)

        return str(file_path)

        # return target_path
