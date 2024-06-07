FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# Poetry 설치
RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Poetry 설정을 위해 환경 변수 설정
ENV POETRY_VIRTUALENVS_CREATE=false

# 프로젝트의 종속성 파일 복사
COPY pyproject.toml poetry.lock ./

# 종속성 설치
RUN poetry install --no-root

# 프로젝트 파일 복사
COPY . .

# 컨테이너 시작 명령어 설정 (예: main.py 파일을 실행)
CMD ["python", "main.py"]