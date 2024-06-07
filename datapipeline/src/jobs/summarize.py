import pandas as pd

from src.middleware.exception import BreedInfoNotFoundError

class Statistics:
    def __init__(self, df):
        df['claim_price'] = df['claim_price'].astype(float)
        self.df = df.groupby(['pet_breed_id', 'age'])
        self.price_groupby_breed_and_age = self.df['claim_price'].mean()
        self.most_common_diseases_groupby_breed_and_age = self.df['disease_name'].agg(lambda x: x.mode()[0])
        
    
    def to_dict(self, df: pd.DataFrame):
        return df.to_dict()
    
    def average_price_change_by_breed_and_age(self, breed):
        return self.to_dict(self.price_groupby_breed_and_age[breed])
        
    def most_common_disease_by_breed_and_age(self, breed):
        return self.to_dict(self.most_common_diseases_groupby_breed_and_age[breed])
    
    def aggregate_stat(self, breed):
        try:
            avg_price = self.average_price_change_by_breed_and_age(breed)
            most_common_disease = self.most_common_disease_by_breed_and_age(breed)
            
            stat = []
            
            for age, avg_price, disease in zip(avg_price.keys(), avg_price.values(), most_common_disease.values()):
                stat.append({'age': age, 'average_cost' : avg_price // 100 * 100 , 'disease': disease})
        except:
            raise BreedInfoNotFoundError(message = f"견종id [{breed}]에 대한 데이터가 없습니다.")
        return stat
        