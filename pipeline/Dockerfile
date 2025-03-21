FROM python:3.10-buster

ENV DEPLOY_URL=http://localhost:5001/deploy
ENV MLSERVER1_HOST=petcare-mlserver1
ENV MLSERVER2_HOST=petcare-mlserver2
ENV MODEL_WEIGHT_PATH=/app/data_storage/train_results/

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

EXPOSE 8000

CMD ["poetry", "run", "streamlit", "run", "main.py", "--server.port", "8000"]