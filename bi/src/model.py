

import pandas as pd
from logger import configure_logger
from schema import Breed, Gender, Neutralized
from typing import List, Optional


logger = configure_logger(__name__)


class Container(object):
    def __init__(self):
        self.insurance_claim_df: pd.DataFrame = None
        self.prediction_df: pd.DataFrame = None
        self.prediction_record_df: pd.DataFrame = None

    def load_df(
        self,
        file_path: str,
    ) -> pd.DataFrame:
        logger.info(f"read {file_path}")
        df = pd.read_csv(file_path)
        df['age'] = (pd.to_datetime(df['created_at']) - pd.to_datetime(df['birth'])).dt.days
        
        logger.info(
            f"""
read {file_path}
shape: {df.shape}
columns: {df.columns}
        """
        )
        return df

    def load_insurance_claim_df(
        self,
        file_path: str,
    ):
        self.insurance_claim_df = self.load_df(file_path=file_path)
        # self.insurance_claim_df["date"] = pd.to_datetime(self.insurance_claim_df["updated_at"])
        # self.insurance_claim_df["year"] = self.insurance_claim_df.date.dt.year
        #TODO: validation
        logger.info(
            f"""
formatted {file_path}
shape: {self.insurance_claim_df.shape}
columns: {self.insurance_claim_df.columns}
        """
        )

    def load_prediction_df(
        self,
        prediction_file_path: str,
        prediction_record_file_path: str,
    ):
        self.prediction_df = self.load_df(file_path=prediction_file_path)
        # TODO: validation
        logger.info(
            f"""
formatted {prediction_file_path}
shape: {self.prediction_df.shape}
columns: {self.prediction_df.columns}
        """
        )

        self.prediction_record_df = self.load_df(file_path=prediction_record_file_path)
        # TODO: validation  
        logger.info(
            f"""
formatted {prediction_record_file_path}
shape: {self.prediction_record_df.shape}
columns: {self.prediction_record_df.columns}
        """
        )


class BreedRepository:
    def __init__(self):
        pass

    def select(
        self,
        container: Container
    ) -> List[Breed]:
        breeds = container.insurance_claim_df.pet_breed_id.unique()
        return [Breed(name=breed) for breed in breeds]
    
class AgeRepository:
    def __init__(self):
        pass

    def select(
        self,
        container: Container
    ):
        pass
        
class GenderRepository:
    def __init__(self):
        pass
    def select(
        self,
        container: Container
    )-> List[Gender]:
        genders = container.insurance_claim_df.gender.unique()
        return [Gender(gender) for gender in genders]

class NeutralizedRepository:
    def __init__(self):
        pass
    def select(
        self,
        container: Container
    )-> List[Neutralized]:
        neutralized = container.insurance_claim_df.neuter_yn.unique()
        return [Neutralized(n) for n in neutralized]



class ClaimPriceRepository:
    def __init__(self):
        pass
    
    def select(
        self,
        container: Container,
        breed: Optional[Breed] = None,
        age: Optional[int] = None,
        gender: Optional[Gender] = None,
        neutralized: Optional[bool] = None,
    ):
        df = container.insurance_claim_df
        if breed:
            df = df[df.pet_breed_id == breed]
        if age:
            df = df[df.age == age] 
        if gender:
            df = df[df.gender == gender]    
        if neutralized:
            df = df[df.neuter_yn == neutralized]
        
        return df
    
class ClaimPricePredictionRepository:
    def __init__(self):
        pass
    
    def select(
        self,
        container: Container,
        breed: Optional[Breed] = None,
        age: Optional[int] = None,
        gender: Optional[Gender] = None,
        neutralized: Optional[bool] = None,
    ):
        df = container.prediction_df
        if breed:
            df = df[df.pet_breed_id == breed]
        if age:
            df = df[df.age == age] 
        if gender:
            df = df[df.gender == gender]    
        if neutralized:
            df = df[df.neuter_yn == neutralized]
        
        return df