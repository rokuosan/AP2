FROM python:3.13-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.11.9 /uv /usr/local/bin/uv
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY README.md pyproject.toml ./
COPY code/sdk/python code/sdk/python
COPY code/samples/python code/samples/python
RUN uv sync --package ap2-samples --no-dev

FROM python:3.13-slim
WORKDIR /app
COPY --from=build /app /app
COPY code/samples/certs code/samples/certs
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    TEMP_DB_DIR=/state \
    AGENT_PROVIDER_PUBLIC_KEY_PATH=/state/agent_provider_signing_key.pub
RUN mkdir /app/.logs \
    && chown -R 65532:65532 /app/.logs \
       /app/.venv/lib/python3.13/site-packages/google/adk/cli/browser/assets/config
USER 65532:65532
