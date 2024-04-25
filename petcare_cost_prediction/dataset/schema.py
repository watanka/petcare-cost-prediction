from pandera import Check, Column, DataFrameSchema, Index
from pydantic import BaseModel, Extra
from dataclasses import dataclass
import pandas as pd

class YearAndWeek(BaseModel):
    year: int
    week_of_year: int

    class Config:
        extra = Extra.forbid
        
      
@dataclass  
class XY:
    x: pd.DataFrame
    y: pd.DataFrame