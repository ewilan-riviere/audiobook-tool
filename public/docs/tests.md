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
git clone https://github.com/ewilan-riviere/audiobook-tool.git /home
cd /home
pip install -e .
pip install pytest
playwright install --with-deps chromium
audiobook-tool -h
pytest
```
