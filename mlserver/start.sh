#!/bin/bash

# MODEL_WEIGHT_PATH 환경변수로 model-settings.json 업데이트
python setup.py

# MLserver 시작
mlserver start /app