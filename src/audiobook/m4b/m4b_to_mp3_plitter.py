import os
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor  # pylint: disable=no-name-in-module
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK  # type: ignore
import ffmpeg  # type: ignore


class M4BToMP3Splitter:
    def __init__(
        self,
        m4b_path: str,
        output_dir: Optional[str] = None,
        max_workers: Optional[int] = None,
    ):
        self.m4b_path: str = os.path.abspath(m4b_path)
        self.output_dir: str = (
            output_dir or os.path.splitext(self.m4b_path)[0] + "_split"
        )
        # Utilise le nombre de coeurs CPU par défaut pour la vitesse
        self.max_workers: int = max_workers or (os.cpu_count() or 4)

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _get_metadata(self) -> Dict[str, Any]:
        """Extracts chapters, bitrate, and global tags via ffprobe."""
        probe = ffmpeg.probe(self.m4b_path, show_chapters=None)  # type: ignore
        return {
            "chapters": probe.get("chapters", []),
            "bitrate": probe.get("format", {}).get("bit_rate"),
            "tags": probe.get("format", {}).get("tags", {}),
        }

    def split_and_convert(self) -> List[str]:
        """Main entry point: splits M4B into MP3 chapters using parallel processing."""
        metadata = self._get_metadata()
        chapters: List[Dict[str, Any]] = metadata["chapters"]

        # Conserve le bitrate original
        source_bitrate = metadata["bitrate"]
        bitrate_str: str = (
            f"{int(source_bitrate) // 1000}k" if source_bitrate else "192k"
        )
        global_tags: Dict[str, Any] = metadata["tags"]

        if not chapters:
            # Cas sans chapitres : on crée un dictionnaire fictif pour process_chapter
            return [self._process_chapter({}, 1, bitrate_str, global_tags)]

        print(f"Starting conversion with {self.max_workers} parallel workers...")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # On prépare les tâches pour chaque chapitre
            futures = [
                executor.submit(
                    self._process_chapter, chapter, i, bitrate_str, global_tags
                )
                for i, chapter in enumerate(chapters, start=1)
            ]

        return [f.result() for f in futures]

    def _process_chapter(
        self,
        chapter: Dict[str, Any],
        index: int,
        bitrate: str,
        global_tags: Dict[str, Any],
    ) -> str:
        """Handles the extraction, conversion, and ID3 tagging for a single segment."""
        # Extraction du titre (fallback sur l'index si vide)
        chapter_tags = chapter.get("tags", {})
        title: str = chapter_tags.get("title", f"Chapter {index}")

        # Nettoyage du nom de fichier
        file_name: str = f"{index:03d} - {self._safe_filename(title)}.mp3"
        output_path: str = os.path.join(self.output_dir, file_name)

        # Arguments de découpage si le chapitre existe (non vide)
        input_args: Dict[str, Any] = {}
        if "start_time" in chapter and "end_time" in chapter:
            input_args["ss"] = float(chapter["start_time"])
            input_args["to"] = float(chapter["end_time"])

        try:
            # Conversion vers MP3 via FFmpeg
            (
                ffmpeg.input(self.m4b_path, **input_args)  # type: ignore
                .output(output_path, audio_bitrate=bitrate, vn=None, loglevel="error")
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )

            # Application des tags ID3 pour les lecteurs MP3
            self._apply_id3_tags(output_path, title, index, global_tags)

        except ffmpeg.Error as e:
            print(
                f"FFmpeg conversion error on chapter {index}: "
                f"{e.stderr.decode() if e.stderr else str(e)}"  # type: ignore
            )

        return output_path

    def _apply_id3_tags(
        self, path: str, title: str, index: int, tags: Dict[str, Any]
    ) -> None:
        """Injects metadata into the generated MP3 file."""
        try:
            audio = ID3(path)
            # TIT2: Titre, TPE1: Artiste, TALB: Album, TRCK: Track Number
            audio.add(TIT2(encoding=3, text=title))  # type: ignore
            audio.add(  # type: ignore
                TPE1(encoding=3, text=tags.get("artist", tags.get("author", "Unknown")))
            )
            audio.add(  # type: ignore
                TALB(encoding=3, text=tags.get("album", tags.get("title", "Audiobook")))
            )
            audio.add(TRCK(encoding=3, text=str(index)))  # type: ignore
            audio.save()  # type: ignore
        except Exception as e:
            print(f"Metadata tagging failed for {path}: {e}")

    @staticmethod
    def _safe_filename(name: str) -> str:
        """Sanitizes string for filesystem compatibility."""
        return "".join([c for c in name if c.isalnum() or c in (" ", "-", "_")]).strip()
