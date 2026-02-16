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
  Built to be used with <a href="https://www.audiobookshelf.org/" target="_blank">audiobookshelf</a>.
</p>

<p align="center">
    <a href="https://www.python.org/"><img src="https://img.shields.io/static/v1?style=flat&label=Python&message=v3.12&color=3776AB&logo=python&logoColor=ffffff&labelColor=18181b" alt="Python version"></a>
    <a href="https://github.com/ewilan-riviere/audiobook-tool/blob/main/LICENSE"><img src="https://img.shields.io/static/v1?style=flat&label=License&message=MIT&color=3776AB&labelColor=18181b" alt="License"></a>
    <a href="https://gitlab.com/kiwilan/audiobook-tool/-/pipelines"><img src="https://gitlab.com/kiwilan/audiobook-tool/badges/main/pipeline.svg" alt="Build Status"></a>
</p>

---

## Why?

I used [Audiobook Builder](https://www.splasm.com/audiobookbuilder/) a lot. It was very handy for creating audiobooks from MP3 files and inserting metadata for [audiobookshelf](https://www.audiobookshelf.org/).

However, Audiobook Builder is not free, and it creates separate audiobooks in several parts if necessary (which I appreciate for streaming), but with chapters that can be split up.

So I needed a tool that creates an audiobook in several parts of an adjustable size, that doesn't split the chapters, and that adapts to a YAML file for metadata. As a bonus, this tool could also parse Audible to retrieve metadata from the website...

## Features

- 🎧 Fetch metadata from Audible from ASIN code
- 📦 Build M4B multi-part/one audiobook from MP3/M4A files
- 📤 Extract chapters from audiobook and convert to M4A/MP3
- 🔖 Parse audiobook to convert tags to YAML file

## Usage

### Audible

`audible` command will fetch metadata from Audible website (web scraping with [playwright](https://playwright.dev/)) to create `metadata.yml` file and `cover.jpg` file. You need ASIN code available in Audible URL and shortcut for any audiobook, like ASIN code `B0G5SMXT5S` for `https://www.audible.com/pd/B0G5SMXT5S?ipRedirectOverride=true` with _Assassin’s Apprentice (The Farseer Trilogy, Book 1)_ audiobook.

> [!INFO]
> An ASIN code only works on one Audible domain, and the same book has a different ASIN code between the `.com` and `.fr` domains, for example.

```sh
audiobook-tool audible <ASIN_CODE>
```

| Flag       | Alias | Description           | Type  | Default |
| :--------- | :---: | :-------------------- | :---: | :------ |
| `--locale` | `-l`  | Audible domain to use | `str` | `None`  |

If you not set `--locale` flag, CLI will parse all Audible domains to find ASIN audiobook. You can set the `--locale` flag (can be `com`, `co.uk`, `fr`, `de`) to speed up the process.

### Build

`build` command is main command of this CLI. This command will create an `.m4b` audiobook from `.mp3` or `.m4a` source files.

```sh
audiobook-tool build /path/to/source_files
```

| Flag            | Alias | Description                                                  |  Type  | Default |
| :-------------- | :---: | :----------------------------------------------------------- | :----: | :------ |
| `--clear`       | `-c`  | Clear covers from source files                               | `bool` | `False` |
| `--asin`        | `-a`  | ASIN code to fetch Audible metadata before build             | `str`  | `None`  |
| `--locale`      | `-l`  | Audible domain to use                                        | `str`  | `None`  |
| `--output-path` | `-o`  | Path where put audiobook files (default is source directory) | `str`  | `None`  |
| `--single`      | `-s`  | Create only one audiobook (not splitted)                     | `bool` | `False` |
| `--part-size`   | `-p`  | Size of each part\* in MB (default use `.env`)               | `int`  | `None`  |

\*: ABOUT SPLIT

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
