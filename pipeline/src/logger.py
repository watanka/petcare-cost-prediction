import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

def setup_logger(name: str = __name__, log_level: str = "INFO") -> logging.Logger:
    """
    로거를 설정하고 반환합니다.
    
    Args:
        name (str): 로거 이름
        log_level (str): 로깅 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        logging.Logger: 설정된 로거 객체
    """
    # 로그 디렉토리 생성
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 로그 파일명 설정 (날짜별)
    current_date = datetime.now().strftime("%Y%m%d")
    log_file = log_dir / f"{current_date}_{name}.log"
    
    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 이미 핸들러가 있다면 제거
    if logger.handlers:
        logger.handlers.clear()
    
    # 파일 핸들러 설정 (최대 10MB, 백업 5개)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    
    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler(sys.stdout)
    
    # 포맷터 설정
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 기본 로거 설정
logger = setup_logger("petcare_pipeline", "INFO")

def get_logger(name: str = __name__, log_level: str = "INFO") -> logging.Logger:
    """
    지정된 이름의 로거를 반환합니다.
    
    Args:
        name (str): 로거 이름
        log_level (str): 로깅 레벨
        
    Returns:
        logging.Logger: 설정된 로거 객체
    """
    return setup_logger(name, log_level) 