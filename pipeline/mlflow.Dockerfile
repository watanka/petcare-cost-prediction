FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    pkg-config \
    libssl-dev \
    libffi-dev \
    python3-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /mlflow

COPY requirements-mlflow.txt .
RUN pip install -r requirements-mlflow.txt

EXPOSE 5000

CMD mlflow server \
    --host 0.0.0.0 \
    --port 5000 \
    --backend-store-uri ${MLFLOW_TRACKING_URI} \
    --default-artifact-root s3://mlflow/ 