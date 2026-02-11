# Tests

Or verbose

```sh
pytest -s
pytest -s tests/audio/test_reader.py
```

Locally test

```sh
docker run -it --rm python:3.12-slim bash
```

```sh
apt-get update && apt-get upgrade -y
apt-get install -y ffmpeg git
git clone https://gitlab.com/kiwilan/audiobook-tool.git /home
cd /home
pip install -e .
pip install pytest
playwright install --with-deps chromium
audiobook-tool -h
pytest
```

```toml
dependencies = [
  "pyyaml~=6.0.1",
  "mutagen~=1.47.0",
  "python-dotenv~=1.0.1",
  "isodate~=0.7.2",
  "httpx~=0.28.0",
  "beautifulsoup4~=4.12.3",
  "requests~=2.32.0",
  "ffmpeg-python~=0.2.0",
  "rich~=13.7.0",
  "playwright~=1.49.0",
  "playwright-stealth~=1.0.6",
  "fake-useragent~=1.5.1"
]
```
