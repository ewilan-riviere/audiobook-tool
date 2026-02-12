FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
  ffmpeg curl \
  && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

RUN uv run playwright install --with-deps chromium

COPY . .

ENTRYPOINT ["uv", "run", "python", "src/audiobook/__main__.py"]
