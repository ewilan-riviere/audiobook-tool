from src.audiobook.forge import AudiobookForge
import src.audiobook.utils as utils
from src.audiobook.audio import AudioReader


def test_forge():
    mp3_dir = "./tests/media/the-wall"
    forge = AudiobookForge(mp3_dir, True)
    forge = forge.build()

    assert forge.blacksmith
    assert len(forge.blacksmith.mp3_files) == 2
    assert len(forge.blacksmith.chapters) == 2
    assert forge.blacksmith.target_bitrate == "128k"
    assert utils.file_exists(forge.m4b_file) is True

    reader = AudioReader(forge.m4b_file)
    print(reader)
