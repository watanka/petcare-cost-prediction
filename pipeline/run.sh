#!/bin/bash

set -eu

NAME=pipeline
WORKERS=3
WORKER_CLASS=uvicorn.workers.UvicornWorker
LOG_LEVEL=info

exec poetry run gunicorn main:app \
    --name $NAME \
    --workers $WORKERS \
    --worker-class $WORKER_CLASS \
    --log-level=$LOG_LEVEL \
    --log-file=-
