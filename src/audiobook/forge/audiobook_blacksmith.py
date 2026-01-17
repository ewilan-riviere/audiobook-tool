import os
from pathlib import Path
from typing import List, cast
from concurrent.futures.process import ProcessPoolExecutor
from mutagen.mp3 import MP3, MPEGInfo
from .audio_chapter import AudioChapter
from .ffmpeg_runner import FFmpegRunner


class AudiobookBlacksmith:
    """Gestionnaire principal du cycle de vie de la création du livre audio."""

    def __init__(self, directory_path: str):
        self.directory = Path(directory_path).resolve()
        self.chapters: List[AudioChapter] = []
        self.target_bitrate: str = "128k"
        self.output_path = self.directory / f"{self.directory.name}.m4b"
        self.meta_path = self.directory / "metadata.txt"
        self.list_path = self.directory / "inputs.txt"

    def _prepare_data(self) -> None:
        """Scanne le dossier et définit les paramètres d'encodage."""
        mp3_files = sorted(list(self.directory.glob("*.mp3")), key=lambda x: x.name)
        if not mp3_files:
            raise FileNotFoundError(f"Aucun fichier MP3 trouvé dans {self.directory}")

        max_br_observed: int = 0
        for f in mp3_files:
            audio = MP3(f)
            # Cast explicite pour Pylance/Pylint
            info = cast(MPEGInfo, audio.info)
            # Utilisation de getattr pour une robustesse totale face aux types inconnus
            current_br = int(getattr(info, "bitrate", 128000))
            max_br_observed = max(max_br_observed, current_br)

            self.chapters.append(
                AudioChapter(
                    source_path=f, temp_aac_path=f.with_suffix(".m4a"), title=f.stem
                )
            )

        self.target_bitrate = f"{int(max_br_observed / 1000)}k"
        print(f"🔍 Bitrate cible : {self.target_bitrate}")

    def _write_assets(self) -> None:
        """Génère les fichiers texte nécessaires à FFmpeg (liste et chapitres)."""
        metadata_lines = [";FFMETADATA1"]
        current_time_ms = 0

        with open(self.list_path, "w", encoding="utf-8") as f_list:
            for chap in self.chapters:
                duration = chap.load_duration()

                metadata_lines.append(
                    f"\n[CHAPTER]\nTIMEBASE=1/1000\nSTART={current_time_ms}"
                )
                current_time_ms += duration
                metadata_lines.append(f"END={current_time_ms}\ntitle={chap.title}")

                f_list.write(f"file '{chap.temp_aac_path.name}'\n")

        self.meta_path.write_text("\n".join(metadata_lines), encoding="utf-8")

    def _cleanup(self) -> None:
        """Supprime les fichiers temporaires pour laisser le dossier propre."""
        for path in [self.meta_path, self.list_path]:
            if path.exists():
                path.unlink()
        for chap in self.chapters:
            if chap.temp_aac_path.exists():
                chap.temp_aac_path.unlink()

    def process(self) -> None:
        """Exécute la séquence complète de traitement."""
        try:
            self._prepare_data()

            print(f"🚀 Encodage parallèle ({os.cpu_count()} cœurs)...")
            with ProcessPoolExecutor() as executor:
                # Création des tâches d'encodage
                futures = [
                    executor.submit(
                        FFmpegRunner.encode_to_aac,
                        c.source_path,
                        c.temp_aac_path,
                        self.target_bitrate,
                    )
                    for c in self.chapters
                ]
                # Attente des résultats pour capturer les erreurs
                for future in futures:
                    future.result()

            self._write_assets()
            print("📦 Concaténation et injection des chapitres...")
            FFmpegRunner.merge_to_m4b(self.list_path, self.meta_path, self.output_path)
            print(f"✨ Succès ! Fichier créé : {self.output_path.name}")

        except Exception as e:
            print(f"❌ Erreur durant le traitement : {e}")
        finally:
            print("🧹 Nettoyage des fichiers temporaires...")
            self._cleanup()
