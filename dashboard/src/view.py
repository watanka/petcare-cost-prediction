import os
from enum import Enum
from typing import List, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from configurations import Configurations
from logger import configure_logger
from model import Container

from service import DataStatisticsService, PredictionStatisticsService, DistrictStatisticsService
from ui import OptionFactory
from map_visualization import display_seoul_map_streamlit

logger = configure_logger(__name__)

class BI(Enum):
    INSURANCE_CLAIM = "실제 보험 청구금액"
    INSURANCE_CLAIM_PREDICTION_EVALUATION = "예측 보험 청구금액"
    
    
def init_container() -> Container:
    container = Container()
    
    # 보험 청구 데이터 로드
    try:
        insurance_claim_df = pd.read_csv("data_storage/insurance_claim.csv")
        container.insurance_claim_df = insurance_claim_df
    except Exception as e:
        logger.error(f"보험 청구 데이터 로드 중 오류 발생: {e}")
        st.error("보험 청구 데이터를 로드할 수 없습니다.")
    
    # 예측 데이터 로드 시도
    try:
        prediction_file_path = "data_storage/prediction/2025-03-01/prediction.csv"
        if os.path.exists(prediction_file_path):
            prediction_df = pd.read_csv(prediction_file_path)
            container.prediction_df = prediction_df
            logger.info("예측 데이터 로드 성공")
        else:
            logger.warning(f"예측 데이터 파일이 존재하지 않습니다: {prediction_file_path}")
    except Exception as e:
        logger.error(f"예측 데이터 로드 중 오류 발생: {e}")
    
    return container


def build_price_prediction_target_selectbox(container: Container) -> Tuple[Optional[Container], Optional[str]]:
    _options = os.listdir(Configurations.insurance_claim_prediction_dir)
    options = ['ALL']
    options.extend(_options)
    selected = st.sidebar.selectbox(
        label="예측 요청 기간",
        options=options,
    )
    if selected == 'ALL':
        container.combine_records(
            [
                pd.read_csv(os.path.join(
                    Configurations.insurance_claim_prediction_dir,
                    selected,
                    "prediction.csv",
                ))
                for selected in _options
            ]
        )
    else:
        container.load_prediction_df(
            file_path=os.path.join(
                Configurations.insurance_claim_prediction_dir,
                selected,
                "prediction.csv",
            ),
        )
    return container, selected
    

def build_bi_selectbox() -> str:
    options = [None, BI.INSURANCE_CLAIM.value, BI.INSURANCE_CLAIM_PREDICTION_EVALUATION.value]
    selected = st.sidebar.selectbox(
        label="BI",
        options=options,
    )
    return selected


def compose_option_button(
    container: Container,
    variable_name: str,
    variable_type: str,
) -> Optional[str]:
    variable_option = OptionFactory.get_option(variable_name, variable_type)
    options = variable_option.list_labels(container=container)
    
    if variable_type == 'numeric':
        selected = st.sidebar.slider(
            label=variable_name,
            min_value=options[0],
            max_value=options[-1],
            value=(options[0], options[-1]),
        )
        return selected
    elif variable_type == 'category':
        options.append("ALL")
        selected = st.sidebar.selectbox(
            label=variable_name,
            options=options,
        )
        return selected



def show_insurance_prices_predictions(df: pd.DataFrame):
    st.markdown("#### CSV")
    st.dataframe(df)
    fig = go.Figure()
    
    fig.add_trace(go.Bar(x=['실제보험청구액'], y=df['price'], name='Claim Price'))
    fig.add_trace(go.Bar(x=['예측청구액'], y=df['predicted_price'], name='Prediction'))
    

    fig.update_layout(barmode='group', xaxis_title='항목', yaxis_title='금액', title='실제값과 예측값 비교')
    
    st.plotly_chart(fig)
    
    
    logger.info(f"diff at ")



def visualize_map(container: Container, 
                  district_stat_service: DistrictStatisticsService, 
                  tab, 
                  filtered_df: pd.DataFrame, 
                  prediction_df: pd.DataFrame
):
    logger.info("build visualize map...")
    district_stats = district_stat_service.retrieve(
        container=container,
        filtered_df=filtered_df,
        prediction_df=prediction_df,
    )
    logger.info(f"district_stats: {district_stats.columns}")
    
    if district_stats is not None:
        # 지도 시각화 탭 추가
        with tab:
            # 지도 시각화
            display_seoul_map_streamlit(district_stats)
    else:
        # 기본 데이터프레임 표시
        st.dataframe(
            filtered_df,
            height=300,
        )


def setup_options(container: Container, variable_list: List[Tuple[str, str]]):
    options = []
    for variable_name, variable_type in variable_list:
        options.append((variable_name, compose_option_button(
            container=container,
            variable_name=variable_name,
            variable_type=variable_type,
        )))

    return options

def collect_statistics(container: Container, data_stat_service: DataStatisticsService, options: List[Tuple[str, str]], tab):
    logger.info("collect statistics...")
    filtered_df = data_stat_service.retrieve(
        container=container,
        variable_filter=options,
    )

    with tab:
        # 기존 데이터프레임 표시
        st.dataframe(
            filtered_df,
            height=300,
        )
        
        # 기존 시각화 코드
        # claim_price_evaluation_df = prediction_service.aggregate_price_evaluation(
        #     container=container,
        #     claim_price_df=df,
        # )

            
        st.line_chart(filtered_df, x='issued_at', y='price', color='pet_id')
        
    
    return filtered_df
    

def build_aggregation_selectbox() -> str:
    options = ["breed",
                "gender",
                "neutralized",
                "weight",
                "age",
                ]
    selected = st.sidebar.selectbox(
        label="aggregate by",
        options=options,
    )
    return selected


def visualize_prediction_evaluation(
                                container: Container,  
                                data_stat_service: DataStatisticsService,
                                prediction_service: PredictionStatisticsService
                                ):
    logger.info("build insurance price prediction evaluation BI...")
    breed = compose_option_button(
        container=container,
        variable_name="breed",
        variable_type="category",
    )
    
    # 예측 대상값에 해당하는 breed, gender, neutralized 값의 평균 계산

    # aggregate_by = build_aggregation_selectbox()
    # sort_by = build_sort_selectbox()

    container, by_time = build_price_prediction_target_selectbox(container=container)
    if container is None or by_time is None:
        return

    
    claim_price_df = data_stat_service.retrieve(container = container, variable_filter = [('breed', breed)])
    claim_price_by_breed_evaluation_df = prediction_service.aggregate_price_evaluation(
        container=container,
        claim_price_df=claim_price_df,
    )
    show_insurance_prices_predictions(
        df=claim_price_by_breed_evaluation_df,
        # aggregate_by=aggregate_by,
        # sort_by=sort_by,
    )
    


def build(
    variable_list: List[Tuple[str, str]],
    container: Container,
    data_stat_service: DataStatisticsService,
    prediction_service: PredictionStatisticsService,
    district_stat_service: DistrictStatisticsService,
):
    st.markdown("# 양육비 예측 대시보드")

    bi = build_bi_selectbox()

    filtered_df = None
    prediction_df = None
    
    if bi == BI.INSURANCE_CLAIM.value:
        options = setup_options(container=container,
            variable_list=variable_list,
        )
        tab1, tab2 = st.tabs(["데이터 분석", "지역별 분석"])

        filtered_df = collect_statistics(
            container=container,
            data_stat_service=data_stat_service,
            options = options,
            tab=tab1,
        )
        visualize_map(
            container=container,
            district_stat_service=district_stat_service,
            filtered_df = filtered_df,
            prediction_df = prediction_service.retrieve(container=container),
            tab=tab2
        )
    elif bi == BI.INSURANCE_CLAIM_PREDICTION_EVALUATION.value:
        visualize_prediction_evaluation(
            container=container,
            data_stat_service=data_stat_service,
            prediction_service=prediction_service,
        )