# Audiobook Tool

[![python][python-src]][python-href]

Python CLI to handle audiobooks.

> [!IMPORTANT]
> Not ready for production.

- Build from MP3
- Extract from M4B
- Fusion MP3 to M4B
- Fetch metadata

## Using as CLI

```sh
pip install -e .
```

```sh
audiobook-tool build ./path/to/mp3_directory
```

## Test

Test CLI

```sh
pytest
```

Or verbose

```sh
pytest -s
pytest -s tests/audio/test_reader.py
```

[python-src]: https://img.shields.io/static/v1?style=flat&label=Python&message=v3.12&color=3776AB&logo=python&logoColor=ffffff&labelColor=18181b
[python-href]: https://www.python.org/
