import streamlit as st
import os

import datetime
from src.train import train_model
from src.configure import load_config, configure_data, configure_model, configure_preprocessing
# 스타일 및 설정
st.set_page_config(page_title="PETCARE COST PREDICTION MODEL", layout="wide")


def main():
    st.title("PETCARE COST PREDICTION MODEL")
    
    # 설정 파일 로드
    base_config = load_config()
    if not base_config:
        st.error("설정 파일을 로드할 수 없습니다. 기본값을 사용합니다.")
        base_config = {
            "data_dir": "data_storage/records",
            "model_dir": "models",
            "mlflow": {
                "tracking_uri": "http://localhost:5000",
                "experiment_name": "petcare_cost_prediction"
            }
        }
    
    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["데이터 선택", "모델 설정", "전처리 설정"])
    
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
        tracking_url = os.getenv("MLFLOW_TRACKING_URL", "http://localhost:5000")
        st.markdown(f"""
            <div style='text-align: center; margin: 20px 0;'>
                <a href='{tracking_url}' target='_blank'>
                    <button style='
                        background-color: #FF4B4B;
                        color: white;
                        padding: 10px 20px;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 16px;
                        font-weight: bold;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    '>
                        MLflow 실험 대시보드 열기
                    </button>
                </a>
            </div>
        """, unsafe_allow_html=True)
        
    # 학습 실행
    if train_button:
        with st.spinner("모델 학습 중..."):
            try:
                
                result = train_model(config)
                
                st.success("학습이 완료되었습니다!")
                st.text(f'run_id: {result.get("run_id")}')
                st.dataframe(result.get("evaluation").eval_df)
                st.text(f'MAE: {result.get("evaluation").mean_absolute_error}')
                st.text(f'MAPE: {result.get("evaluation").mean_absolute_percentage_error}')
                st.text(f'RMSE: {result.get("evaluation").root_mean_squared_error}')
                
                # 학습 결과 저장
                st.session_state.last_run_id = result.get("run_id")
                st.session_state.last_model_path = result.get("artifacts", [])
                
                # MLflow 대시보드 링크
                
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
