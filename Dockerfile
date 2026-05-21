FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz-subset0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --only main

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]