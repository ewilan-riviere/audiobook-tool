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

> [!TIP]
> Built to be used with [audiobookshelf](https://www.audiobookshelf.org/).

## Why?

I used [Audiobook Builder](https://www.splasm.com/audiobookbuilder/) a lot. It was very handy for creating audiobooks from MP3 files and inserting metadata for [audiobookshelf](https://www.audiobookshelf.org/).

However, Audiobook Builder is not free, and it creates separate audiobooks in several parts if necessary (which I appreciate for streaming), but with chapters that can be split up.

So I needed a tool that creates an audiobook in several parts of an adjustable size, that doesn't split the chapters, and that adapts to a YAML file for metadata. As a bonus, this tool could also parse Audible to retrieve metadata from the website...

## Features

- Fetch metadata from Audible from ASIN code
- Build M4B multi-part/one audiobook from MP3/M4A files
- Extract chapters from audiobook and convert to M4A/MP3
- Parse audiobook to convert tags to YAML file

## Docker

### Docker compose (recommanded)

```sh
docker compose up -d
```

### Docker run

```sh
docker build -t audiobook-tool .
```

```sh
docker run -it \
  -v "$(pwd):/app/data" \
  --env-file .env \
  audiobook-tool
```

## Using as CLI

With [`uv`](https://docs.astral.sh/uv/)

```sh
uv sync
```

Or with `pip`

```sh
pip install -e .
```

Use `audiobook-tool` CLI

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
