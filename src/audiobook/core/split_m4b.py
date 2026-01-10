from typing import List, Dict, Any, Union
import subprocess
import json
import sys
from pathlib import Path
import shutil
import os
from audiobook.models import AudiobookMetadata
from .m4b_tagger import M4bTagger


class SplitM4b:
    def __init__(self, m4b_file: str, metadata: AudiobookMetadata | None):
        self.m4b_file = m4b_file

        self.default_target_size_mb: int = 600
        self.ffmpeg_log_level: str = "error"
        self.output_folder_suffix: str = "_parts"

        self.output_directory: str = "cover_temp.jpg"
        self.chapters: List[Dict[str, Any]] = []
        self.temp_cover = ""
        self.total_size: int = 0
        self.total_duration: float = 0
        self.target_duration: float = 0
        self.current_part: int = 1
        self.start_time: float = 0

        self.__handle_paths()
        self.metadata = metadata

    def execute(self) -> None:
        metadata: Dict[str, Any] = self.__get_metadata()
        self.chapters = metadata.get("chapters", [])

        has_cover: bool = self.__extract_cover()
        self.__handle_total_size(metadata)

        bitrate: float = self.total_size / self.total_duration
        self.target_duration: float = (
            self.default_target_size_mb * 1024 * 1024
        ) / bitrate

        self.current_part: int = 1
        self.start_time: float = float(self.chapters[0]["start_time"])

        print("")
        parts: list[Path] = []
        for i, chap in enumerate(self.chapters):
            part_path = self.__set_chapter(chap, i, has_cover)
            if part_path:
                parts.append(part_path)

        print("")
        i = 1
        for part in parts:
            print(f" -> Tagging {part.name}...")
            tagger = M4bTagger(str(part), self.metadata)
            tagger.tag_file(track=i)
            i = i + 1

        print("")
        if self.metadata and self.metadata.title:
            i = 1
            for part in parts:
                new_name = f"{self.metadata.title}_Part{i:02d}"
                print(f" -> Rename {part.name} to {new_name}...")
                tagger = M4bTagger(str(part), self.metadata)
                self.__rename(str(part), new_name)
                i = i + 1

        os.remove(self.temp_cover)
        if self.metadata and self.metadata.title and len(parts) > 0:
            self.__rename_parent_directory(str(parts[0]), self.metadata.title)

    def __rename(self, absolute_path: str, new_name_no_ext: str) -> Union[Path, None]:
        # Convert string input to a Path object
        file_path = Path(absolute_path)

        if not file_path.exists():
            print(f"Error: The file at {absolute_path} does not exist.")
            return None

        # Get the original extension (e.g., '.pdf' or '.csv')
        extension = file_path.suffix

        # Create the new path using with_name
        # with_name replaces the filename part but keeps the parent directory
        new_file_path = file_path.with_name(f"{new_name_no_ext}{extension}")

        try:
            # Perform the rename
            file_path.rename(new_file_path)
            return new_file_path
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def __set_chapter(self, chapter: Dict[str, Any], i: int, has_cover: bool):
        chap_end: float = float(chapter["end_time"])
        current_chunk_duration: float = chap_end - self.start_time

        if (
            current_chunk_duration >= self.target_duration
            or i == len(self.chapters) - 1
        ):
            part_name: str = (
                f"{Path(self.m4b_file).stem}_Part{self.current_part:02d}.m4b"
            )
            output_path: Path = Path(self.output_directory) / part_name
            print(f" -> Generating {part_name}...")

            ffmpeg_cmd: List[str] = ["ffmpeg", "-y", "-v", self.ffmpeg_log_level]
            ffmpeg_cmd += [
                "-ss",
                str(self.start_time),
                "-to",
                str(chap_end),
                "-i",
                str(self.m4b_file),
            ]

            if has_cover:
                ffmpeg_cmd += ["-i", str(self.temp_cover)]

            ffmpeg_cmd += ["-map", "0:a"]

            if has_cover:
                ffmpeg_cmd += ["-map", "1:0"]  # Map the JPEG to the second stream

            ffmpeg_cmd += [
                "-c",
                "copy",
                "-disposition:v",
                "attached_pic",
                "-f",
                "ipod",  # Force le format conteneur compatible Apple/Audiobooks
                "-map_metadata",
                "0",
                str(output_path),
            ]

            subprocess.run(ffmpeg_cmd, check=True)

            if i < len(self.chapters) - 1:
                self.start_time = float(self.chapters[i + 1]["start_time"])
                self.current_part += 1

            return output_path

    def __handle_total_size(self, metadata: Dict[str, Any]):
        try:
            self.total_size: int = int(metadata["format"]["size"])
            self.total_duration: float = float(metadata["format"]["duration"])
        except (KeyError, ValueError):
            return

    def __handle_paths(self):
        input_file: Path = Path(self.m4b_file)  # /path/to/audiobook.m4b
        if not input_file.exists():
            print(f"File not found: {input_file}")
            return

        script_root: Path = Path(input_file).parent.resolve()
        output_directory: Path = (
            script_root / f"{input_file.stem}{self.output_folder_suffix}"
        )
        self.output_directory = str(output_directory)

        if output_directory.exists():
            shutil.rmtree(self.output_directory)
        output_directory.mkdir(parents=True, exist_ok=True)

        temp_cover: Path = Path(self.output_directory) / "cover_temp.jpg"
        self.temp_cover = str(temp_cover)

    def __get_metadata(self) -> Dict[str, Any]:
        """Extract metadata and chapter list using ffprobe."""
        cmd: List[str] = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_chapters",
            str(self.m4b_file),
        ]
        try:
            result = subprocess.check_output(cmd)
            return json.loads(result.decode("utf-8"))
        except subprocess.CalledProcessError as e:
            print(f"Error analyzing file: {e}")
            sys.exit(1)

    def __extract_cover(self) -> bool:
        """Extracts cover art specifically to a JPEG file."""

        # We try to extract any video stream (the cover) to a file
        cmd: List[str] = [
            "ffmpeg",
            "-y",
            "-v",
            "quiet",
            "-i",
            str(self.m4b_file),
            "-vframes",
            "1",
            "-q:v",
            "2",
            str(self.temp_cover),
        ]
        try:
            subprocess.run(cmd, check=True)
            return Path(self.temp_cover).exists()
        except subprocess.CalledProcessError:
            return False

    def __rename_parent_directory(
        self, file_absolute_path: str, new_parent_name: str
    ) -> Union[Path, None]:
        """
        Renames the parent directory of a given file path.

        Args:
            file_absolute_path: The full path to a file inside the folder to rename.
            new_parent_name: The new name for the parent folder.

        Returns:
            The new Path to the file inside the renamed folder.
        """
        file_path = Path(file_absolute_path)
        parent_dir = file_path.parent

        if not parent_dir.exists():
            print(f"Error: The directory {parent_dir} does not exist.")
            return None

        # Define the new path for the directory
        # .with_name() on the parent object changes the folder name itself
        new_parent_path = parent_dir.with_name(new_parent_name)

        try:
            # Rename the directory
            parent_dir.rename(new_parent_path)

            # Reconstruct the path to the file in the new location
            new_file_path = new_parent_path / file_path.name

            print(f"Directory renamed: {parent_dir.name} -> {new_parent_name}")
            print(f"New file location: {new_file_path}")

            return new_file_path

        except FileExistsError:
            print(f"Error: A folder named '{new_parent_name}' already exists.")
        except Exception as e:
            print(f"An error occurred: {e}")

        return None
