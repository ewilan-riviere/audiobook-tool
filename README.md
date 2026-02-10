# Audiobook Tool

[![python][python-src]][python-href]
[![pipeline][pipeline-src]][pipeline-href]

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

Run tests:

```sh
pytest
```

To know more about tests, check [docs/tests.md](./public/docs/tests.md)

[python-src]: https://img.shields.io/static/v1?style=flat&label=Python&message=v3.12&color=3776AB&logo=python&logoColor=ffffff&labelColor=18181b
[python-href]: https://www.python.org/
[pipeline-src]: https://gitlab.com/kiwilan/audiobook-tool/badges/main/pipeline.svg
[pipeline-href]: https://gitlab.com/kiwilan/audiobook-tool/-/pipelines
