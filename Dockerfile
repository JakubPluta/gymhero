FROM python:3.10-slim


RUN pip install poetry==1.7.0 && pip install psycopg2-binary && poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml ./
WORKDIR /app
COPY . .
RUN poetry install --without dev && rm -rf $POETRY_CACHE_DIR

EXPOSE 8000

ENTRYPOINT ["poetry", "run", "python", "-m", "gymhero.server"]
