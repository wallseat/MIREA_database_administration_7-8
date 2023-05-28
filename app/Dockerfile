FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir --no-python-version-warning -r requirements.txt \
    && rm -f requirements.txt

COPY src/ src/

RUN pip install -e .