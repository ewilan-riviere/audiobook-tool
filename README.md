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

## Features

- 🎧 Fetch metadata and cover from [Audible](https://www.audible.com/) with **ASIN** code
- 📦 Build `M4B` audiobook from `MP3`/`M4A` files (can be multi-part or one)
- 📤 Extract chapters from `M4B` audiobook and convert to `M4A`/`MP3`
- 🔖 Parse `M4B` audiobook to convert tags to `YAML` file

## Roadmap

- [ ] Fix M4A handle
- [ ] Test for one audiobook
- [ ] Confirm for override metadata/cover
- [ ] Confirm after Audible fetch
- [ ] Refact. args
- [ ] Refact clear flag
- [ ] Review logging
- [ ] GitHub test
- [ ] README

## Why?

I have been using [audiobookshelf](https://www.audiobookshelf.org/) for a long time, and to manage my audiobooks, I used [Audiobook Builder](https://www.splasm.com/audiobookbuilder/) (which is a paid program). While this software is very useful for managing audiobooks, when you need to create several in a row, it is time-consuming and tedious, lacking flexibility.

I also needed to create audiobooks in several parts (to help with streaming) but without splitting the chapters into two parts (which is unpleasant). I also needed a CLI capable of reading metadata from a YAML file in order to apply the corresponding tags to the audiobook.

In addition, when I retrieve metadata from [Audible](https://www.audible.com/), it is rather tedious, and I wanted to be able to do it automatically.

The whole thing needed to be flexible and resilient, offering high-quality audiobooks that could be used directly by [audiobookshelf](https://www.audiobookshelf.org/).

## Usage

### Audible

`audible` command will fetch metadata from Audible website (web scraping with [playwright](https://playwright.dev/)) to create `metadata.yml` file and `cover.jpg` file. You need ASIN code available in Audible URL and shortcut for any audiobook, like ASIN code `B0G5SMXT5S` for `https://www.audible.com/pd/B0G5SMXT5S?ipRedirectOverride=true` with _Assassin’s Apprentice (The Farseer Trilogy, Book 1)_ audiobook.

> [!TIP]
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

#### Metadata & cover

You can create `metadata.yml` file in `/path/to/source_files` to specify tags to use for M4B audiobook, you can use [`metadata.template.yml`](./metadata.template.yml) as example. These metadata are based on [audiobookshelf's Audio Metadata](https://www.audiobookshelf.org/docs#book-audio-metadata).

- `title`: used as `title` and `album`
- `authors`: used as `artist` and `album_artist`
- `narrators`: used as `composer`
- `description`: used as `description` and `synopsis`
- `lyrics`: used as `lyrics`
- `copyright`: used as `copyright`
- `genres`: used as `genre`
- `series`: used as `series`
- `volume`: used as `series-part`
- `language`: used as `language`
- `year`: used as `date`
- `publisher`: used as `publisher`
- `subtitle`: used as `subtitle` and `comment`
- `isbn`: used as `isbn`
- `asin`: used as `asin`

```yml
title: "The Fellowship of the Ring"
authors: "J.R.R. Tolkien & Christopher Tolkien"
narrators: "Rob Inglis & Andy Serkis"
description: "Sauron, the Dark Lord, has gathered to him all the Rings of Power..."
lyrics: "With a masterful performance by Andy Serkis, who plays Gollum in Peter Jackson's films."
copyright: "©1954 The Tolkien Estate Limited (P)2025 HarperCollins Publishers Limited"
genres: "Fantasy/Fiction"
series: "The Lord of the Rings"
volume: 1.0
language: "English"
year: 2005
publisher: "HarperCollins Publishers Limited"
subtitle: "One Ring To Rule Them All"
isbn: 9780007123827
asin: 0008487278
```

For cover, just put `cover.jpg` into `/path/to/source_files` and `build` command will attach it to M4B audiobook.

> [!TIP]
> `audible` command or `build` command with `--asin` flag will create `metadata.yml` and `cover.jpg` automtically if ASIN is valid.

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
