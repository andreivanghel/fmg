# Python image
FROM python:3.11.9-slim

# Evita che Python scriva file .pyc e forza l'output dei log sul terminale
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Imposta la cartella di lavoro dentro il container
WORKDIR /code

# Copia il file delle dipendenze e installale
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il resto del tuo codice nel container
COPY . /code/