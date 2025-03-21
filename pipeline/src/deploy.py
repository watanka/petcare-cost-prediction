from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import json
import requests
from typing import Dict, List
from dataclasses import dataclass
import os
from src.logger import setup_logger
import docker

DEPLOY_URL = os.getenv("DEPLOY_URL")

MLSERVER1_HOST = os.getenv("MLSERVER1_HOST", "petcare-mlserver1")
MLSERVER2_HOST = os.getenv("MLSERVER2_HOST", "petcare-mlserver2")
MODEL_WEIGHT_PATH = os.getenv("MODEL_WEIGHT_PATH", "/app/data_storage/train_results/")
MLSERVER1_PORT = os.getenv("MLSERVER1_PORT", 8000)
MLSERVER2_PORT = os.getenv("MLSERVER2_PORT", 8002)


logger = setup_logger(__name__)

@dataclass
class ExperimentResult:
    name: str
    mean_absolute_error: float
    mean_absolute_percentage_error: float
    root_mean_squared_error: float

class ModelDeploymentView:
    def __init__(self, experiments_dir: str = "data_storage/train_results"):
        self.experiments_dir = Path(experiments_dir)
        
    def load_experiments(self) -> List[ExperimentResult]:
        """모든 실험 결과 로드"""
        experiments = []
        for exp_dir in self.experiments_dir.glob("*"):
            if exp_dir.is_dir():
                metrics_file = exp_dir / "metrics.json"
                if metrics_file.exists():
                    with open(metrics_file, "r") as f:
                        metrics = json.load(f)
                        experiments.append(ExperimentResult(
                            name=exp_dir.name,
                            **metrics
                        ))
        return experiments

    def plot_metrics_comparison(self, experiments_df: pd.DataFrame):
        """메트릭 비교 시각화"""
        metrics_df = pd.melt(
            experiments_df,
            id_vars=['name'],
            value_vars=['mean_absolute_error', 'mean_absolute_percentage_error', 'root_mean_squared_error'],
            var_name='metric',
            value_name='value'
        )
        
        fig = px.line(
            metrics_df,
            x='name',
            y='value',
            color='metric',
            title='모델 성능 지표 비교',
            labels={
                'name': '실험 이름',
                'value': '값',
                'metric': '지표'
            }
        )
        return fig

    def deploy_model(self, model_name: str) -> bool:
        """모델 배포 요청"""
        model_path = os.path.join(MODEL_WEIGHT_PATH, model_name)
        logger.info(f"배포할 모델 경로: {model_path}")

        if self._restart_container(MLSERVER1_HOST, model_path):
            logger.info("MLserver1 restart successful")
        else:
            logger.error("MLserver1 restart failed")
        
        # MLserver2 재시작
        logger.info("Restarting MLserver2...")
        if self._restart_container(MLSERVER2_HOST, model_path):
            logger.info("MLserver2 restart successful")
            return {"status": "success"}
        else:
            logger.error("MLserver2 restart failed")
            return False
        
    def render_performance_section(self, df: pd.DataFrame):
        """성능 지표 섹션 렌더링"""
        st.subheader("모델 성능 추이")
        fig = self.plot_metrics_comparison(df)
        st.plotly_chart(fig, use_container_width=True)
    
        

    def render_deployment_section(self, df: pd.DataFrame):
        """배포 섹션 렌더링"""
        col3, col4 = st.columns([1, 1])
        options = df['name'].tolist()

        with col3:
            selected_model = st.selectbox(
                "배포할 모델 선택",
                options=options,
            )
        with col4:
            st.markdown("### 배포 설정")
            self.handle_deployment(selected_model)

    def handle_deployment(self, model_name: str):
        """배포 처리"""
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f"""
            **배포할 모델 정보**
            - Model Name: {model_name}
            """)
        
        with col2:
            if st.button("모델 배포", type="primary"):
                # 배포 진행 상태 표시
                with st.spinner('모델 배포 중...'):
                    success = self.deploy_model(
                        model_name,
                    )
                    
                    if success:
                        st.success("모델이 성공적으로 배포되었습니다!")
                    else:
                        st.error("모델 배포 중 오류가 발생했습니다.")

    def render(self):
        """뷰 렌더링"""
        st.header("모델 배포 설정")
        
        experiments = self.load_experiments()
        if not experiments:
            st.warning("학습된 모델이 없습니다.")
            return
            
        df = pd.DataFrame(experiments)
        
        self.render_performance_section(df)
        st.subheader("모델 배포")
        self.render_deployment_section(df)

    def _restart_container(self, container_name: str, model_path: str):
        client = docker.from_env()
        try:
            # 기존 컨테이너 가져오기
            container = client.containers.get(container_name)
            
            # 컨테이너 설정 백업
            config = container.attrs
            host_config = config['HostConfig']
            
            # 1. 기존 컨테이너 중지 및 제거
            logger.info(f"Stopping and removing container {container_name}")

            # 현재 처리중인 요청이 있는지 확인필요
            container.stop()
            container.remove()
            
            # 2. 새로운 환경변수로 컨테이너 재생성
            logger.info(f"Creating new container {container_name} with model path: {model_path}")
            new_container = client.containers.create(
                image=config['Config']['Image'],
                name=container_name,
                environment={
                    **dict(env.split('=') for env in config['Config'].get('Env', []) if '=' in env),
                    'MODEL_WEIGHT_PATH': model_path
                },
                volumes=host_config.get('Binds', []),
                ports={port: host_config['PortBindings'].get(port, []) 
                       for port in config['Config'].get('ExposedPorts', {})},
                network_mode=host_config.get('NetworkMode', 'default'),
                detach=True
            )
            
            # 3. 새 컨테이너 시작
            logger.info(f"Starting new container {container_name}")
            new_container.start()
            
            logger.info(f"Container {container_name} successfully restarted with new model path")
            return True
        
        except Exception as e:
            logger.error(f"Container restart failed: {str(e)}")
            return False