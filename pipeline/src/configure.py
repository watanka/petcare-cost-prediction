import streamlit as st
import pandas as pd
import datetime
import os
from glob import glob
import yaml

def load_config():
    """config.yml 파일에서 설정을 로드합니다."""
    config_path = os.path.join("./config.yml")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        st.error(f"설정 파일을 찾을 수 없습니다: {config_path}")
        return {}
    except yaml.YAMLError as e:
        st.error(f"설정 파일 파싱 중 오류 발생: {e}")
        return {}

def configure_data(data_dir):
    """데이터 선택 및 설정"""
    st.subheader("데이터 관리")
    
    # 데이터 디렉토리 구조
    archive_path = os.path.join(data_dir, "archive")
    os.makedirs(archive_path, exist_ok=True)
    
    # 날짜별 폴더 목록
    date_folders = [d for d in glob(os.path.join(data_dir, "*")) if os.path.isdir(d) and d != archive_path]
    date_folders.sort(reverse=True)  # 최신 날짜순 정렬
    
    if date_folders:
        # 날짜 폴더 선택 (다중 선택 가능)
        selected_folders = st.multiselect(
            "날짜 선택 (여러 개 선택 가능)",
            options=date_folders,
            format_func=lambda x: os.path.basename(x)
        )
        
        if selected_folders:
            # 선택된 폴더들의 데이터 로드 및 병합
            dfs = []
            for folder in selected_folders:
                csv_files = glob(f'{folder}/*.csv')
                if csv_files:
                    # 각 폴더의 첫 번째 CSV 파일 사용 (동일한 이름의 파일)
                    file_path = csv_files[0]
                    df = pd.read_csv(file_path)
                    dfs.append(df)
            
            if dfs:
                # 데이터프레임 병합
                df = pd.concat(dfs, ignore_index=True)
                
                # 데이터 미리보기
                st.subheader("선택된 데이터 미리보기")
                st.dataframe(df.head())
                
                # 데이터 정보
                st.subheader("데이터 정보")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("행 수", len(df))
                with col2:
                    st.metric("열 수", len(df.columns))
                with col3:
                    st.metric("중복 행", len(df) - len(df.drop_duplicates()))
                
                # 컬럼 정보
                st.subheader("컬럼 정보")
                st.dataframe(pd.DataFrame({
                    '컬럼명': df.columns,
                    '데이터 타입': df.dtypes,
                    '결측치 수': df.isnull().sum(),
                    '고유값 수': df.nunique()
                }))
                
                # 데이터 관리 옵션
                with st.expander("데이터 관리"):
                    if st.button("선택된 폴더 아카이브"):
                        for folder in selected_folders:
                            folder_name = os.path.basename(folder)
                            archive_folder = os.path.join(archive_path, f"archive_{folder_name}")
                            os.rename(folder, archive_folder)
                        st.success(f"선택된 폴더들이 아카이브되었습니다.")
                        st.experimental_rerun()
            else:
                st.warning("선택된 폴더에 CSV 파일이 없습니다.")
                return None
        else:
            st.warning("날짜 폴더를 선택해주세요.")
            return None
    else:
        st.warning(f"{data_dir} 경로에 날짜 폴더가 없습니다.")
        return None
    
    # 데이터 컬럼 정보 저장
    if "df_columns" not in st.session_state:
        st.session_state.df_columns = df.columns.tolist()
        st.session_state.df_dtypes = {col: str(df[col].dtype) for col in df.columns}
    
    test_split = st.slider("테스트 데이터 비율", 0.1, 0.5, 0.2, 0.05)
    
    # 날짜 범위 설정
    st.subheader("날짜 범위 설정")
    dates = [datetime.datetime.strptime(os.path.basename(folder), "%Y-%m-%d").date() for folder in selected_folders]
    min_date = min(dates)
    max_date = max(dates)
    
    col1, col2 = st.columns(2)
    with col1:
        date_from = st.date_input(
            "시작일",
            value=min_date
        )
    with col2:
        date_to = st.date_input(
            "종료일",
            value=max_date
        )
    
    # 데이터 설정 구성
    data_config = { 
        "source": [os.path.join(folder, glob(f'{folder}/*.csv')[0]) for folder in selected_folders],
        "dataframe": df,
        "details": {
            "date_from": date_from.strftime("%Y-%m-%d"),
            "date_to": date_to.strftime("%Y-%m-%d"),
            "test_split_ratio": test_split,
            "data_structure": {
                "selected_folders": selected_folders,
                "archive_path": archive_path
            }
        }
    }
    
    return data_config

def configure_model():
    """모델 파라미터 설정"""
    config = load_config()
    default_params = config.get("model_params", {}).get("light_gbm_regression_serving", {})
    
    model_type = st.selectbox("모델", ["light_gbm_regression_serving"])
    
    # 모델 타입에 따른 파라미터 설정
    if model_type == "light_gbm_regression_serving":
        num_leaves = st.slider("num_leaves", 2, 256, default_params.get("num_leaves", 31))
        learning_rate = st.slider("learning_rate", 0.01, 0.5, default_params.get("learning_rate", 0.05), 0.01)
        feature_fraction = st.slider("feature_fraction", 0.1, 1.0, default_params.get("feature_fraction", 0.9), 0.1)
        max_depth = st.slider("max_depth", -1, 20, default_params.get("max_depth", -1))
        num_iterations = st.number_input("num_iterations", 100, 1000000, default_params.get("num_iterations", 1000000))
        early_stopping_rounds = st.number_input("early_stopping_rounds", 10, 1000, default_params.get("early_stopping_rounds", 200))
        
        model_params = {
            "name": "light_gbm_regression_serving",
            "task": "train",
            "boosting": "gbdt",
            "objective": "regression",
            "num_leaves": num_leaves,
            "learning_rate": learning_rate,
            "feature_fraction": feature_fraction,
            "max_depth": max_depth,
            "num_iterations": num_iterations,
            "early_stopping_rounds": early_stopping_rounds,
            "seed": default_params.get("seed", 1234),
            "verbose_eval": default_params.get("verbose_eval", 1000),
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
            if col == 'price' or col == 'issued_at':
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