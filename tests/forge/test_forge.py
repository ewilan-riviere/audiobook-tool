from src.audiobook.forge import AudiobookForge
import src.audiobook.utils as utils


def test_forge():
    mp3_dir = "./tests/media/the-wall"
    print("forge")
    forge = AudiobookForge(mp3_dir, True)
    forge = forge.build()
    print(forge)

    assert utils.file_exists(forge.m4b_file) is True
