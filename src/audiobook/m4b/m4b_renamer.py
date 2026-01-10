"""Rename M4B with name from metadata"""

from pathlib import Path
import shutil
from audiobook.metadata import MetadataAudiobook


class M4bRenamer:
    """Rename M4B with name from metadata"""

    def __init__(self, m4b_files: list[str], metadata: MetadataAudiobook):
        self.m4b_files = m4b_files
        self.metadata = metadata

        self.__rename_files()

        first_file = self.m4b_files[0]
        first_file_parent = Path(first_file).parent
        self.__rename_directory(str(first_file_parent), self.metadata.title)

    def __rename_files(self):
        i = 1
        for file in self.m4b_files:
            self.__rename_file(file, f"{self.metadata.title}_Part{i:02d}")
            i = i + 1

    def __rename_file(self, absolute_path: str, new_name: str) -> str:
        """
        Renomme un fichier en gardant son dossier d'origine et son extension.

        :param absolute_path: Chemin complet du fichier (ex: /home/user/music/audio.m4b)
        :param new_name: Nouveau nom sans extension (ex: mon_livre_audio)
        :return: Le nouveau chemin absolu sous forme de chaîne
        """
        path = Path(absolute_path)

        # .with_name remplace le nom complet (nom + extension)
        # On ajoute donc l'extension d'origine (.suffix) au nouveau nom
        new_path = path.with_name(new_name + path.suffix)

        if new_path.exists():
            new_path.unlink()

        # Effectue le renommage réel sur le disque
        path.rename(new_path)

        return str(new_path.resolve())

    def __rename_directory(self, absolute_path: str, new_name: str) -> str:
        """
        Renomme un répertoire en gardant son emplacement d'origine.

        :param absolute_path: Chemin complet du dossier (ex: /path/to/my_folder)
        :param new_name: Nouveau nom du dossier
        :return: Le nouveau chemin absolu sous forme de chaîne
        """
        path = Path(absolute_path)

        # On remplace simplement le dernier composant du chemin par le nouveau nom
        new_path = path.with_name(new_name)

        if new_path.exists():
            shutil.rmtree(new_path)

        # Renommage effectif
        path.rename(new_path)

        return str(new_path.resolve())
