import subprocess
from pathlib import Path
from audiobook import utils
from audiobook.models import ContainerAudiobook


class M4bExtractor:
    def __init__(self, container: ContainerAudiobook, output_format: str = "mp3"):
        self.container = container
        self.output_dir = container.audiobook_path / "extracted_chapters"
        self.output_format = output_format

        utils.remove_directory(self.output_dir)
        utils.make_directory(self.output_dir)

    def extract(self, to_mp3: bool = False, high_fidelity: bool = False):
        total_chapters = len(self.container.chapters)
        divider = "=" * 60

        print(f"\n{divider}")
        print("🚀 ÉTAPE 1 : Extraction M4A (Stream Copy)")
        print(f"🔢 Chapitres à traiter : {total_chapters}")
        print(f"{divider}\n")

        extracted_files: list[Path] = []
        self._to_m4a(extracted_files, total_chapters)

        if to_mp3:
            self._to_mp3(extracted_files, total_chapters, high_fidelity)

        print(f"\n✅ Terminé ! Fichiers dans : {self.output_dir}")
        return self

    def _to_m4a(
        self,
        extracted_files: list[Path],
        total_chapters: int,
    ):
        current_m4b_index = 0

        for i, chapter in enumerate(self.container.chapters):
            if i > 0 and chapter.id == 0:
                current_m4b_index += 1

            input_file = self.container.m4b_files[current_m4b_index]

            raw_title = chapter.tags.get("title", f"Chapter_{i}")
            clean_title = "".join(
                [c for c in raw_title if c.isalnum() or c in (" ", "-", "_")]
            ).strip()

            m4a_path = self.output_dir / f"{i + 1:02d} - {clean_title}.m4a"

            print(
                f"[{((i + 1) / total_chapters) * 100:6.2f}%] 🛠  Extraction : {m4a_path.name}"
            )
            self._ffmpeg_copy(
                input_file, chapter.start_time, chapter.end_time, m4a_path
            )

            extracted_files.append(m4a_path)

    def _to_mp3(
        self,
        extracted_files: list[Path],
        total_chapters: int,
        high_fidelity: bool = True,
    ):
        divider = "=" * 60
        print(f"\n{divider}")
        print("🚀 ÉTAPE 2 : Conversion MP3 (Lame Encodage)")
        print(f"{divider}\n")

        for i, m4a_path in enumerate(extracted_files):
            mp3_path = m4a_path.with_suffix(".mp3")

            if high_fidelity:
                audio_params = ["-q:a", "0"]
                mode_info = "HIFI (V0)"
            else:
                audio_params = self._get_match_source_params(m4a_path)
                mode_info = f"Match Source ({audio_params[1]})"

            progress = ((i + 1) / total_chapters) * 100
            print(f"[{progress:6.2f}%] 🔄 Conversion : {mp3_path.name} [{mode_info}]")
            self._ffmpeg_convert_to_mp3(m4a_path, mp3_path, audio_params)
            m4a_path.unlink()

    def _ffmpeg_copy(self, input_path: Path, start: str, end: str, output_path: Path):
        """Découpe sans ré-encoder (Stream Copy)."""
        command = [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-ss",
            str(start),
            "-to",
            str(end),
            "-i",
            str(input_path),
            "-map",
            "0:a:0",
            "-c:a",
            "aac",  # On ré-encode en AAC au lieu de 'copy'
            "-b:a",
            "192k",  # Bitrate solide pour préserver la source
            "-map_metadata",
            "-1",
            "-vn",
            "-sn",
            "-dn",
            str(output_path),
        ]
        subprocess.run(command, check=True)

    def _ffmpeg_convert_to_mp3(
        self,
        input_path: Path,
        output_path: Path,
        audio_params: list[str],
    ):
        """Exécute la conversion avec les paramètres injectés."""
        command = [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(input_path),
            "-codec:a",
            "libmp3lame",
            *audio_params,
            str(output_path),
        ]
        subprocess.run(command, check=True)

    def _get_match_source_params(self, input_path: Path) -> list[str]:
        """
        Analyse le fichier source pour retourner les arguments de bitrate MP3 adaptés.
        """
        try:
            cmd = [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=bit_rate",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(input_path),
            ]
            res = subprocess.run(cmd, check=True, capture_output=True, text=True)

            # Conversion en entier (bps)
            source_br = int(res.stdout.strip())

            # Calcul : Bitrate source * 1.2 pour compenser l'efficacité moindre du MP3
            # On arrondit au kbps et on plafonne à 320k
            target_kbps = min(int(source_br * 1.2) // 1000, 320)

            return ["-b:a", f"{target_kbps}k"]
        except Exception:
            # Fallback sécurisé : Qualité VBR 4 (environ 160kbps)
            return ["-q:a", "4"]
