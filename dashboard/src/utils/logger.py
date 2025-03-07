import os
import logging
from logging.handlers import RotatingFileHandler
from config.settings import Settings

def get_logger(name: str) -> logging.Logger:
    """로거 인스턴스 생성"""
    settings = Settings()
    
    # 로그 디렉토리 생성
    os.makedirs(settings.log_dir, exist_ok=True)
    
    # 로거 설정
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level))
    
    # 이미 핸들러가 설정되어 있으면 추가하지 않음
    if not logger.handlers:
        # 파일 핸들러 설정
        log_file = os.path.join(settings.log_dir, 'dashboard.log')
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        
        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler()
        console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
    
    return logger