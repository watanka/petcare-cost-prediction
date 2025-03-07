import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import platform
from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)

def set_korean_font():
    """한글 폰트 설정"""
    settings = Settings()
    
    try:
        # 운영체제별 기본 한글 폰트 설정
        system = platform.system()
        
        if system == 'Windows':
            plt.rcParams['font.family'] = 'Malgun Gothic'
        elif system == 'Darwin':  # macOS
            plt.rcParams['font.family'] = 'AppleGothic'
        else:  # Linux 등
            # 사용자 정의 폰트 경로 확인
            if os.path.exists(settings.korean_font):
                font_path = settings.korean_font
                font_name = fm.FontProperties(fname=font_path).get_name()
                plt.rcParams['font.family'] = font_name
            else:
                # 시스템에 설치된 한글 폰트 찾기
                korean_fonts = [f.name for f in fm.fontManager.ttflist if 'Gothic' in f.name or 'Nanum' in f.name]
                if korean_fonts:
                    plt.rcParams['font.family'] = korean_fonts[0]
                else:
                    logger.warning("한글 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")
        
        # 마이너스 기호 표시 설정
        plt.rcParams['axes.unicode_minus'] = False
        
        logger.info(f"한글 폰트 설정 완료: {plt.rcParams['font.family']}")
    except Exception as e:
        logger.error(f"한글 폰트 설정 중 오류 발생: {e}")