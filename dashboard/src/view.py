import os
from enum import Enum
from typing import List, Optional, Tuple
import re
import numpy as np

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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
        available_dates = [f for f in os.listdir(container.config.insurance_claim_records_dir) 
                          if os.path.isdir(os.path.join(container.config.insurance_claim_records_dir, f)) 
                          and re.match(r'\d{4}-\d{2}-\d{2}', f)]
        available_dates.sort(reverse=True)  # 최신 날짜가 먼저 오도록 정렬
        insurance_claim_df = pd.read_csv(f"{container.config.insurance_claim_records_dir}/{available_dates[0]}/insurance_claim.csv")
        container.insurance_claim_df = insurance_claim_df
    except Exception as e:
        logger.error(f"보험 청구 데이터 로드 중 오류 발생: {e}")
        st.error("보험 청구 데이터를 로드할 수 없습니다.")
    
    return container


# def build_price_prediction_target_selectbox(container: Container, selected) -> Tuple[Optional[Container], Optional[str]]:
#     _options = os.listdir(Configurations.insurance_claim_prediction_dir)
#     options = ['ALL']
#     options.extend(_options)
#     selected = st.sidebar.selectbox(
#         label="예측 요청 기간",
#         options=options,
#     )
#     if selected == 'ALL':
#         container.combine_records(
#             [
#                 pd.read_csv(os.path.join(
#                     Configurations.insurance_claim_prediction_dir,
#                     selected,
#                     "prediction.csv",
#                 ))
#                 for selected in _options
#             ]
#         )
#     else:
#         container.load_prediction_df(
#             file_path=os.path.join(
#                 Configurations.insurance_claim_prediction_dir,
#                 selected,
#                 "prediction.csv",
#             ),
#         )
#     return container, selected


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
            key=f"slider_{variable_name}"
        )
        return selected
    elif variable_type == 'category':
        options.append("ALL")
        selected = st.sidebar.selectbox(
            label=variable_name,
            options=options,
            key=f"selectbox_{variable_name}"
        )
        return selected


def visualize_map(container: Container, 
                  district_stat_service: DistrictStatisticsService, 
                  tab, 
):
    logger.info("build visualize map...")

    filtered_df = container.insurance_claim_df
    prediction_df = container.prediction_df

    district_stats = district_stat_service.retrieve(
        container=container,
        filtered_df=filtered_df,
        # prediction_df=prediction_df,
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


def setup_options(container: Container, variable_list: List[Tuple[str, str]] = []):
    options = []
    for variable_name, variable_type in variable_list:
        options.append((variable_name, compose_option_button(
            container=container,
            variable_name=variable_name,
            variable_type=variable_type,
        )))

    return options

def setup_dataframe(container: Container, options: List[Tuple[str, str]]):
    for variable_name, selected in options:
        logger.info(f"variable_name: {variable_name}, selected: {selected}")
        if variable_name == 'date':
            if selected == 'ALL':
                df = pd.concat(
                    [
                        pd.read_csv(os.path.join(
                            container.config.insurance_claim_records_dir,
                            dirname,
                            "insurance_claim.csv",
                        ))
                        for dirname in os.listdir(container.config.insurance_claim_records_dir)
                    ]
                )
                container.set_insurance_claim_df(df)
            else:
                df = pd.read_csv( 
                    os.path.join(
                        container.config.insurance_claim_records_dir,
                        selected,
                        "insurance_claim.csv",
                    ),
                )
                container.set_insurance_claim_df(df)
            break



def collect_statistics(container: Container, data_stat_service: DataStatisticsService, options: List[Tuple[str, str]], tab):
    logger.info("collect statistics...")
    filtered_df = data_stat_service.retrieve(
        container=container,
        variable_filter=options,
    )

    with tab:
        # 기존 데이터프레임 표시
        if filtered_df is not None:
            st.dataframe(
                filtered_df,
                height=300,
            )
            st.line_chart(filtered_df, x='issued_at', y='price', color='pet_id')
        else:
            st.sidebar.error("선택된 데이터가 없습니다.")
    
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


def visualize_prediction_evaluation(container: Container,prediction_service: PredictionStatisticsService):
    insurance_claim_df = container.insurance_claim_df
    
    # 1. 날짜 폴더 목록 가져오기
    prediction_dates = [f for f in os.listdir(container.config.insurance_claim_prediction_dir) 
                       if os.path.isdir(os.path.join(container.config.insurance_claim_prediction_dir, f)) 
                       and re.match(r'\d{4}-\d{2}-\d{2}', f)]
    prediction_dates.sort()  # 날짜순 정렬
    logger.info(f"prediction_dates: {prediction_dates}")
    if not prediction_dates:
        st.error("예측 데이터가 없습니다. data_storage/{yyyy-mm-dd} 형식의 폴더를 확인해주세요.")
        return
    
    # 2. 사용자가 날짜 선택
    selected_date = st.selectbox(
        "예측 날짜 선택",
        options=prediction_dates,
        index=0
    )
    
    # 3. 선택된 날짜 폴더 내의 모델 목록 가져오기
    date_path = os.path.join(container.config.insurance_claim_prediction_dir, selected_date)
    model_folders = [f for f in os.listdir(date_path) 
                    if os.path.isdir(os.path.join(date_path, f))]
    logger.info(f"model_folders: {model_folders}")
    if not model_folders:
        st.error(f"선택한 날짜({selected_date})에 모델 데이터가 없습니다.")
        return
    
    # 4. 모델 데이터 로드
    model_data = {}
    for model_name in model_folders:
        file_path = os.path.join(date_path, model_name, 'prediction.csv')
        if os.path.exists(file_path):
            try:
                prediction_df = pd.read_csv(file_path)
                # 예측 데이터와 실제 데이터 병합 및 분석
                comparison_df = prediction_service.summarize_prediction(
                    container=container,
                    insurance_claim_df=insurance_claim_df,
                    prediction_df=prediction_df,
                )
                model_data[model_name] = comparison_df
            except Exception as e:
                st.warning(f"모델 '{model_name}'의 데이터를 로드하는 중 오류 발생: {str(e)}")
    
    if not model_data:
        st.error("로드할 수 있는 모델 데이터가 없습니다.")
        return

    # 5. 모델별 요약 통계 계산
    model_summary = []
    
    for model_name, df in model_data.items():
        avg_price = df['price'].mean()
        avg_pred = df['predicted_price'].mean()
        avg_diff = df['diff'].mean()
        avg_error = df['error_rate'].mean() * 100  # 백분율로 표시
        mse = (df['diff'] ** 2).mean()
        rmse = np.sqrt(mse)
        mae = df['diff'].abs().mean()
        
        model_summary.append({
            '모델명': model_name,
            '평균 실제가': f"{avg_price:,.0f}원",
            '평균 예측가': f"{avg_pred:,.0f}원",
            '평균 차이': f"{avg_diff:,.0f}원",
            '평균 오차율': f"{avg_error:.2f}%",
            'MSE': f"{mse:.0f}",
            'RMSE': f"{rmse:.0f}",
            'MAE': f"{mae:.0f}",
            'raw_price': avg_price,
            'raw_pred': avg_pred,
            'raw_diff': avg_diff,
            'raw_error': avg_error,
            'raw_mse': mse,
            'raw_rmse': rmse,
            'raw_mae': mae
        })
    
    # 6. 요약 통계 표시
    st.markdown(f"### {selected_date} 날짜의 모델별 예측 결과 요약")
    
    summary_df = pd.DataFrame(model_summary)
    display_df = summary_df.drop(columns=[col for col in summary_df.columns if col.startswith('raw_')])
    
    st.dataframe(
        display_df,
        column_config={
            "모델명": st.column_config.TextColumn("모델명", width="medium"),
            "평균 실제가": st.column_config.TextColumn("평균 실제가", width="medium"),
            "평균 예측가": st.column_config.TextColumn("평균 예측가", width="medium"),
            "평균 차이": st.column_config.TextColumn("평균 차이", width="medium"),
            "평균 오차율": st.column_config.TextColumn("평균 오차율", width="medium"),
            "MSE": st.column_config.TextColumn("MSE", width="small"),
            "RMSE": st.column_config.TextColumn("RMSE", width="small"),
            "MAE": st.column_config.TextColumn("MAE", width="small"),
        },
        hide_index=True,
        use_container_width=True,
    )
    
    # 7. 시각화: 모델별 실제가와 예측가 비교 (막대 그래프)
    st.markdown("### 모델별 실제가와 예측가 비교")
    
    fig1 = go.Figure()
    
    for i, model_name in enumerate(summary_df['모델명']):
        fig1.add_trace(go.Bar(
            x=[f"{model_name} (실제)"],
            y=[summary_df.loc[i, 'raw_price']],
            name=f"{model_name} (실제)",
            marker_color='royalblue'
        ))
        fig1.add_trace(go.Bar(
            x=[f"{model_name} (예측)"],
            y=[summary_df.loc[i, 'raw_pred']],
            name=f"{model_name} (예측)",
            marker_color='lightcoral'
        ))
    
    fig1.update_layout(
        barmode='group',
        xaxis_title='모델 및 유형',
        yaxis_title='금액 (원)',
        title=f'{selected_date} 날짜의 모델별 실제가와 예측가 비교',
        legend_title="구분",
        height=500
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # 8. 시각화: 모델별 오차율 비교 (막대 그래프)
    st.markdown("### 모델별 예측 오차율")
    
    fig2 = go.Figure()
    
    fig2.add_trace(go.Bar(
        x=summary_df['모델명'],
        y=summary_df['raw_error'],
        marker_color=['red' if x > 0 else 'green' for x in summary_df['raw_error']],
        text=[f"{x:.2f}%" for x in summary_df['raw_error']],
        textposition='auto'
    ))
    
    fig2.update_layout(
        xaxis_title='모델명',
        yaxis_title='오차율 (%)',
        title=f'{selected_date} 날짜의 모델별 예측 오차율 비교',
        height=400
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # 9. 시각화: 모델별 MSE, RMSE, MAE 비교 (레이더 차트)
    st.markdown("### 모델별 오차 지표 비교")
    
    # 레이더 차트용 데이터 준비
    metrics = ['MSE', 'RMSE', 'MAE']
    
    fig3 = go.Figure()
    
    for i, model_name in enumerate(summary_df['모델명']):
        fig3.add_trace(go.Scatterpolar(
            r=[summary_df.loc[i, 'raw_mse'], 
               summary_df.loc[i, 'raw_rmse'], 
               summary_df.loc[i, 'raw_mae']],
            theta=metrics,
            fill='toself',
            name=model_name
        ))
    
    fig3.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
            )
        ),
        title=f'{selected_date} 날짜의 모델별 오차 지표 비교',
        height=500
    )
    
    st.plotly_chart(fig3, use_container_width=True)
    
    # 10. 상세 분석: 모델 선택 및 품종별/지역별 분석
    st.markdown("### 상세 분석")
    
    # 모델 선택
    selected_model = st.selectbox(
        "분석할 모델 선택",
        options=list(model_data.keys())
    )
    
    if selected_model:
        model_df = model_data[selected_model]
        
        # 탭으로 구분하여 다양한 분석 제공
        tab1, tab2, tab3 = st.tabs(["품종별 분석", "지역별 분석", "상세 데이터"])
        
        with tab1:
            # 품종별 오차율 분석
            breed_analysis = model_df.groupby('breed').agg({
                'price': 'mean',
                'predicted_price': 'mean',
                'error_rate': ['mean', 'std', 'count']
            })
            
            breed_analysis.columns = ['평균_실제가', '평균_예측가', '평균_오차율', '오차율_표준편차', '데이터_수']
            breed_analysis['평균_오차율'] = breed_analysis['평균_오차율'] * 100  # 백분율로 변환
            breed_analysis['오차율_표준편차'] = breed_analysis['오차율_표준편차'] * 100
            
            breed_analysis = breed_analysis.reset_index()
            
            # 품종별 오차율 막대 그래프
            fig_breed = px.bar(
                breed_analysis,
                x='breed',
                y='평균_오차율',
                error_y='오차율_표준편차',
                color='평균_오차율',
                color_continuous_scale=['green', 'yellow', 'red'],
                labels={'breed': '품종', '평균_오차율': '평균 오차율 (%)', '오차율_표준편차': '표준편차 (%)'},
                title=f'{selected_model} 모델의 품종별 평균 예측 오차율',
                hover_data=['데이터_수', '평균_실제가', '평균_예측가']
            )
            
            st.plotly_chart(fig_breed, use_container_width=True)
            
            # 품종별 데이터 표시
            st.dataframe(
                breed_analysis,
                column_config={
                    "breed": st.column_config.TextColumn("품종", width="medium"),
                    "평균_실제가": st.column_config.NumberColumn("평균 실제가", format="%d원"),
                    "평균_예측가": st.column_config.NumberColumn("평균 예측가", format="%d원"),
                    "평균_오차율": st.column_config.NumberColumn("평균 오차율", format="%.2f%%"),
                    "오차율_표준편차": st.column_config.NumberColumn("오차율 표준편차", format="%.2f%%"),
                    "데이터_수": st.column_config.NumberColumn("데이터 수", format="%d건"),
                },
                hide_index=True,
                use_container_width=True,
            )
        
        with tab2:
            # 지역별 오차율 분석
            district_analysis = model_df.groupby('district').agg({
                'price': 'mean',
                'predicted_price': 'mean',
                'error_rate': ['mean', 'std', 'count']
            })
            
            district_analysis.columns = ['평균_실제가', '평균_예측가', '평균_오차율', '오차율_표준편차', '데이터_수']
            district_analysis['평균_오차율'] = district_analysis['평균_오차율'] * 100
            district_analysis['오차율_표준편차'] = district_analysis['오차율_표준편차'] * 100
            
            district_analysis = district_analysis.reset_index()
            
            # 지역별 오차율 막대 그래프
            fig_district = px.bar(
                district_analysis,
                x='district',
                y='평균_오차율',
                error_y='오차율_표준편차',
                color='평균_오차율',
                color_continuous_scale=['green', 'yellow', 'red'],
                labels={'district': '지역', '평균_오차율': '평균 오차율 (%)', '오차율_표준편차': '표준편차 (%)'},
                title=f'{selected_model} 모델의 지역별 평균 예측 오차율',
                hover_data=['데이터_수', '평균_실제가', '평균_예측가']
            )
            
            st.plotly_chart(fig_district, use_container_width=True)
            
            # 지역별 데이터 표시
            st.dataframe(
                district_analysis,
                column_config={
                    "district": st.column_config.TextColumn("지역", width="medium"),
                    "평균_실제가": st.column_config.NumberColumn("평균 실제가", format="%d원"),
                    "평균_예측가": st.column_config.NumberColumn("평균 예측가", format="%d원"),
                    "평균_오차율": st.column_config.NumberColumn("평균 오차율", format="%.2f%%"),
                    "오차율_표준편차": st.column_config.NumberColumn("오차율 표준편차", format="%.2f%%"),
                    "데이터_수": st.column_config.NumberColumn("데이터 수", format="%d건"),
                },
                hide_index=True,
                use_container_width=True,
            )
            
            # 지도 시각화 (선택 사항)
            if st.checkbox("지역별 오차율 지도로 보기"):
                try:
                    from map_visualization import display_seoul_error_map
                    display_seoul_error_map(district_analysis)
                except Exception as e:
                    st.error(f"지도 시각화 중 오류 발생: {str(e)}")
        
        with tab3:
            # 상세 데이터 표시
            st.dataframe(
                model_df,
                column_config={
                    "claim_id": st.column_config.TextColumn("청구 ID", width="medium"),
                    "breed": st.column_config.TextColumn("품종", width="medium"),
                    "gender": st.column_config.TextColumn("성별", width="small"),
                    "neutralized": st.column_config.TextColumn("중성화", width="small"),
                    "district": st.column_config.TextColumn("지역", width="medium"),
                    "weight": st.column_config.NumberColumn("체중", format="%.1f kg"),
                    "age": st.column_config.NumberColumn("나이", format="%d세"),
                    "price": st.column_config.NumberColumn("실제가", format="%d원"),
                    "predicted_price": st.column_config.NumberColumn("예측가", format="%d원"),
                    "diff": st.column_config.NumberColumn("차이", format="%d원"),
                    "error_rate": st.column_config.ProgressColumn("오차율", format="%.2f%%", min_value=-0.5, max_value=0.5),
                },
                hide_index=True,
                use_container_width=True,
            )
            
            # CSV 다운로드 버튼
            csv = model_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="CSV 다운로드",
                data=csv,
                file_name=f"{selected_date}_{selected_model}_analysis.csv",
                mime="text/csv",
            )
    
    # 11. 모델 간 비교 분석 (선택적)
    if len(model_data) > 1:
        st.markdown("### 모델 간 비교 분석")
        
        # 비교할 모델 선택
        compare_models = st.multiselect(
            "비교할 모델 선택 (2개 이상)",
            options=list(model_data.keys()),
            default=list(model_data.keys())[:min(3, len(model_data))]
        )
        
        if len(compare_models) >= 2:
            # 품종별 모델 간 오차율 비교
            st.markdown("#### 품종별 모델 간 오차율 비교")
            
            breed_comparison = []
            
            for model_name in compare_models:
                model_df = model_data[model_name]
                breed_stats = model_df.groupby('breed')['error_rate'].mean() * 100
                
                for breed, error_rate in breed_stats.items():
                    breed_comparison.append({
                        '모델명': model_name,
                        '품종': breed,
                        '오차율': error_rate
                    })
            
            breed_comp_df = pd.DataFrame(breed_comparison)
            
            fig_breed_comp = px.bar(
                breed_comp_df,
                x='품종',
                y='오차율',
                color='모델명',
                barmode='group',
                labels={'품종': '품종', '오차율': '평균 오차율 (%)', '모델명': '모델'},
                title='품종별 모델 간 오차율 비교'
            )
            
            st.plotly_chart(fig_breed_comp, use_container_width=True)
            
            # 지역별 모델 간 오차율 비교
            st.markdown("#### 지역별 모델 간 오차율 비교")
            
            district_comparison = []
            
            for model_name in compare_models:
                model_df = model_data[model_name]
                district_stats = model_df.groupby('district')['error_rate'].mean() * 100
                
                for district, error_rate in district_stats.items():
                    district_comparison.append({
                        '모델명': model_name,
                        '지역': district,
                        '오차율': error_rate
                    })
            
            district_comp_df = pd.DataFrame(district_comparison)
            
            fig_district_comp = px.bar(
                district_comp_df,
                x='지역',
                y='오차율',
                color='모델명',
                barmode='group',
                labels={'지역': '지역', '오차율': '평균 오차율 (%)', '모델명': '모델'},
                title='지역별 모델 간 오차율 비교'
            )
            
            st.plotly_chart(fig_district_comp, use_container_width=True)


def build(
    variable_list: List[Tuple[str, str]],
    container: Container,
    data_stat_service: DataStatisticsService,
    prediction_service: PredictionStatisticsService,
    district_stat_service: DistrictStatisticsService,
):
    st.markdown("# 양육비 예측 대시보드")

    bi = build_bi_selectbox()

    # options = setup_options(
    #         container = container,
    #         variable_list = variable_list,
    #     )
    # setup_dataframe(
    #     container = container,
    #     options = options,
    # )

    if bi == BI.INSURANCE_CLAIM.value:
        tab1, tab2 = st.tabs(["데이터 분석", "지역별 분석"])
        options = setup_options(
            container = container,
            variable_list = variable_list,
        )
        setup_dataframe(
            container = container,
            options = options,
        )
        collect_statistics(
            container=container,
            data_stat_service=data_stat_service,
            options = options,
            tab=tab1,
        )
        visualize_map(
            container=container,
            district_stat_service=district_stat_service,
            tab=tab2
        )
    elif bi == BI.INSURANCE_CLAIM_PREDICTION_EVALUATION.value:
        options = setup_options(
            container = container,
        )
        setup_dataframe(
            container = container,
            options = options,
        )
        visualize_prediction_evaluation(
            container=container,
            prediction_service=prediction_service,
        )