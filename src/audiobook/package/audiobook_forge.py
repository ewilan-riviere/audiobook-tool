import subprocess
import os
from pathlib import Path


class AudiobookForge:
    def __init__(self, mp3_directory: str):
        self.mp3_directory = mp3_directory
        parent = Path(mp3_directory).name
        self.m4b_file = f"{self.mp3_directory}/{parent}.m4b"
        self.size = 0
        self.size_human: str = "0 B"

    def remove(self):
        if Path(self.m4b_file).is_file():
            os.remove(self.m4b_file)

    def __convert_size(self):
        """Convert bytes to human readable format."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if self.size < 1024:
                return f"{self.size:.2f} {unit}"
            self.size /= 1024
        return f"{self.size:.2f} PB"

    def execute(self):
        try:
            result = subprocess.run(
                [
                    "audiobook-forge",
                    "build",
                    "--root",
                    self.mp3_directory,
                ],
                check=True,
            )
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Le binaire a échoué avec le code : {e.returncode}")

        if Path(self.m4b_file).is_file():
            self.size = os.path.getsize(self.m4b_file)
            self.size_human = self.__convert_size()
        else:
            print(f"ERROR: M4B not found at {self.m4b_file}")

        return self
