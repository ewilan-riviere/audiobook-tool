from src.audiobook.forge import AudiobookForge


def test_forge():
    mp3_dir = "./tests/media/the-wall"
    print("forge")
    forge = AudiobookForge(mp3_dir, True)
    forge = forge.build()
    print(forge)
