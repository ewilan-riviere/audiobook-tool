# Audiobook Tool 🎧

A professional CLI tool to merge MP3 files into M4B audiobooks and intelligently split large files without cutting mid-sentence.

## 🚀 Key Features

- **Smart Merging**: Combines a directory of MP3s into a single M4B file.
- **Automatic Chaptering**: Creates chapters based on individual MP3 file names.
- **Rich Metadata Support**: Full support for advanced tags via an optional `metadata.yml`.
- **Cover Art Integration**: Automatically embeds `cover.jpg` or `cover.png` if found.
- **Intelligent Splitting**: Splits oversized files into parts (400-600MB) **without cutting inside a chapter**.
- **Flexible Outputs**: Custom paths for merged files and specific output directories for split parts.

---

## ⚙️ Requirements

- **Python**: 3.8+
- **FFmpeg**: Must be installed and available in your system `PATH`.
- **PyYAML**: For metadata parsing.

## 🛠 Installation (Development Mode)

```bash
pip install -e .
```

---

## 📖 Usage

### Merging MP3s

Merge a directory and specify the output filename/path:

```bash
# Default output (creates directory_name.m4b in current dir)
audiobook-tool merge ./my_book_directory

# Custom output path (will create directories if they don't exist)
audiobook-tool merge ./my_book_directory -o ./library/2026/fantasy_novel.m4b
```

Before running the `merge` command, organize your files as follows:

```text
my_audiobook_source/
├── 01 - Prologue.mp3
├── 02 - Chapter One.mp3
├── 03 - Chapter Two.mp3
├── ...
├── cover.jpg          # (Optional) Automatic cover art
└── metadata.yml      # (Optional) Rich tags & description
```

> **Note:** Files are sorted naturally. It is highly recommended to prefix your MP3 files with numbers (01, 02, etc.) to ensure the chapters are created in the correct order.

#### Cover

Keep `cover.jpg` or `cover.png` into same directory as MP3 files (optional).

#### Metadata

Create a `metadata.yml` in your source directory (optional). All fields are optional:

```yml
title: "The Fellowship of the Ring"
authors: "J.R.R. Tolkien"
narrators: "Rob Inglis"
year: 1954
series: "The Lord of the Rings"
volume: 1
description: |
  The first part of the epic masterpiece...
```

Check [metadata.template.yml](./metadata.template.yml) to get a full template.

### 2. Splitting Large Files

Split a large M4B into a specific directory to keep your workspace clean:

```bash
# Parts will be saved in the specified directory
audiobook-tool split ./huge_book.m4b -o ./output_parts/ --min 400 --max 600
```

### 4. Viewing Metadata

Export technical info and chapters to a JSON file:

```bash
audiobook-tool metadata ./book.m4b -o info.json
```
