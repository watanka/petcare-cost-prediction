import os
from enum import Enum
from typing import List, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from configurations import Configurations
from logger import configure_logger
from model import Container
from plotly.subplots import make_subplots
from service import ServiceFactory, ClaimPriceService, ClaimPricePredictionService
import json
from PIL import Image

logger = configure_logger(__name__)

class BI(Enum):
    INSURANCE_CLAIM = "실제 보험 청구금액"
    INSURANCE_CLAIM_PREDICTION_EVALUATION = "예측 보험 청구금액"
    
    
def init_container() -> Container:
    container = Container()
    container.load_insurance_claim_df(os.path.join(Configurations.insurance_claim_record_file))
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


def build_variable_selectbox(
    container: Container,
    variable_name: str,
    variable_type: str,
) -> Optional[str]:
    variable_service = ServiceFactory.get_service(variable_name, variable_type)
    options = variable_service.list_labels(container=container)
    
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

def build_variable_slider(
    container: Container,
    variable_name: str,
    variable_type: str,
) -> Optional[str]:
    variable_service = ServiceFactory.get_service(variable_name, variable_type)
    options = variable_service.list_labels(container=container)
    selected = st.sidebar.slider(
        label=variable_name,
        min_value=options[0],
        max_value=options[-1],
        value=(options[0], options[-1]),
    )
    return selected



def build_sort_selectbox() -> str:
    options = ["pet_breed_id",
                "gender",
                "neutralized",
                "weight",
                "age",
                "price",
                "predicted_price",
                "diff",
                "error_rate",
                ]
    selected = st.sidebar.selectbox(
        label="sort by",
        options=options,
    )
    return selected


def show_insurance_prices(
    df: pd.DataFrame,
    breeds: List[str],
    gender: Optional[str] = None,
    neutralized: Optional[str] = None,
):
    st.markdown("### 결과 요약")
    for b in breeds:
        _df = (
            df[df.breed == b]
            .drop(['breed'], axis=1)
            .reset_index(drop=True)
        )
        st.dataframe(_df)
        
        price_range_max = _df.price.max()
        with st.expander(
            label=f"BREED {b}",
            expanded=True,
        ):
            fig = px.line(
                _df,
                x="age",
                y="price",
                color="district",
                line_group = "district",
                title=f"BREED {b}",
            )
            fig.update_yaxes(range=[0, price_range_max])
            st.plotly_chart(fig, use_container_width=True)
            logger.info(f"BREED {b}")


def show_insurance_prices_predictions(
    df: pd.DataFrame,
    breeds: List[str] = None,
    gender: Optional[str] = None,
    neutralized: Optional[str] = None,
):
    st.markdown("#### CSV")
    st.dataframe(df)
    fig = go.Figure()
    
    fig.add_trace(go.Bar(x=['실제보험청구액'], y=df['price'], name='Claim Price'))
    fig.add_trace(go.Bar(x=['예측청구액'], y=df['predicted_price'], name='Prediction'))
    

    fig.update_layout(barmode='group', xaxis_title='항목', yaxis_title='금액', title='실제값과 예측값 비교')
    
    st.plotly_chart(fig)
    
    
    logger.info(f"diff at ")

def display_seoul_map(district_stats: pd.DataFrame):
    """
    서울 구별 통계를 지도로 시각화
    """
    # 1. 기본 레이아웃
    st.subheader("서울시 구별 보험금 청구 현황")
    
    # 2. 표시할 데이터 선택
    col1, col2 = st.columns(2)
    with col1:
        display_option = st.selectbox(
            "표시할 데이터",
            ["평균 청구금액", "평균 예측금액", "청구 건수", "오차율"],
            index=0
        )
    
    # 3. 데이터 매핑
    value_map = {
        "평균 청구금액": "avg_claim_price",
        "평균 예측금액": "avg_predicted_price",
        "청구 건수": "claim_count",
        "오차율": "error_rate"
    }
    
    # 4. 데이터 테이블 표시
    with col2:
        st.dataframe(
            district_stats[[
                'district', 
                'avg_claim_price', 
                'avg_predicted_price', 
                'claim_count', 
                'error_rate'
            ]].sort_values('district'),
            height=300
        )
    
    # 5. 막대 그래프로 시각화
    fig = px.bar(
        district_stats,
        x='district',
        y=value_map[display_option],
        title=f'서울시 구별 {display_option}',
        labels={'district': '지역구', value_map[display_option]: display_option},
        color=value_map[display_option],
        color_continuous_scale='RdYlBu_r'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        width=800
    )
    
    st.plotly_chart(fig)
    
    # 6. 통계 요약
    st.subheader("통계 요약")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "평균 청구금액이 가장 높은 구",
            f"{district_stats.loc[district_stats['avg_claim_price'].idxmax(), 'district']}",
            f"{int(district_stats['avg_claim_price'].max()):,}원"
        )
    
    with col2:
        st.metric(
            "청구 건수가 가장 많은 구",
            f"{district_stats.loc[district_stats['claim_count'].idxmax(), 'district']}",
            f"{int(district_stats['claim_count'].max()):,}건"
        )
    
    with col3:
        st.metric(
            "예측 오차율이 가장 낮은 구",
            f"{district_stats.loc[district_stats['error_rate'].abs().idxmin(), 'district']}",
            f"{district_stats['error_rate'].abs().min():.2f}%"
        )

def build_insurance_claims(
    container: Container,
    variable_list: List[Tuple[str, str]],
    claim_price_service: ClaimPriceService,
):
    logger.info("build item sales BI...")
    variable_filter = []
    for variable_name, variable_type in variable_list:
        selected = build_variable_selectbox(
            container=container,
            variable_name=variable_name,
            variable_type=variable_type,
        )
        variable_filter.append((variable_name, selected))

    df = claim_price_service.retrieve_claim_prices(
        container=container,
        variable_filter=variable_filter,
        # TODO: add other variables
    )

    breed = df.breed.unique()
    

    show_insurance_prices(
        df=df,
        breeds=breed
    )
    
    # 구별 통계 계산 및 시각화
    claim_price_prediction_service = ClaimPricePredictionService()
    district_stats = claim_price_prediction_service.calculate_district_statistics(
        container=container,
        claim_price_df=df
    )
    
    display_seoul_map(district_stats)
    
    # 기존의 데이터프레임 표시
    st.dataframe(
        df,
        height=300,
    )
    
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

def build_insurance_claims_prediction_evaluation(
                                container: Container,  
                                claim_price_service: ClaimPriceService,
                                claim_price_prediction_service: ClaimPricePredictionService
                                ):
    logger.info("build insurance price prediction evaluation BI...")
    breed = build_variable_selectbox(
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

    # logger.info(f'before view: {container.insurance_claim_df.shape}')
    # logger.info(f'before view: {container.prediction_df.shape}')
    
    claim_price_df = claim_price_service.retrieve_claim_prices(container = container, variable_filter = [('breed', breed)])
    claim_price_by_breed_evaluation_df = claim_price_prediction_service.aggregate_price_evaluation(
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
    claim_price_service: ClaimPriceService,
    claim_price_prediction_service: ClaimPricePredictionService,
):
    st.markdown("# 양육비 예측 대시보드")

    bi = build_bi_selectbox()

    if bi is None:
        return
    elif bi == BI.INSURANCE_CLAIM.value:
        build_insurance_claims(
            container=container,
            variable_list=variable_list,
            claim_price_service=claim_price_service, 
        )
    elif bi == BI.INSURANCE_CLAIM_PREDICTION_EVALUATION.value:
        build_insurance_claims_prediction_evaluation(
            container=container,
            claim_price_service=claim_price_service,
            claim_price_prediction_service=claim_price_prediction_service,
            # INSURANCE_CLAIM_prediction_evaluation_service=INSURANCE_CLAIM_prediction_evaluation_service,
        )
    else:
        raise ValueError()