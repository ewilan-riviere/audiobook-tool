# Tests

Or verbose

```sh
pytest -s
pytest -s tests/audio/test_reader.py
```

Docker test

```sh
dockr down -v
docker compose up -d
```

```sh
docker exec audiobook_tool uv run pytest
```

Locally test

```sh
docker run -it --rm python:3.12-slim bash
```

```sh
apt-get update && apt-get upgrade -y
apt-get install -y ffmpeg curl git
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="/root/.local/bin:$PATH"
git clone https://gitlab.com/kiwilan/audiobook-tool.git /home
cd /home
uv sync --frozen --extra dev
uv run playwright install --with-deps chromium
uv run audiobook-tool -h
uv run pytest
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

```bash
# brew install uv
alias py-sync="uv sync" # Create the venv and install everything according to the lockfile
alias py-add="uv add"   # Adds a lib and freezes it immediately
alias py-run="uv run"   # Run a command in the environment
alias py-update="uv lock --upgrade" # Updates versions according to your toml
alias py-export="uv export --format requirements-txt > requirements.txt" # Create requirements.txt based on locked dependencies
```
