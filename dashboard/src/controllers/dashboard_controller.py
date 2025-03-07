import os
import re
import pandas as pd
from models.container import Container
from services.data_service import DataService
from services.prediction_service import PredictionService
from services.district_service import DistrictService
from utils.logger import get_logger

logger = get_logger(__name__)

class DashboardController:
    """대시보드 컨트롤러"""
    
    def __init__(self):
        self.data_service = DataService()
        self.prediction_service = PredictionService()
        self.district_service = DistrictService()
        
    def initialize_container(self) -> Container:
        """컨테이너 초기화 및 데이터 로드"""
        container = Container()
        self._load_available_dates(container)
        return container
        
    def _load_available_dates(self, container: Container) -> None:
        """사용 가능한 날짜 목록 로드"""
        try:
            logger.info(f"container.settings.insurance_claim_records_dir: {container.settings.insurance_claim_records_dir}")
            available_dates = [f for f in os.listdir(container.settings.insurance_claim_records_dir) 
                              if os.path.isdir(os.path.join(container.settings.insurance_claim_records_dir, f)) 
                              and re.match(r'\d{4}-\d{2}-\d{2}', f)]
            available_dates.sort(reverse=True)  # 최신 날짜가 먼저 오도록 정렬
            logger.info(f"available_dates: {available_dates}")
            container.available_dates = available_dates
        except Exception as e:
            logger.error(f"날짜 폴더 목록을 가져오는 중 오류 발생: {e}")
            container.available_dates = []
            
    def load_insurance_claim_data(self, container: Container, date: str) -> bool:
        """보험 청구 데이터 로드"""
        try:
            file_path = os.path.join(container.settings.insurance_claim_records_dir, date, "insurance_claim.csv")
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                container.set_insurance_claim_df(df)
                container.selected_date = date
                logger.info(f"{date} 날짜의 보험 청구 데이터 로드 성공")
                return True
            else:
                logger.warning(f"보험 청구 데이터 파일이 존재하지 않습니다: {file_path}")
                return False
        except Exception as e:
            logger.error(f"보험 청구 데이터 로드 중 오류 발생: {e}")
            return False
            
    def load_prediction_models(self, container: Container, date: str) -> bool:
        """예측 모델 데이터 로드"""
        try:
            prediction_path = os.path.join(container.settings.insurance_claim_prediction_dir, date)
            if not os.path.exists(prediction_path):
                logger.warning(f"예측 데이터 폴더가 존재하지 않습니다: {prediction_path}")
                return False
                
            # 모델 폴더 확인
            model_folders = [f for f in os.listdir(prediction_path) 
                            if os.path.isdir(os.path.join(prediction_path, f))]
            
            if not model_folders:
                logger.warning(f"{date} 날짜에 모델 폴더가 없습니다.")
                return False
                
            # 기존 모델 데이터 초기화
            container.clear_model_data()
            
            # 각 모델 데이터 로드
            for model_name in model_folders:
                file_path = os.path.join(prediction_path, model_name, 'prediction.csv')
                if os.path.exists(file_path):
                    try:
                        prediction_df = pd.read_csv(file_path)
                        
                        # 기본 모델인 경우 container.prediction_df에도 설정
                        if model_name == model_folders[0]:
                            container.set_prediction_df(prediction_df)
                            
                        # 모델 데이터 추가
                        if container.insurance_claim_df is not None:
                            comparison_df = self.prediction_service.summarize_prediction(
                                container=container,
                                insurance_claim_df=container.insurance_claim_df,
                                prediction_df=prediction_df
                            )
                            container.add_model_data(model_name, comparison_df)
                            logger.info(f"{date} 날짜의 {model_name} 모델 데이터 로드 성공")
                    except Exception as e:
                        logger.error(f"모델 '{model_name}'의 데이터를 로드하는 중 오류 발생: {str(e)}")
            
            return len(container.model_data) > 0
        except Exception as e:
            logger.error(f"예측 모델 데이터 로드 중 오류 발생: {e}")
            return False