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
    && poetry install --no-interaction --no-ansi --no-root

COPY . /app


# 컨테이너 시작 명령어 설정 (예: main.py 파일을 실행)
CMD ["python", "main.py"]