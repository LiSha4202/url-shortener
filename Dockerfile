FROM python:3.13.2-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app/src

WORKDIR /app

RUN pip install --upgrade pip wheel "poetry==2.4.1"

RUN poetry config virtualenvs.create false

COPY pyproject.toml ./
COPY poetry.lock ./

RUN poetry install --no-root

RUN apt-get update && apt-get install -y dos2unix && rm -rf /var/lib/apt/lists/*

COPY . . 

WORKDIR /app

RUN chmod +x prestart.sh

ENTRYPOINT ["./prestart.sh"]
CMD ["python", "/app/src/main.py"]