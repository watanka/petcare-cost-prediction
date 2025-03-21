import streamlit as st
import os

import datetime
from src.train import train_model
from src.configure import load_config, configure_data, configure_model, configure_preprocessing
from src.deploy import ModelDeploymentView
# 스타일 및 설정
st.set_page_config(page_title="PETCARE COST PREDICTION MODEL", layout="wide")


def main():
    st.title("Pet Insurance Claim Pipeline")
    
    # 설정 파일 로드
    base_config = load_config()
    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs([
        "데이터 분석",
        "모델 학습",
        "예측",
        "모델 배포"
    ])
    
    # 데이터 설정 탭
    with tab1:
        st.header("데이터 설정")
        data_config = configure_data(base_config.get("data_dir", "data_storage/records"))
    
    # 모델 설정 탭
    with tab2:
        st.header("모델 파라미터 설정")
        model_config = configure_model()
        
    # 전처리 설정 탭
    with tab3:
        st.header("컬럼별 전처리 설정")
        preprocess_config = configure_preprocessing(data_config)
    
    with tab4:
        deployment_view = ModelDeploymentView()
        deployment_view.render()

    # 사이드바 - 실험 설정 및 실행 버튼
    with st.sidebar:
        st.title("실험 관리")
        experiment_name = st.text_input("실험 이름", base_config.get("mlflow", {}).get("experiment_name", "petcare_cost_prediction"))
        run_name = st.text_input("실행 이름", f"run-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}")
        

        # 전체 설정 구성 - 기존 설정을 유지하면서 업데이트
        config = base_config.copy()  # 기존 설정 복사
        config.update({  # 새로운 설정 업데이트
            "name": experiment_name,
            "run_name": run_name,
            "data": data_config,
            "model": model_config,
            "preprocessing": preprocess_config})
        
        # 설정 표시
        if st.checkbox("설정 확인"):
            st.json(config)
        
        
        # 학습 버튼
        train_button = st.button("학습 시작", type="primary")
        
    # 학습 실행
    if train_button:
        with st.spinner("모델 학습 중..."):
            try:
                
                evaluation, artifact = train_model(config)
                
                st.success("학습이 완료되었습니다!")
                st.text(f'run_name: {config.get("run_name")}')
                st.dataframe(evaluation.eval_df)
                st.text(f'MAE: {evaluation.mean_absolute_error}')
                st.text(f'MAPE: {evaluation.mean_absolute_percentage_error}')
                st.text(f'RMSE: {evaluation.root_mean_squared_error}')
                
                # 학습 결과 저장
                st.session_state.last_run_name = config.get("run_name")
                st.session_state.last_model_path = artifact.model_file_path

            except Exception as e:
                st.error(f"학습 실행 중 오류가 발생했습니다: {e}")
                st.exception(e)
    

    # # 테스트 버튼
    # test_data = create_test_form(preprocess_config)
    
    # # 테스트 실행
    # if test_data:
    #     with st.spinner("테스트 중..."):
    #         test_prediction(config, test_data)

    

if __name__ == "__main__":
    main()
