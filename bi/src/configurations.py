import os


class Configurations:
    insurance_claim_record_file: str = os.getenv("INSURANCE_CLAIM_FILE", '/data_storage/insurance_claim.csv')
    insurance_claim_prediction_dir: str = os.getenv("INSURANCE_CLAIM_PREDICTION_DIR", './sample_data')