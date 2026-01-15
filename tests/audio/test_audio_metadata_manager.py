import pytest
# from pathlib import Path
# from src.audiobook.audio.audio_metadata_manager import AudioMetadataManager


# Fixture pour créer un environnement de test propre
@pytest.fixture
# def temp_audio_file(tmp_path):
#     """Crée un fichier factice simulant un audio."""
#     audio_path = tmp_path / "test_audio.mp3"
#     audio_path.write_bytes(b"fake audio data")
#     return audio_path


# def test_manager_initialization(temp_audio_file):
#     # Arrange
#     manager = AudioMetadataManager(temp_audio_file)

#     # Assert
#     assert manager.file_path == temp_audio_file
#     assert manager.extension == ".mp3"


# def test_update_metadata(temp_audio_file):
#     # Arrange
#     manager = AudioMetadataManager(temp_audio_file)
#     new_metadata = {"title": "Mon Super Livre", "author": "Jean Test"}

#     # Act
#     # Ici, on suppose que ta méthode s'appelle update()
#     manager.update(new_metadata)

#     # Assert
#     # Vérifie que les données internes du manager sont à jour
#     assert manager.get_title() == "Mon Super Livre"
