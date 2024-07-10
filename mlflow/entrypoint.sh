#!/bin/bash

mlflow server --backend-store-uri postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/mlflow \
 --artifacts-destination /data_storage \
 --host 0.0.0.0
