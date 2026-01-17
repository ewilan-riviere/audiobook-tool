import os
from pathlib import Path
from typing import List, Dict, cast
from concurrent.futures import as_completed, Future
from concurrent.futures.process import ProcessPoolExecutor
from mutagen.mp3 import MP3, MPEGInfo
from .audio_chapter import AudioChapter
from .ffmpeg_runner import FFmpegRunner


class AudiobookBlacksmith:
    """Gestionnaire principal de conversion avec logging en temps réel."""

    def __init__(self, directory_path: str):
        self.directory = Path(directory_path).resolve()
        self.chapters: List[AudioChapter] = []
        self.target_bitrate: str = "128k"
        self.output_path = self.directory / f"{self.directory.name}.m4b"
        self.meta_path = self.directory / "metadata.txt"
        self.list_path = self.directory / "inputs.txt"

    def _prepare_data(self) -> None:
        mp3_files = sorted(list(self.directory.glob("*.mp3")), key=lambda x: x.name)
        if not mp3_files:
            raise FileNotFoundError(f"Aucun fichier MP3 trouvé dans {self.directory}")

        max_br_observed: int = 0
        for f in mp3_files:
            audio = MP3(f)
            info = cast(MPEGInfo, audio.info)
            current_br = int(getattr(info, "bitrate", 128000))
            max_br_observed = max(max_br_observed, current_br)

            self.chapters.append(
                AudioChapter(
                    source_path=f, temp_aac_path=f.with_suffix(".m4a"), title=f.stem
                )
            )

        self.target_bitrate = f"{int(max_br_observed / 1000)}k"
        print(f"🔍 Analyse terminée. Bitrate cible : {self.target_bitrate}")

    def _write_assets(self) -> None:
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
        for path in [self.meta_path, self.list_path]:
            if path.exists():
                path.unlink()
        for chap in self.chapters:
            if chap.temp_aac_path.exists():
                chap.temp_aac_path.unlink()

    def process(self) -> None:
        """Lance l'encodage parallèle et la fusion finale."""
        try:
            self._prepare_data()
            total = len(self.chapters)
            print(f"🚀 Encodage de {total} fichiers sur {os.cpu_count()} cœurs...")

            future_to_file: Dict[Future[str], str] = {}

            with ProcessPoolExecutor() as executor:
                # Soumission des fichiers au pool
                for c in self.chapters:
                    future = executor.submit(
                        FFmpegRunner.encode_to_aac,
                        c.source_path,
                        c.temp_aac_path,
                        self.target_bitrate,
                    )
                    future_to_file[future] = c.source_path.name

                # Suivi de l'avancement en temps réel
                completed = 0
                for future in as_completed(future_to_file):
                    filename = future_to_file[future]
                    try:
                        future.result()
                        completed += 1
                        print(f"  ✅ [{completed}/{total}] Terminé : {filename}")
                    except Exception as e:
                        print(f"  ❌ Erreur sur {filename} : {e}")
                        raise

            print("📦 Fusion finale et création des chapitres...")
            self._write_assets()
            FFmpegRunner.merge_to_m4b(self.list_path, self.meta_path, self.output_path)
            print(f"✨ Terminé avec succès : {self.output_path.name}")

        except Exception as e:
            print(f"\n💥 Échec du processus : {e}")
        finally:
            print("🧹 Nettoyage des fichiers temporaires...")
            self._cleanup()
