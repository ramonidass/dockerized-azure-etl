FROM python:3.11-slim as base

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
RUN uv pip install --system .

# ---

FROM python:3.11-slim as final

WORKDIR /app

COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

COPY src/ src/

CMD ["python", "-m", "src.main"]
