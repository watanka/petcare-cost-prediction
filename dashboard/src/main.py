from logger import configure_logger
from service import (
    DataStatisticsService,
    PredictionStatisticsService,
    DistrictStatisticsService,
)
from view import build, init_container

logger = configure_logger(__name__)



def main():
    logger.info('now loading...')

    container = init_container()

    data_stat_service = DataStatisticsService()
    prediction_stat_service = PredictionStatisticsService()
    district_stat_service = DistrictStatisticsService()
    
    variable_list = [
        ('gender', 'category'),
        ('breed', 'category'),
        ('neutralized', 'category'),
        ('age', 'numeric'),
        ('district', 'category'),
        ('date', 'category')
    ]

    build(
        variable_list,
        container,
        data_stat_service,
        prediction_stat_service,
        district_stat_service,
    )

if __name__ == '__main__':
    main()