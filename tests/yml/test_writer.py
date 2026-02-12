from pathlib import Path
import datetime
from audiobook.yml import YmlReader, YmlWriter
from audiobook.models import AudibleAudiobook


def audible_audiobook() -> AudibleAudiobook:
    audiobook = AudibleAudiobook("2367627002")

    audiobook.url = "https://www.audible.fr/pd/Lil-dOtolep-Livre-Audio/2367627002"
    audiobook.original_title = "L'œil d'Otolep"
    audiobook.subtitle = "Les mondes d'Ewilan 2"
    audiobook.description = (
        "À Gwendalavir, Ewilan se prépare à partir pour Valingaï afin..."
    )
    audiobook.copyright = "©2004 / 2015 / 2017 Rageot Éditeur, Paris (P)2018 Audiolib"
    audiobook.publisher = "Audiolib"
    audiobook.authors = ["Pierre Bottero"]
    audiobook.narrators = ["Kelly Marot"]
    audiobook.published_at = datetime.date(2018, 9, 12)
    audiobook.duration = datetime.time(7, 7)
    audiobook.language = "French"
    audiobook.abridged = False
    audiobook.cover = "https://m.media-amazon.com/images/I/51OqxjVPjNL._SL500_.jpg"
    audiobook.volume = 2.0
    audiobook.part = None
    audiobook.title = "L'œil d'Otolep"
    audiobook.series = "Les mondes d'Ewilan"
    audiobook.original_series = ["Les mondes d'Ewilan"]
    audiobook.format = "Version intégrale Livre audio"
    audiobook.book_format = "AudiobookFormat"
    audiobook.sku = "BK_ODLB_002050FR"
    audiobook.rating = 4.84
    audiobook.price = 9.95
    audiobook.genres = ["Science-fiction", "Science-fiction et fantasy"]
    audiobook.categories = ["Adolescents et jeunes adultes"]

    return audiobook


def test_writer():
    save_path = "./tests/media/output"
    audible = audible_audiobook()

    writer = YmlWriter(audible, save_path).write()

    assert writer.success is True
    assert isinstance(writer.data, dict)
    assert writer.save_path == Path(save_path).resolve() / "metadata.yml"

    reader = YmlReader(writer.save_path).read()

    metadata = reader.metadata
    assert metadata
    assert metadata.title == "L'œil d'Otolep"
    assert metadata.series == "Les mondes d'Ewilan"
    assert metadata.volume == 2.0
