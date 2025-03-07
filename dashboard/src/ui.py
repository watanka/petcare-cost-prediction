from typing import List, Tuple
from enum import Enum

from logger import configure_logger

from model import (Container, 
                   BaseRepository,
                   BreedRepository, 
                   AgeRepository,
                   GenderRepository,
                   NeutralizedRepository,
                   DistrictRepository,
                   DateRepository)


logger = configure_logger(__name__)

class BaseOption(object):
    def __init__(self):
        pass

class OptionFactory:
    @staticmethod
    def get_option(option_name: str, variable_type: str) -> BaseOption:
        '''
        variable_type: [category, numeric]
        '''
        if variable_type == 'category':
            if option_name == 'gender':
                repository = GenderRepository()
            elif option_name == 'neutralized':
                repository = NeutralizedRepository()
            elif option_name == 'breed':
                repository = BreedRepository()
            elif option_name == 'district':
                repository = DistrictRepository()
            elif option_name == 'date':
                repository = DateRepository()
            return CategoryOption(repository)
        
        elif variable_type == 'numeric':
            if option_name == 'age':
                repository = AgeRepository()
            return NumericOption(repository)
        else:
            raise ValueError(f"Invalid option name: {option_name}")
        


class CategoryOption(BaseOption):
    def __init__(self, repository: BaseRepository):
        super().__init__()
        self.repository = repository

    def list_labels(self, container: Container) -> List[str]:
        variables = self.repository.select(container=container)
        logger.info(f"variables: {variables}")
        variable_names = [v.value if isinstance(v, Enum) else v for v in variables ]
        return variable_names

class NumericOption(BaseOption):
    def __init__(self, repository: BaseRepository):
        super().__init__()
        self.repository = repository

    def list_labels(self, container: Container) -> Tuple[int, int]:
        value_range = self.repository.select(container=container)
        logger.info(f"value_range: {value_range}")
        return value_range
        