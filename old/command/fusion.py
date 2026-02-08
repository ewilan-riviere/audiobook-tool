"""fusion command of audiobook-tool"""

from pathlib import Path
from audiobook.args import AudiobookArgs


class CommandFusion:
    """fusion command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        m4b_directory = Path(str(args.m4b_directory))
        mp3_directory = Path(str(args.mp3_directory))

        if not m4b_directory.exists() or not mp3_directory.exists():
            print("Erreur : L'un des répertoires n'existe pas.")
            return

        print("--- Début de la fusion ---")
        print(f"Base : {m4b_directory}")
        print(f"Ajouts : {mp3_directory}")
