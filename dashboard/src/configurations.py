import os


class Configurations:
    insurance_claim_records_dir: str = os.getenv("INSURANCE_CLAIM_RECORDS_DIR", '/app/data_storage/records')
    insurance_claim_prediction_dir: str = os.getenv("INSURANCE_CLAIM_PREDICTION_DIR", '/app/data_storage/prediction')