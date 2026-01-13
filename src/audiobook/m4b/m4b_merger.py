import os
from typing import List, Optional
import ffmpeg  # type: ignore
from mutagen.mp4 import MP4
from audiobook.metadata import MetadataFile
from audiobook.config import ConfigExtract


class M4BMerger:
    def __init__(self, config: ConfigExtract):
        self._file_paths: List[str] = config.m4b_list
        self._files_metadata: List[MetadataFile] = config.m4b_metadata
        self._temporary_directory: str = config.temporary_directory_path

    def _sort_files(self) -> List[MetadataFile]:
        return sorted(
            self._files_metadata,
            key=lambda x: (x.track is None, x.track, str(x.path).lower()),
        )

    def merge(self, output_filename: str = "merged_audiobook.m4b") -> Optional[str]:
        sorted_list = self._sort_files()
        sorted_paths = [os.path.abspath(f.path) for f in sorted_list]

        if not sorted_paths:
            return None

        output_path = os.path.join(self._temporary_directory, output_filename)
        concat_list_path = os.path.join(self._temporary_directory, "concat_list.txt")
        meta_file_path = os.path.join(
            self._temporary_directory, "metadata_chapters.txt"
        )

        try:
            # 1. FFmpeg Concat List
            with open(concat_list_path, "w", encoding="utf-8") as f:
                for path in sorted_paths:
                    f.write(f"file '{path.replace("'", "'\\''")}'\n")

            # 2. Rebuild Chapters
            self._generate_merged_metadata(sorted_paths, meta_file_path)

            # 3. FFmpeg Merge
            input_audio = ffmpeg.input(concat_list_path, format="concat", safe=0)  # type: ignore
            (
                ffmpeg.output(  # type: ignore
                    input_audio["a"], output_path, c="copy", map_metadata=1, vn=None  # type: ignore
                )
                .global_args("-i", meta_file_path)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )

            # 4. RESTORE CUSTOM ATOMS / TAGS
            # On copie les tags du premier fichier source vers le fichier fusionné
            self._copy_mp4_atoms(sorted_paths[0], output_path)

            print(f"Successfully merged: {output_path}")
            return output_path

        except ffmpeg.Error as e:
            print(f"FFmpeg Error: {e.stderr.decode() if e.stderr else str(e)}")  # type: ignore
            return None
        finally:
            for p in [concat_list_path, meta_file_path]:
                if os.path.exists(p):
                    os.remove(p)

    def _copy_mp4_atoms(self, source_path: str, destination_path: str) -> None:
        """
        Copies all MP4 tags (atoms) including custom ones from source to destination.
        """
        try:
            source = MP4(source_path)
            destination = MP4(destination_path)

            # On copie tous les tags (dictionnaire de clés/valeurs)
            # source.tags contient les atomes comme '\xa9nam' (titre), 'aART' (album artist), etc.
            for key, value in source.tags.items():  # type: ignore
                destination.tags[key] = value  # type: ignore

            destination.save()  # type: ignore
        except Exception as e:
            print(f"Warning: Failed to copy custom atoms: {e}")

    def _generate_merged_metadata(
        self, paths: List[str], output_meta_path: str
    ) -> None:
        """Creates a FFMETADATA1 file with recalculated chapters."""
        metadata_content = [";FFMETADATA1"]
        cumulative_offset_ns = 0

        for path in paths:
            probe = ffmpeg.probe(path, show_chapters=None)  # type: ignore
            chapters = probe.get("chapters", [])
            duration_s = float(probe.get("format", {}).get("duration", 0))
            duration_ns = int(duration_s * 1_000_000_000)

            for chap in chapters:
                tb_num, tb_den = map(int, chap["time_base"].split("/"))
                start_ns = int(int(chap["start"]) * tb_num * 1_000_000_000 / tb_den)
                end_ns = int(int(chap["end"]) * tb_num * 1_000_000_000 / tb_den)
                title = chap.get("tags", {}).get("title", "Unknown Chapter")

                metadata_content.append("\n[CHAPTER]")
                metadata_content.append("TIMEBASE=1/1000000000")
                metadata_content.append(f"START={cumulative_offset_ns + start_ns}")
                metadata_content.append(f"END={cumulative_offset_ns + end_ns}")
                metadata_content.append(f"title={title}")

            cumulative_offset_ns += duration_ns

        with open(output_meta_path, "w", encoding="utf-8") as f:
            f.write("\n".join(metadata_content))
