"""Primary conversion manager with real-time logging."""

import os
from pathlib import Path
from typing import List, Dict, cast
from concurrent.futures import as_completed, Future
from concurrent.futures.process import ProcessPoolExecutor
from mutagen.mp3 import MP3, MPEGInfo
from .audio_chapter import AudioChapter
from .ffmpeg_runner import FFmpegRunner
from .audiobook_fixer import AudiobookFixer


class AudiobookBlacksmith:
    """Primary conversion manager with real-time logging."""

    def __init__(self, directory_path: str):
        self.directory = Path(directory_path).resolve()
        self.chapters: List[AudioChapter] = []
        self.target_bitrate: str = "128k"
        self.output_path = self.directory / f"{self.directory.name}.m4b"
        self.meta_path = self.directory / "metadata.txt"
        self.list_path = self.directory / "inputs.txt"

        if Path(self.output_path).exists():
            os.remove(self.output_path)

    def _prepare_data(self) -> None:
        """Initializes the chapter list, calculates the bitrate, and extracts titles from tags."""
        mp3_files = sorted(list(self.directory.glob("*.mp3")), key=lambda x: x.name)
        if not mp3_files:
            raise FileNotFoundError(f"Aucun fichier MP3 trouvé dans {self.directory}")

        total_bitrate: int = 0
        file_count: int = 0

        for f in mp3_files:
            audio = MP3(f)
            info = cast(MPEGInfo, audio.info)

            # 1. Gestion du Bitrate
            current_br = int(getattr(info, "bitrate", 128000))
            total_bitrate += current_br
            file_count += 1

            # 2. Extraction du titre (Tag 'TIT2' ou nom de fichier en secours)
            # audio.get("TIT2") renvoie un objet tag, on prend sa première valeur texte
            title_tag = audio.get("TIT2")  # type: ignore
            chapter_title = str(title_tag[0]) if title_tag else f.stem  # type: ignore

            # Nettoyage optionnel : si le tag est vide ou juste des espaces
            if not chapter_title.strip():
                chapter_title = f.stem

            self.chapters.append(
                AudioChapter(
                    source_path=f,
                    temp_aac_path=f.with_suffix(".m4a"),
                    title=chapter_title,
                )
            )

        # avg_bitrate = int(total_bitrate / file_count)
        avg_bitrate = min(int(total_bitrate / file_count), 192000)
        self.target_bitrate = f"{int(avg_bitrate / 1000)}k"

        print(f"🔍 Analyze: {file_count} files. Average bitrate: {self.target_bitrate}")

    def _write_assets(self) -> None:
        """Generates metadata files with path escaping."""
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

                # IMPORTANT: FFmpeg concat needs single quotes escaped for filenames
                # We replace ' with '\' (FFmpeg escape sequence)
                escaped_name = chap.temp_aac_path.name.replace("'", "'\\''")
                f_list.write(f"file '{escaped_name}'\n")

        self.meta_path.write_text("\n".join(metadata_lines), encoding="utf-8")

    def _cleanup(self) -> None:
        for path in [self.meta_path, self.list_path]:
            if path.exists():
                path.unlink()
        for chap in self.chapters:
            if chap.temp_aac_path.exists():
                chap.temp_aac_path.unlink()

    def process(self) -> None:
        """Start parallel encoding and final merging."""
        try:
            self._prepare_data()
            total = len(self.chapters)
            print(f"🚀 Encoding of {total} files on {os.cpu_count()} cores...")

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
                        print(f"  ✅ [{completed}/{total}] Done: {filename}")
                    except Exception as e:
                        print(f"  ❌ Error on {filename}: {e}")
                        raise

            print("📦 Final merger and creation of chapters...")
            self._write_assets()
            FFmpegRunner.merge_to_m4b(self.list_path, self.meta_path, self.output_path)
            print(f"✨ Successfully completed: {self.output_path.name}")

        except Exception as e:
            print(f"\n💥 Process failure : {e}")
        finally:
            print("🧹 Cleaning temporary files...")
            self._cleanup()

    def validate(self) -> None:
        """Validate M4B with ffmpeg and mutagen"""
        try:
            fixer = AudiobookFixer(str(self.output_path))

            fixed_path = fixer.fix_structure()
            if fixer.verify_with_mutagen(fixed_path):
                print("🚀 File is now fully compatible with Mutagen!")
                fixer.replace()

        except Exception as error:
            print(f"Critical failure: {error}")
