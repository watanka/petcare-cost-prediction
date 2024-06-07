from elasticapm.contrib.starlette import make_apm_client, ElasticAPM

# Elastic APM
# https://medium.com/squad-engineering/how-to-optimize-elastic-apm-6f7f6d58bed5
apm_config = {
    "SERVICE_NAME": "petcare-cost-prediction",
    "SERVER_URL": "http://localhost:8200",
    "ENVIRONMENT": "dev",
    "GLOBAL_LABELS": "platform=Platform, application=Application",
    "TRANSACTION_MAX_SPANS": 250,
    "STACK_TRACE_LIMIT": 250,
    "TRANSACTION_SAMPLE_RATE": 0.5,
    "APTURE_HEADERS": "false"
}

apm = make_apm_client(apm_config)
