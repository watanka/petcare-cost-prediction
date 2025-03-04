from datetime import datetime
from pandera import Column, DataFrameSchema, Check, Index
from pydantic import BaseModel, Extra
from typing import List
from enum import Enum



class Gender(Enum):
    남자 = "남자"
    여자 = "여자" 


    
class Breed(Enum):
    진돗개 = "진돗개"
    푸들 = "푸들"
    포메라니안 = "포메라니안"
    치와와 = "치와와"
    시바견 = "시바견"
    비숑 = "비숑"
    말티즈 = "말티즈"
    골든리트리버 = "골든리트리버"


class Neutralized(Enum):
    y = "y"
    n = "n"


class District(Enum):
    중구 = "중구"
    구로구 = "구로구"
    종로구 = "종로구"
    금천구 = "금천구"
    노원구 = "노원구"
    광진구 = "광진구"
    도봉구 = "도봉구"
    성북구 = "성북구"
    관악구 = "관악구"
    마포구 = "마포구"
    은평구 = "은평구"
    영등포구 = "영등포구"
    중랑구 = "중랑구"
    동대문구 = "동대문구"
    동작구 = "동작구"
    양천구 = "양천구"
    성동구 = "성동구"
    강북구 = "강북구"
    송파구 = "송파구"
    서대문구 = "서대문구"
    강동구 = "강동구"
    강서구 = "강서구"
    용산구 = "용산구"
    서초구 = "서초구"
    강남구 = "강남구"


class Pet(BaseModel):
    gender: Gender
    breed: Breed
    neutralized: Neutralized
    district: District
    age: int
    weight: float
    price: int


# 데이터 검증을 위한 Pandera 스키마
insurance_schema = DataFrameSchema(
    {
        "gender": Column(str, Check.isin(["남자", "여자"])),
        "breed": Column(str),
        "neutralized": Column(str, Check.isin(["y", "n"])),
        "district": Column(str),
        "age": Column(int, Check.ge(0)),
        "weight": Column(float, Check.gt(0)),
        "price": Column(int, Check.gt(0))
    }
)


