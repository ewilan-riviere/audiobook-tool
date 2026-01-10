import os
import shutil
import subprocess
from typing import Optional, Any
from mutagen.mp4 import MP4
from audiobook.models import AudiobookMetadata


class M4bTagger:
    def __init__(self, input_path: str, metadata: AudiobookMetadata | None):
        self.input_path = input_path
        self.metadata = metadata

        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"Input file not found: {self.input_path}")

    def _build_ffmpeg_args(self, track: int | None) -> list[str]:
        """
        Gère les tags standards via FFmpeg.
        """
        if not self.metadata:
            return []

        args: list[str] = []

        def add_tag(ffmpeg_key: str, value: Any):
            if value:
                args.extend(["-metadata", f"{ffmpeg_key}={str(value)}"])

        # Tags Standards (bien gérés par FFmpeg en MP4)
        add_tag("title", self.metadata.title)
        add_tag("album", self.metadata.title)
        add_tag("artist", self.metadata.authors)
        add_tag("album_artist", self.metadata.authors)
        add_tag("composer", self.metadata.narrators)
        add_tag("genre", self.metadata.genres)
        add_tag("date", self.metadata.year)
        add_tag("copyright", self.metadata.copyright)
        add_tag("comment", self.metadata.description)
        add_tag("publisher", self.metadata.editor)

        add_tag("description", self.metadata.description)
        add_tag("synopsis", self.metadata.description)

        if track:
            add_tag("track", track)

        return args

    def _apply_custom_atoms(self, file_path: str):
        """
        Force l'écriture des atomes SERIES, SUBTITLE et LANGUAGE via Mutagen.
        C'est cette étape qui rend les tags "non-standards" visibles.
        """
        if not self.metadata:
            return

        audio = MP4(file_path)

        # 1. Langue (Atome standard MP4 ©lan)
        if self.metadata.language:
            # Mutagen attend souvent une liste de strings pour les atomes
            audio["\xa9lan"] = [self.metadata.language]

        # 2. Tags Personnalisés (Format '----:com.apple.iTunes:NOM')
        # Ce format est le standard pour SERIES et SUBTITLE dans le monde du M4B
        custom_mapping: dict[str, Any] = {
            "LANGUAGE": self.metadata.language,
            "SERIES": self.metadata.series,
            "SERIES-PART": self.metadata.volume,
            "SUBTITLE": self.metadata.subtitle,
        }

        for key, value in custom_mapping.items():
            if value:
                atom_key = f"----:com.apple.iTunes:{key}"
                # On encode en UTF-8 pour la compatibilité
                audio[atom_key] = [str(value).encode("utf-8")]

        audio.save()  # type: ignore

    def tag_file(
        self, output_path: Optional[str] = None, track: int | None = None
    ) -> str:
        """
        Combine FFmpeg (pour la structure) et Mutagen (pour les tags spéciaux).
        """
        # 1. Déterminer le chemin de sortie
        target_path = output_path if output_path else f"{self.input_path}.tagged.m4b"
        is_inplace = output_path is None

        # 2. Commande FFmpeg
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            self.input_path,
            "-map_metadata",
            "0",
            "-c",
            "copy",
        ]
        cmd.extend(self._build_ffmpeg_args(track))
        cmd.append(target_path)

        # 3. Exécution FFmpeg
        try:
            subprocess.run(
                cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            if is_inplace and os.path.exists(target_path):
                os.remove(target_path)
            raise RuntimeError(f"FFmpeg failed: {e.stderr.decode()}")

        # 4. Correction avec Mutagen pour les tags non-standards
        self._apply_custom_atoms(target_path)

        # 5. Remplacement si in-place
        if is_inplace:
            shutil.move(target_path, self.input_path)
            return self.input_path

        return target_path
