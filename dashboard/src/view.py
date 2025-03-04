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

logger = configure_logger(__name__)

class BI(Enum):
    INSURANCE_CLAIM = "실제 보험 청구금액"
    INSURANCE_CLAIM_PREDICTION_EVALUATION = "예측 보험 청구금액"
    
    
def init_container(insurance_claim_df: pd.DataFrame, prediction_df: pd.DataFrame) -> Container:
    container = Container(insurance_claim_df=insurance_claim_df, prediction_df=prediction_df)
    return container


def build_price_prediction_target_selectbox(container: Container) -> Tuple[Optional[Container], Optional[str]]:
    options = [None]
    _options = os.listdir(Configurations.insurance_claim_prediction_dir)
    options.extend(_options)
    selected = st.sidebar.selectbox(
        label="예측 요청 기간",
        options=options,
    )
    if selected == 'ALL':
        container.load_prediction_df(
            prediction_file_path=os.path.join(
                Configurations.insurance_claim_prediction_dir,
                selected,
                "prediction.csv",
            ),
        )
        return container, selected
    else:
        return None, None


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
) -> Optional[str]:
    variable_service = ServiceFactory.get_service(variable_name)
    options = variable_service.list_labels(container=container)
    options.append("ALL")
    selected = st.sidebar.selectbox(
        label=variable_name,
        options=options,
    )
    return selected


def build_sort_selectbox() -> str:
    options = ["pet_breed_id",
                "gender",
                "neutralized",
                "weight_kg",
                "age",
                "claim_price",
                "prediction",
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
            df[df.pet_breed_id == b]
            .drop(['pet_breed_id'], axis=1)
            .reset_index(drop=True)
        )
        st.dataframe(_df)
        
        price_range_max = _df.claim_price.max()
        with st.expander(
            label=f"BREED {b}",
            expanded=True,
        ):
            fig = px.line(
                _df,
                x="age",
                y="claim_price",
                color="pet_id",
                line_group = "pet_id",
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
    st.markdown("### Compare Diff")
    st.dataframe(df)
    fig = go.Figure()
    if 'claim_price' in df.columns:
        fig.add_trace(go.Bar(x=['실제보험청구액'], y=df['claim_price'], name='Claim Price'))
    fig.add_trace(go.Bar(x=['예측청구액'], y=df['prediction'], name='Prediction'))
    

    fig.update_layout(barmode='group', xaxis_title='항목', yaxis_title='금액', title='Comparison of Claim Price and Prediction')
    
    st.plotly_chart(fig)
    
    
    logger.info(f"diff at ")

def build_insurance_claims(
    container: Container,
    variable_list: List[str],
    claim_price_service: ClaimPriceService,
):
    logger.info("build item sales BI...")
    variable_filter = []
    for variable_name in variable_list:
        variable = build_variable_selectbox(
            container=container,
            variable_name=variable_name,
        )
        variable_filter.append(variable)
    df = claim_price_service.retrieve_claim_prices(
        container=container,
        variable_filter=variable_filter,
        # TODO: add other variables
    )

    breed = df.pet_breed_id.unique()
    

    show_insurance_prices(
        df=df,
        breeds=breed
    )
    
def build_aggregation_selectbox() -> str:
    options = ["pet_breed_id",
                "gender",
                "neutralized",
                "weight_kg",
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
        variable_name="Breed",
    )
    
    # 예측 대상값에 해당하는 breed, gender, neutralized 값의 평균 계산

    # aggregate_by = build_aggregation_selectbox()
    # sort_by = build_sort_selectbox()

    container, by_time = build_price_prediction_target_selectbox(container=container)
    if container is None or by_time is None:
        return

    logger.info(f'before view: {container.insurance_claim_df.shape}')
    logger.info(f'before view: {container.prediction_df.shape}')
    
    claim_price_df = claim_price_service.retrieve_claim_prices(container = container, breed = breed)
    claim_price_by_breed_evaluation_df = claim_price_prediction_service.aggregate_price_evaluation(
        container=container,
        claim_price_df=claim_price_df,
        breed = breed,
    )
    show_insurance_prices_predictions(
        df=claim_price_by_breed_evaluation_df,
        # aggregate_by=aggregate_by,
        # sort_by=sort_by,
    )
    


def build(
    variable_list: List[str],
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
            variable_list=variable_list,
            claim_price_service=claim_price_service,
            claim_price_prediction_service=claim_price_prediction_service,
            # INSURANCE_CLAIM_prediction_evaluation_service=INSURANCE_CLAIM_prediction_evaluation_service,
        )
    else:
        raise ValueError()