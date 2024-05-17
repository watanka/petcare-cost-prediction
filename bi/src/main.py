from logger import configure_logger
from service import (BreedService, 
                     GenderService, 
                     NeutralizedService,
                     ClaimPriceService, 
                     ClaimPricePredictionService)
from view import build

logger = configure_logger(__name__)


def main():
    logger.info('now loading...')
    breed_service = BreedService()
    claim_price_service = ClaimPriceService()
    gender_service = GenderService()
    neutralized_service = NeutralizedService()
    claim_price_prediction_service = ClaimPricePredictionService()
    build(
        breed_service,
        gender_service,
        neutralized_service,
        claim_price_service,
        claim_price_prediction_service
    )

if __name__ == '__main__':
    main()