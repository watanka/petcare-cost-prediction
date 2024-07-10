#!/bin/bash
set -eu
# namespace up

ABSOLUTE_PATH=$(pwd)

kubectl apply -f $ABSOLUTE_PATH/mlflow/namespace.yaml
kubectl apply -f $ABSOLUTE_PATH/mlflow/mlflow.yaml

kubectl apply -f $ABSOLUTE_PATH/pipeline/namespace.yaml
kubectl apply -f $ABSOLUTE_PATH/pipeline/pipeline.yaml

kubectl apply -f $ABSOLUTE_PATH/mlserver/namespace.yaml
kubectl apply -f $ABSOLUTE_PATH/mlserver/mlserver.yaml

kubectl apply -f $ABSOLUTE_PATH/db/namespace.yaml
kubectl apply -f $ABSOLUTE_PATH/db/postgres.yaml

kubectl apply -f $ABSOLUTE_PATH/dashboard/namespace.yaml
kubectl apply -f $ABSOLUTE_PATH/dashboard/dashboard.yaml
