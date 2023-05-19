FROM python:3.11-slim-buster

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update -qq \
    && DEBIAN_FRONTEND=noninteractive apt-get install -yq --no-install-recommends \
        curl \
        openssh-client \
        vim \
        git \
    && apt-get clean \
    && rm -rf /var/cache/apt/archives/* \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && truncate -s 0 /var/log/*log

RUN curl -sSL https://install.python-poetry.org > install-poetry.py \
    && python3 install-poetry.py \
    && rm install-poetry.py

ENV PATH $PATH:/root/.local/bin
RUN poetry config virtualenvs.create false

RUN mkdir -p /app
WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install  --no-interaction --no-ansi
CMD [ "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000" ]