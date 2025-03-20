import streamlit as st



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
