"""Clean track titles from M4B files"""

from audiobook.m4b import M4bChapterEditor
import audiobook.utils as utils


class CleanTrackTitles:
    """Clean track titles from M4B files"""

    def __init__(self, m4b_directory: str, mp3_directory: str):
        print("Clean track titles...")
        self.m4b_directory = m4b_directory
        self.mp3_directory = mp3_directory
        self.m4b_list = utils.get_files(self.m4b_directory, "m4b")
        self.mp3_list = utils.get_files(self.mp3_directory, "mp3")

    def edit(self) -> None:
        """
        Modifie le titre des fichiers M4B dans un répertoire donné.
        """
        for m4b in self.m4b_list:
            editor = M4bChapterEditor(m4b, self.mp3_directory)
            editor.run()
