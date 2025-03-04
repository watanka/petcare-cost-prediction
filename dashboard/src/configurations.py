import os


class Configurations:
    insurance_claim_record_file: str = os.getenv("INSURANCE_CLAIM_FILE", '/app/data_storage/insurance_claim.csv')
    insurance_claim_prediction_file: str = os.getenv("INSURANCE_CLAIM_PREDICTION_FILE", '/app/data_storage/prediction.csv')