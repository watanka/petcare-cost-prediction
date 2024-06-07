ARG FROM_IMAGE=python:3.10.6-slim

FROM ${FROM_IMAGE}

ARG LOCAL_DIR=bi

ENV PROJECT_DIR opt
WORKDIR /${PROJECT_DIR}
RUN apt-get -y update && \
    apt-get -y install \
    apt-utils \
    gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    python3 -m pip install --user pipx && \
    python3 -m pipx install poetry

# poetry 설치 디렉토리 PATH에 추가    
ENV PATH="${PATH}:/root/.local/bin"


COPY . .
RUN poetry install
VOLUME /data_storage


CMD ["poetry", "run", "streamlit", "run", "src/main.py" ]