import streamlit as st
import os
import pandas as pd
import numpy as np
import mlflow
import datetime
from pathlib import Path
import json
from glob import glob
import yaml

# 스타일 및 설정
st.set_page_config(page_title="PETCARE COST PREDICTION MODEL", layout="wide")

def main():
    st.title("반려동물 보험료 예측 모델 학습 및 배포")
    
    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["데이터 선택", "모델 설정", "전처리 설정"])
    
    # 데이터 설정 탭
    with tab1:
        st.header("데이터 설정")
        data_config = configure_data(config.data_dir)
    
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
        experiment_name = st.text_input("실험 이름", "petcare_cost_prediction")
        run_name = st.text_input("실행 이름", f"run-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}")
        
        # 전체 설정 구성
        config = {
            "name": experiment_name,
            "data": data_config,
            "model": model_config,
            "preprocessing": preprocess_config,
        }
        
        # 설정 표시
        if st.checkbox("설정 확인"):
            st.json(config)
        
        # 학습 버튼
        train_button = st.button("학습 시작", type="primary")
        
        
    # 학습 실행
    if train_button:
        with st.spinner("모델 학습 중..."):
            try:
                from train import train_model
                result = train_model(config)
                
                st.success("학습이 완료되었습니다!")
                st.json(result)
                
                # 학습 결과 저장
                st.session_state.last_run_id = result.get("run_id")
                st.session_state.last_model_path = result.get("artifacts", [])
                
                # MLflow 링크 제공
                tracking_url = os.getenv("MLFLOW_TRACKING_URL", "http://localhost:5000")
                st.markdown(f"[MLflow 실험 대시보드 열기]({tracking_url})")
            except Exception as e:
                st.error(f"학습 실행 중 오류가 발생했습니다: {e}")
                st.exception(e)
    

def configure_data(data_dir):
    """데이터 선택 및 설정"""

    csv_files = glob(f'{data_dir}/**/*.csv', recursive=True)
    if csv_files:
        # 파일 이름만 표시를 위해 경로에서 추출
        file_options = [file_path for file_path in csv_files]
        file_display = [os.path.basename(file_path) for file_path in csv_files]
        
        # 파일 이름을 보여주고 실제 경로를 값으로 사용하는 딕셔너리 생성
        file_dict = dict(zip(file_display, file_options))
        
        selected_file_name = st.selectbox("CSV 파일 선택", options=file_display)
        data_path = file_dict[selected_file_name]
        
        st.success(f"선택된 파일: {data_path}")
    else:
        st.warning(f"{data_dir} 경로에 CSV 파일이 없습니다.")
        data_path = st.text_input("CSV 파일 경로 직접 입력", "data/pet_insurance_claim_ml_fake_data.csv")
    
    df = pd.read_csv(data_path)

    # 데이터 컬럼 정보 저장
    if "df_columns" not in st.session_state:
        st.session_state.df_columns = df.columns.tolist()
        st.session_state.df_dtypes = {col: str(df[col].dtype) for col in df.columns}
    
    # 타겟 변수 선택
    target_column = st.selectbox("타겟 변수", df.columns, index=df.columns.get_loc("claim_price") if "claim_price" in df.columns else 0)
    test_split = st.slider("테스트 데이터 비율", 0.1, 0.5, 0.2, 0.05)
    
    # 데이터 설정 구성
    data_config = { 
        "source": data_path,
        "dataframe": df,
        "target_column": target_column,
        "details": {
            "date_from": "2020-01-01",
            "date_to": datetime.datetime.now().strftime("%Y-%m-%d"),
            "test_split_ratio": test_split
        }
    }

    return data_config

def configure_model():
    """모델 파라미터 설정"""
    model_type = st.selectbox("모델", ["light_gbm_regression"])
    
    # 모델 타입에 따른 파라미터 설정
    if model_type == "light_gbm_regression":
        num_leaves = st.slider("num_leaves", 2, 256, 3)
        learning_rate = st.slider("learning_rate", 0.01, 0.5, 0.05, 0.01)
        feature_fraction = st.slider("feature_fraction", 0.1, 1.0, 0.5, 0.1)
        max_depth = st.slider("max_depth", -1, 20, -1)
        num_iterations = st.number_input("num_iterations", 100, 1000000, 1000000)
        early_stopping_rounds = st.number_input("early_stopping_rounds", 10, 1000, 200)
        
        model_params = {
            "task": "train",
            "boosting": "gbdt",
            "objective": "regression",
            "num_leaves": num_leaves,
            "learning_rate": learning_rate,
            "feature_fraction": feature_fraction,
            "max_depth": max_depth,
            "num_iterations": num_iterations,
            "early_stopping_rounds": early_stopping_rounds,
            "seed": 1234,
            "verbose_eval": 1000,
        }
    
    eval_metrics = st.selectbox("평가 지표", ["mse", "rmse", "mae", "mape"])
    
    model_config = {
        "name": model_type,
        "eval_metrics": eval_metrics,
        "params": model_params
    }
    
    return model_config

def configure_preprocessing(data_config):
    """컬럼별 전처리 설정"""
    columns_config = {}
    
    if "df_columns" in st.session_state:
        st.info("각 컬럼의 전처리 방식을 설정하세요.")
        
        for col in st.session_state.df_columns:
            # 타겟 변수는 제외
            if col == data_config.get("target_column"):
                continue
                
            st.subheader(f"컬럼: {col}")
            col_type = st.session_state.df_dtypes.get(col, "object")
            
            col_container = st.container()
            with col_container:
                # 컬럼 타입 선택
                data_type = st.selectbox(
                    "데이터 타입",
                    ["numeric", "categorical", "date", "text", "id"],
                    key=f"type_{col}",
                    index=0 if "int" in col_type or "float" in col_type else 1
                )
                
                # 컬럼 타입에 따른 전처리 방식 설정
                if data_type == "numeric":
                    handling = st.selectbox(
                        "전처리 방식",
                        ["standard_scale", "minmax_scale", "log_transform", "none"],
                        key=f"handling_{col}"
                    )
                    missing = st.selectbox(
                        "결측치 처리",
                        ["mean", "median", "zero", "drop"],
                        key=f"missing_{col}"
                    )
                    columns_config[col] = {
                        "type": data_type,
                        "handling": handling,
                        "missing_value": missing
                    }
                
                elif data_type == "categorical":
                    handling = st.selectbox(
                        "전처리 방식",
                        ["one_hot", "label", "target", "none"],
                        key=f"handling_{col}"
                    )
                    missing = st.selectbox(
                        "결측치 처리",
                        ["mode", "special_value", "drop"],
                        key=f"missing_{col}"
                    )
                    columns_config[col] = {
                        "type": data_type,
                        "handling": handling,
                        "missing_value": missing
                    }
                
                elif data_type == "date":
                    features = st.multiselect(
                        "추출할 특성",
                        ["year", "month", "day", "weekday", "age"],
                        key=f"features_{col}",
                        default=["age"] if "birth" in col.lower() else ["year", "month"]
                    )
                    columns_config[col] = {
                        "type": data_type,
                        "extract_features": features
                    }
                
                elif data_type == "text":
                    handling = st.selectbox(
                        "전처리 방식",
                        ["count_vectorizer", "tfidf", "none"],
                        key=f"handling_{col}"
                    )
                    columns_config[col] = {
                        "type": data_type,
                        "handling": handling
                    }
                
                elif data_type == "id":
                    handle_unknown = st.checkbox("알 수 없는 값 처리", key=f"unknown_{col}", value=True)
                    columns_config[col] = {
                        "type": data_type,
                        "handle_unknown": handle_unknown
                    }
    else:
        st.warning("먼저 데이터를 로드하세요.")
    
    # 전체 전처리 설정
    preprocess_config = {
        "columns": columns_config,
        "drop_columns": st.multiselect("제외할 컬럼", st.session_state.get("df_columns", []))
    }
    
    return preprocess_config

def configure_deployment():
    """MLServer 배포 설정"""
    st.info("MLServer를 통한 모델 배포 설정")
    
    server_host = st.text_input("서버 호스트", "localhost")
    server_port = st.number_input("서버 포트", 8080)
    model_name = st.text_input("모델 이름", "pet-insurance-claim-prediction")
    model_version = st.text_input("모델 버전", "v1")
    replicas = st.number_input("복제본 수", 1)
    
    convert_to_onnx = st.checkbox("ONNX 변환", value=True)
    
    # 추가 MLServer 설정
    with st.expander("고급 설정"):
        parallel_workers = st.number_input("병렬 워커 수", 1)
        timeout = st.number_input("타임아웃(초)", 60)
        enable_docs = st.checkbox("API 문서 활성화", value=True)
    
    deploy_config = {
        "server_host": server_host,
        "server_port": server_port,
        "model_name": model_name.lower().replace(" ", "-"),
        "model_version": model_version,
        "replicas": replicas,
        "convert_to_onnx": convert_to_onnx,
        "advanced": {
            "parallel_workers": parallel_workers,
            "timeout": timeout,
            "enable_docs": enable_docs
        }
    }
    
    return deploy_config

def create_test_form(columns_config):
    """테스트 데이터 입력 폼 생성"""
    test_data = {}
    
    st.subheader("테스트 입력")
    for col, config in columns_config.items():
        col_type = config.get("type")
        
        if col_type == "numeric":
            test_data[col] = st.number_input(f"{col}", key=f"test_{col}")
        elif col_type == "categorical":
            test_data[col] = st.text_input(f"{col}", key=f"test_{col}")
        elif col_type == "date":
            test_data[col] = st.date_input(f"{col}", key=f"test_{col}")
        elif col_type == "text":
            test_data[col] = st.text_area(f"{col}", key=f"test_{col}")
        elif col_type == "id":
            test_data[col] = st.number_input(f"{col}", key=f"test_{col}")
    
    return test_data

def test_prediction(endpoint, test_data):
    """예측 테스트 실행"""
    import requests
    import json
    import numpy as np
    
    # 테스트 데이터를 MLServer 형식으로 변환
    inference_request = {
        "inputs": [
            {
                "name": "predict-data",
                "shape": [1, len(test_data)],
                "datatype": "FP32",
                "data": [list(test_data.values())]
            }
        ]
    }
    
    # API 요청
    response = requests.post(endpoint, json=inference_request)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"API 오류: {response.status_code}", "message": response.text}

if __name__ == "__main__":
    main()
