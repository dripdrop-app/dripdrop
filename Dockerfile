FROM ghcr.io/astral-sh/uv:python3.13-bookworm

RUN apt update && apt install -y ffmpeg 

WORKDIR /app

COPY ./uv.lock ./uv.lock
COPY ./pyproject.toml ./pyproject.toml

RUN uv sync

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

CMD ["fastapi", "run", "--host", "0.0.0.0"]
