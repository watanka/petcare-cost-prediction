FROM python:3.10-buster

WORKDIR /app

COPY pyproject.toml poetry.lock* README.md /app/ 

RUN pip install poetry

# 시스템 패키지 설치
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY . /app

EXPOSE 8501

CMD ["poetry", "run", "streamlit", "run", "main.py"]