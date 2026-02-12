from pathlib import Path
from audiobook.yml import YmlReader


def test_reader():
    template_path = "./metadata.template.yml"
    reader = YmlReader(template_path).read()

    assert reader.yml_path == Path(
        "/Users/ewilan/Workspace/audiobook-tool/metadata.template.yml"
    )
    assert isinstance(reader.yml_data, dict)
    assert reader.yml_data.get("title") == "The Fellowship of the Ring"
    assert reader.default_title == "audiobook-tool"

    metadata = reader.metadata

    assert metadata
    assert metadata.title == "The Fellowship of the Ring"
    assert metadata.authors == "J.R.R. Tolkien & Christopher Tolkien"
    assert metadata.narrators == "Rob Inglis & Andy Serkis"
    assert isinstance(metadata.description, str)
    assert isinstance(metadata.lyrics, str)
    assert (
        metadata.copyright
        == "©1954 The Tolkien Estate Limited (P)2025 HarperCollins Publishers Limited"
    )
    assert metadata.genres == "Fantasy/Fiction"
    assert metadata.series == "The Lord of the Rings"
    assert metadata.volume == 1.0
    assert metadata.language == "English"
    assert metadata.year == 2005
    assert metadata.publisher == "HarperCollins Publishers Limited"
    assert metadata.subtitle == "One Ring To Rule Them All"
    assert metadata.isbn == 9780007123827
    assert metadata.asin == "0008487278"

    audiobook = reader.to_audiobook()

    assert audiobook
    assert audiobook.title == "The Fellowship of the Ring"
    assert audiobook.album == "The Fellowship of the Ring"
    assert audiobook.artist == "J.R.R. Tolkien & Christopher Tolkien"
    assert audiobook.album_artist == "J.R.R. Tolkien & Christopher Tolkien"
    assert audiobook.composer == "Rob Inglis & Andy Serkis"
    assert audiobook.genre == "Fantasy/Fiction"
    assert audiobook.date == "2005"
    assert (
        audiobook.copyright
        == "©1954 The Tolkien Estate Limited (P)2025 HarperCollins Publishers Limited"
    )
    assert audiobook.comment is None
    assert isinstance(audiobook.description, str)
    assert isinstance(audiobook.synopsis, str)
    assert audiobook.description == audiobook.synopsis
    assert audiobook.compilation is None
    assert isinstance(audiobook.lyrics, str)
    assert audiobook.publisher == "HarperCollins Publishers Limited"
    assert audiobook.language == "English"
    assert audiobook.series == "The Lord of the Rings"
    assert audiobook.series_part == "1.0"
    assert audiobook.subtitle == "One Ring To Rule Them All"
    assert audiobook.isbn is None
    assert audiobook.asin == "0008487278"
