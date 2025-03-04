from logger import configure_logger
from service import (ClaimPriceService, 
                     ClaimPricePredictionService)
from view import build, init_container
from dataloader import DataLoader

logger = configure_logger(__name__)



def main():
    logger.info('now loading...')

    # data_loader = DataLoader(config=Configurations)
    # insurance_claim_df, prediction_df = data_loader.init_df()

    container = init_container()

    claim_price_service = ClaimPriceService()
    claim_price_prediction_service = ClaimPricePredictionService()
    
    variable_list = [
        ('gender', 'category'),
        ('breed', 'category'),
        ('neutralized', 'category'),
        ('age', 'numeric'),
    ]

    build(
        variable_list,
        container,
        claim_price_service,
        claim_price_prediction_service
    )

if __name__ == '__main__':
    main()