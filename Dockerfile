# Python image
FROM python:3.11.9-slim

# Evita che Python scriva file .pyc e forza l'output dei log sul terminale
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Imposta la cartella di lavoro dentro il container
WORKDIR /code

# copia solo pyproject.toml e installa le dipendenze
COPY pyproject.toml /code/
RUN pip install --no-cache-dir -e ".[dev]"

# Copia tutto il resto del tuo codice nel container
COPY . /code/