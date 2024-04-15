import hydra
from omegaconf import DictConfig
from src.configurations import Configurations

@hydra.main(
    config_path="/opt/hydra",
    config_name=Configurations.target_config_name
)
def main(cfg: DictConfig):
    
    # experiment 설정
    
    # 데이터 설정
    
    # 데이터 전처리 파이프라인
    
    # 데이터 받아오기
    
    # 모델 학습
    



if __name__ == '__main__':
    main()