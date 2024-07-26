# Этап 1: Установка зависимостей с помощью poetry
FROM python:3.12

# python:
ENV PYTHONFAULTHANDLER=1 \
PYTHONUNBUFFERED=1 \
PYTHONHASHSEED=random \
# pip:
PIP_NO_CACHE_DIR=off \
PIP_DISABLE_PIP_VERSION_CHECK=on \
PIP_DEFAULT_TIMEOUT=100 \
# poetry:
POETRY_VERSION=1.7.1 \
POETRY_VIRTUALENVS_CREATE=false \
POETRY_CACHE_DIR='/var/cache/pypoetry'

# System deps:
RUN apt-get update && \
  apt-get install --no-install-recommends -y \
  build-essential \
  gettext \
  libpq-dev \
  wget \
  # Cleaning cache:
  && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/* \
  # Installing `poetry` package manager:
  # https://github.com/python-poetry/poetry
  && pip install "poetry==$POETRY_VERSION" && poetry --version

# Копируем файлы проекта в контейнер
COPY pyproject.toml poetry.lock /app/

WORKDIR /app

# Project initialization:
RUN poetry install --no-root

# Creating folders, and files for a project:
COPY . .

RUN python app.py
