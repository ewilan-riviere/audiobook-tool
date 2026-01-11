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
        """Extract metadata lines from FFmpeg."""
        result = subprocess.run(
            ["ffmpeg", "-i", self.filepath, "-f", "ffmetadata", "-"],
            check=True,
            capture_output=True,
        )
        # Decode and split into lines immediately
        content = result.stdout.decode("utf-8", errors="replace")
        return content.splitlines()

    def _process_lines(self, lines: List[str]) -> List[str]:
        """Process lines one by one with a robust state machine."""
        new_lines: List[str] = []
        self.original_titles = []
        self.new_titles = []

        counter = 1
        is_inside_chapter = False

        for line in lines:
            # Detect chapter start
            if line.strip() == "[CHAPTER]":
                is_inside_chapter = True
                new_lines.append(line)
                continue

            # Detect title inside a chapter
            if is_inside_chapter and line.startswith("title="):
                # Extract old title
                old_title = line.split("=", 1)[1].strip()
                self.original_titles.append(old_title)

                mp3_file = f"{self.mp3_directory}/{old_title}.mp3"
                mp3_title = utils.get_mp3_title(mp3_file)

                # Create new title
                # new_title = f"{prefix} {counter}"
                new_title = f"{mp3_title}"
                self.new_titles.append(new_title)

                new_lines.append(f"title={new_title}")

                # Reset state until next [CHAPTER]
                is_inside_chapter = False
                counter += 1
            else:
                new_lines.append(line)

        return new_lines

    def _apply_metadata_with_ffmpeg(self) -> None:
        """Injects metadata while preserving video streams (cover art)."""
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                self.filepath,  # Entrée 0 : Fichier original
                "-i",
                self.meta_file,  # Entrée 1 : Nouveau fichier metadata
                "-map",
                "0",  # <--- COPIE TOUS les flux (audio, vidéo/cover, sous-titres)
                "-map_metadata",
                "1",  # Utilise les métadonnées globales du fichier texte
                "-map_chapters",
                "1",  # Force l'utilisation des chapitres du fichier texte
                "-c",
                "copy",  # Copie sans ré-encodage
                "-disposition:v:0",
                "attached_pic",  # S'assure que l'image est bien marquée comme pochette
                self.temp_output,
                "-y",
            ],
            check=True,
            capture_output=True,
        )

    def run(self):
        try:
            print(f"Reading: {self.filename}...")
            lines = self._extract_metadata()

            # --- DEBUG: Uncomment to see the raw metadata if it fails ---
            # print("\n".join(lines[:20]))

            updated_lines = self._process_lines(lines)

            if not self.original_titles:
                print(
                    "❌ No chapters found! FFmpeg might be using a different metadata format."
                )
                return

            # Save modified meta
            with open(self.meta_file, "w", encoding="utf-8") as f:
                f.write("\n".join(updated_lines) + "\n")

            # Inject
            print("Applying changes...")
            self._apply_metadata_with_ffmpeg()

            # Swap files
            os.remove(self.filepath)
            os.rename(self.temp_output, self.filepath)

            self._print_summary()

        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            if os.path.exists(self.meta_file):
                os.remove(self.meta_file)

    def _print_summary(self):
        print(f"\n✅ Success! {len(self.original_titles)} chapters renamed.")
        for i, (old, new) in enumerate(zip(self.original_titles, self.new_titles), 1):
            print(f"  {i:02d}: {old} -> {new}")
