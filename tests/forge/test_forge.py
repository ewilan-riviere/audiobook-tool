from src.audiobook.forge import AudiobookForge
import src.audiobook.utils as utils


def test_forge():
    mp3_dir = "./tests/media/the-wall"
    forge = AudiobookForge(mp3_dir, True)
    forge = forge.build()
    print(forge)

    assert forge.blacksmith
    assert forge.blacksmith.target_bitrate == "128k"
    assert utils.file_exists(forge.m4b_file) is True
