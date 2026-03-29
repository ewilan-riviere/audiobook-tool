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

Use `audiobook-tool` CLI

```sh
audiobook-tool build ./path/to/source_directory
```
