FROM python:3.11-slim-bullseye

WORKDIR /src

ENV POETRY_VERSION=1.7.1
RUN pip install --upgrade pip && \
    pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock* /src/

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-dev

COPY . /src

EXPOSE 5000

CMD if [ "$FASTAPI_CONFIG" = "development" ] ; \
then poetry run uvicorn splitpenny.main:app --reload --host 0.0.0.0 --port 5000; \
else poetry run uvicorn splitpenny.main:app --host 0.0.0.0 --port 5000; \
fi
