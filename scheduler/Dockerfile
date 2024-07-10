FROM python:3.10-slim as build-stage

WORKDIR /tmp
RUN pip install poetry
ENV PATH="${PATH}:/root/.local/bin"

COPY pyproject.toml poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


# Stage 2: Final
FROM python:3.10-slim

WORKDIR /app

COPY --from=build-stage /tmp/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt && \
    apt-get -y update && \
    apt-get -y install \
    apt-utils \
    gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . /app

# 컨테이너 시작 명령어 설정 (예: main.py 파일을 실행)
CMD ["python", "main.py"]