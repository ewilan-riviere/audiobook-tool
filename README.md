<p align="center">
  <picture>
    <source srcset="./public/logo-small.webp">
    <img alt="Tailwind CSS" src="./public/logo-small.webp" height="200" style="max-width: 100%;">
  </picture>
</p>

<p align="center">
  Ultimate Python CLI to handle audiobooks.
</p>

<p align="center">
    <a href="https://www.python.org/"><img src="https://img.shields.io/static/v1?style=flat&label=Python&message=v3.12&color=3776AB&logo=python&logoColor=ffffff&labelColor=18181b" alt="Python version"></a>
    <a href="https://github.com/ewilan-riviere/audiobook-tool/blob/main/LICENSE"><img src="https://img.shields.io/static/v1?style=flat&label=License&message=MIT&color=3776AB&labelColor=18181b" alt="License"></a>
    <a href="https://gitlab.com/kiwilan/audiobook-tool/-/pipelines"><img src="https://gitlab.com/kiwilan/audiobook-tool/badges/main/pipeline.svg" alt="Build Status"></a>
</p>

---

> [!IMPORTANT]
> Not ready for production.

## Features

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

## License

[MIT License](https://github.com/ewilan-riviere/audiobook-tool/blob/main/LICENSE)
