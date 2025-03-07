import os
from dataclasses import dataclass

@dataclass
class Settings:
    """애플리케이션 설정 클래스"""
    
    # 기본 디렉토리 설정
    base_dir: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # 데이터 디렉토리 설정
    data_dir: str = os.path.join(base_dir, "data_storage")
    insurance_claim_records_dir: str = os.path.join(data_dir, "records")
    insurance_claim_prediction_dir: str = os.path.join(data_dir, "prediction")
    
    # 지도 데이터 설정
    map_data_dir: str = os.path.join(data_dir, "map")
    seoul_shapefile: str = os.path.join(map_data_dir, "seoul_municipalities.shp")
    
    # 폰트 설정
    font_dir: str = os.path.join(data_dir, "font")
    korean_font: str = os.path.join(font_dir, "NanumGothic.ttf")
    
    # 로깅 설정
    log_dir: str = os.path.join(base_dir, "logs")
    log_level: str = "INFO"
    
    def __post_init__(self):
        """디렉토리 존재 확인 및 생성"""
        for dir_path in [self.data_dir, self.insurance_claim_records_dir, 
                         self.insurance_claim_prediction_dir, self.map_data_dir, 
                         self.font_dir, self.log_dir]:
            os.makedirs(dir_path, exist_ok=True)