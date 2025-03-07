from enum import Enum, auto

class BI(Enum):
    """BI 유형 열거형"""
    INSURANCE_CLAIM = "실제 보험 청구금액"
    INSURANCE_CLAIM_PREDICTION_EVALUATION = "예측 보험 청구금액"

class VariableType(Enum):
    """변수 유형 열거형"""
    CATEGORY = "category"
    NUMERIC = "numeric"

class ChartType(Enum):
    """차트 유형 열거형"""
    BAR = auto()
    LINE = auto()
    SCATTER = auto()
    PIE = auto()
    MAP = auto()

class District(Enum):
    """서울시 구 열거형"""
    강남구 = "강남구"
    강동구 = "강동구"
    강북구 = "강북구"
    강서구 = "강서구"
    관악구 = "관악구"
    광진구 = "광진구"
    구로구 = "구로구"
    금천구 = "금천구"
    노원구 = "노원구"
    도봉구 = "도봉구"
    동대문구 = "동대문구"
    동작구 = "동작구"
    마포구 = "마포구"
    서대문구 = "서대문구"
    서초구 = "서초구"
    성동구 = "성동구"
    성북구 = "성북구"
    송파구 = "송파구"
    양천구 = "양천구"
    영등포구 = "영등포구"
    용산구 = "용산구"
    은평구 = "은평구"
    종로구 = "종로구"
    중구 = "중구"
    중랑구 = "중랑구"

class Gender(Enum):
    """성별 열거형"""
    남자 = "남자"
    여자 = "여자"

class Breed(Enum):
    """품종 열거형"""
    진돗개 = "진돗개"
    푸들 = "푸들"
    포메라니안 = "포메라니안"
    치와와 = "치와와"
    시바견 = "시바견"
    비숑 = "비숑"
    말티즈 = "말티즈"
    골든리트리버 = "골든리트리버"

class Neutralized(Enum):
    """중성화 여부 열거형"""
    y = "y"
    n = "n"