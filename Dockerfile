FROM python:3.12-slim-bullseye

RUN apt-get -y update; apt-get -y install curl

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.6.1
ENV PATH="$PATH:$POETRY_HOME/bin"

RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . /app

RUN poetry install

ENTRYPOINT ["poetry", "run", "uvicorn", "semantic_search_service.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
