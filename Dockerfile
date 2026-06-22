FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN pip install uv

COPY pyproject.toml README.md ./
COPY src ./src

RUN uv pip install --system .

RUN useradd --create-home --uid 1000 --shell /usr/sbin/nologin rip_agent
USER rip_agent

EXPOSE 8000

CMD ["uvicorn", "rip_agent.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
