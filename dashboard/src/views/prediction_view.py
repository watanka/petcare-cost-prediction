import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os
import re
from models.container import Container
from views.base_view import BaseView
from services.prediction_service import PredictionService
from utils.logger import get_logger

logger = get_logger(__name__)

class PredictionView(BaseView):
    """예측 분석 뷰"""
    
    def __init__(self):
        self.prediction_service = PredictionService()
        
    def render(self, container: Container) -> None:
        """예측 분석 뷰 렌더링"""
        if container.insurance_claim_df is None:
            self.show_warning("분석할 데이터가 없습니다. 날짜를 선택해주세요.")
            return
            
        # 예측 날짜 폴더 목록 가져오기
        prediction_dates = self._get_prediction_dates(container)
        
        if not prediction_dates:
            self.show_error("예측 데이터가 없습니다. data_storage/prediction/{yyyy-mm-dd} 형식의 폴더를 확인해주세요.")
            return
            
        # 예측 날짜 선택
        selected_date = st.selectbox(
            "예측 날짜 선택",
            options=prediction_dates,
            index=0,
            key="prediction_date_select"
        )
        
        # 선택된 날짜의 모델 목록 가져오기
        model_folders = self._get_model_folders(container, selected_date)
        
        if not model_folders:
            self.show_error(f"선택한 날짜({selected_date})에 모델 데이터가 없습니다.")
            return
            
        # 모델 데이터 로드
        model_data = self._load_model_data(container, selected_date, model_folders)
        
        if not model_data:
            self.show_error("로드할 수 있는 모델 데이터가 없습니다.")
            return
            
        # 모델별 요약 통계 계산 및 표시
        self._display_model_summary(model_data)
        
        # 모델별 성능 비교 시각화
        self._visualize_model_comparison(model_data)
        
        # 상세 분석
        self._display_detailed_analysis(model_data)
        
    def _get_prediction_dates(self, container: Container) -> list:
        """예측 날짜 폴더 목록 가져오기"""
        try:
            prediction_dates = [f for f in os.listdir(container.settings.insurance_claim_prediction_dir) 
                               if os.path.isdir(os.path.join(container.settings.insurance_claim_prediction_dir, f)) 
                               and re.match(r'\d{4}-\d{2}-\d{2}', f)]
            prediction_dates.sort()  # 날짜순 정렬
            return prediction_dates
        except Exception as e:
            logger.error(f"예측 날짜 폴더 목록을 가져오는 중 오류 발생: {e}")
            return []
            
    def _get_model_folders(self, container: Container, selected_date: str) -> list:
        """모델 폴더 목록 가져오기"""
        try:
            date_path = os.path.join(container.settings.insurance_claim_prediction_dir, selected_date)
            model_folders = [f for f in os.listdir(date_path) 
                            if os.path.isdir(os.path.join(date_path, f))]
            return model_folders
        except Exception as e:
            logger.error(f"모델 폴더 목록을 가져오는 중 오류 발생: {e}")
            return []
            
    def _load_model_data(self, container: Container, selected_date: str, model_folders: list) -> dict:
        """모델 데이터 로드"""
        model_data = {}
        
        for model_name in model_folders:
            file_path = os.path.join(container.settings.insurance_claim_prediction_dir, selected_date, model_name, 'prediction.csv')
            if os.path.exists(file_path):
                try:
                    prediction_df = pd.read_csv(file_path)
                    # 예측 데이터와 실제 데이터 병합 및 분석
                    comparison_df = self.prediction_service.summarize_prediction(
                        container=container,
                        insurance_claim_df=container.insurance_claim_df,
                        prediction_df=prediction_df
                    )
                    model_data[model_name] = comparison_df
                    logger.info(f"모델 '{model_name}' 데이터 로드 완료: {len(comparison_df)} 행")
                except Exception as e:
                    self.show_warning(f"모델 '{model_name}'의 데이터를 로드하는 중 오류 발생: {str(e)}")
                    
        return model_data
        
    def _display_model_summary(self, model_data: dict) -> None:
        """모델별 요약 통계 표시"""
        st.markdown("### 모델별 예측 결과 요약")
        
        model_summary = []
        
        for model_name, df in model_data.items():
            if df.empty:
                logger.warning(f"모델 '{model_name}'의 데이터프레임이 비어 있습니다.")
                continue
                
            metrics = self.prediction_service.calculate_model_metrics(df)
            
            model_summary.append({
                '모델명': model_name,
                '평균 실제가': f"{metrics['avg_price']:,.0f}원",
                '평균 예측가': f"{metrics['avg_pred']:,.0f}원",
                '평균 차이': f"{metrics['avg_diff']:,.0f}원",
                '평균 오차율': f"{metrics['avg_error']:.2f}%",
                'MSE': f"{metrics['mse']:.0f}",
                'RMSE': f"{metrics['rmse']:.0f}",
                'MAE': f"{metrics['mae']:.0f}",
                'raw_price': metrics['avg_price'],
                'raw_pred': metrics['avg_pred'],
                'raw_diff': metrics['avg_diff'],
                'raw_error': metrics['avg_error'],
                'raw_mse': metrics['mse'],
                'raw_rmse': metrics['rmse'],
                'raw_mae': metrics['mae']
            })
            
        if not model_summary:
            self.show_error("모델 요약 통계를 계산할 수 없습니다.")
            return
            
        summary_df = pd.DataFrame(model_summary)
        display_df = summary_df.drop(columns=[col for col in summary_df.columns if col.startswith('raw_')])
        
        self.show_dataframe(
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
            }
        )
        
        return summary_df
        
    def _visualize_model_comparison(self, model_data: dict) -> None:
        """모델별 성능 비교 시각화"""
        # 모델별 요약 통계 계산
        summary_df = self._display_model_summary(model_data)
        
        if summary_df is None or summary_df.empty:
            return
            
        # 모델별 실제가와 예측가 비교 (막대 그래프)
        st.markdown("### 모델별 실제가와 예측가 비교")
        
        fig1 = go.Figure()
        
        for i, row in summary_df.iterrows():
            model_name = row['모델명']
            fig1.add_trace(go.Bar(
                x=[f"{model_name} (실제)"],
                y=[row['raw_price']],
                name=f"{model_name} (실제)",
                marker_color='royalblue'
            ))
            fig1.add_trace(go.Bar(
                x=[f"{model_name} (예측)"],
                y=[row['raw_pred']],
                name=f"{model_name} (예측)",
                marker_color='lightcoral'
            ))
        
        fig1.update_layout(
            barmode='group',
            xaxis_title='모델 및 유형',
            yaxis_title='금액 (원)',
            title='모델별 실제가와 예측가 비교',
            legend_title="구분",
            height=500
        )
        
        st.plotly_chart(fig1, use_container_width=True)
        
        # 모델별 오차율 비교 (막대 그래프)
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
            title='모델별 예측 오차율 비교',
            height=400
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # 모델별 MSE, RMSE, MAE 비교 (레이더 차트)
        st.markdown("### 모델별 오차 지표 비교")
        
        # 레이더 차트용 데이터 준비
        metrics = ['MSE', 'RMSE', 'MAE']
        
        fig3 = go.Figure()
        
        for i, row in summary_df.iterrows():
            model_name = row['모델명']
            fig3.add_trace(go.Scatterpolar(
                r=[row['raw_mse'], row['raw_rmse'], row['raw_mae']],
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
            title='모델별 오차 지표 비교',
            height=500
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        
    def _display_detailed_analysis(self, model_data: dict) -> None:
        """상세 분석 표시"""
        st.markdown("### 상세 분석")
        
        # 모델 선택
        selected_model = st.selectbox(
            "분석할 모델 선택",
            options=list(model_data.keys()),
            key="model_select"
        )
        
        if selected_model:
            model_df = model_data[selected_model]
            
            if model_df.empty:
                self.show_warning(f"선택한 모델 '{selected_model}'의 데이터가 없습니다.")
                return
                
            # 탭으로 구분하여 다양한 분석 제공
            tab1, tab2, tab3 = st.tabs(["품종별 분석", "지역별 분석", "상세 데이터"])
            
            with tab1:
                # 품종별 오차율 분석
                try:
                    breed_analysis = self.prediction_service.analyze_by_category(model_df, 'breed')
                    
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
                    self.show_dataframe(
                        breed_analysis,
                        column_config={
                            "breed": st.column_config.TextColumn("품종", width="medium"),
                            "평균_실제가": st.column_config.NumberColumn("평균 실제가", format="%d원"),
                            "평균_예측가": st.column_config.NumberColumn("평균 예측가", format="%d원"),
                            "평균_오차율": st.column_config.NumberColumn("평균 오차율", format="%.2f%%"),
                            "오차율_표준편차": st.column_config.NumberColumn("오차율 표준편차", format="%.2f%%"),
                            "데이터_수": st.column_config.NumberColumn("데이터 수", format="%d건"),
                        }
                    )
                except Exception as e:
                    self.show_error(f"품종별 분석 중 오류 발생: {str(e)}")
            
            with tab2:
                # 지역별 오차율 분석
                try:
                    district_analysis = self.prediction_service.analyze_by_category(model_df, 'district')
                    
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
                    self.show_dataframe(
                        district_analysis,
                        column_config={
                            "district": st.column_config.TextColumn("지역", width="medium"),
                                                        "평균_실제가": st.column_config.NumberColumn("평균 실제가", format="%d원"),
                            "평균_예측가": st.column_config.NumberColumn("평균 예측가", format="%d원"),
                            "평균_오차율": st.column_config.NumberColumn("평균 오차율", format="%.2f%%"),
                            "오차율_표준편차": st.column_config.NumberColumn("오차율 표준편차", format="%.2f%%"),
                            "데이터_수": st.column_config.NumberColumn("데이터 수", format="%d건"),
                        }
                    )
                except Exception as e:
                    self.show_error(f"지역별 분석 중 오류 발생: {str(e)}")
            
            with tab3:
                # 상세 데이터 표시
                self.show_dataframe(
                    model_df,
                    column_config={
                        "claim_id": st.column_config.TextColumn("청구 ID", width="medium"),
                        "pet_id": st.column_config.TextColumn("반려동물 ID", width="medium"),
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
                    }
                )
                
                # CSV 다운로드 버튼
                csv = model_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="CSV 다운로드",
                    data=csv,
                    file_name=f"{selected_model}_analysis.csv",
                    mime="text/csv",
                )
        
        # 모델 간 비교 분석 (선택적)
        if len(model_data) > 1:
            st.markdown("### 모델 간 비교 분석")
            
            # 비교할 모델 선택
            compare_models = st.multiselect(
                "비교할 모델 선택 (2개 이상)",
                options=list(model_data.keys()),
                default=list(model_data.keys())[:min(3, len(model_data))],
                key="compare_models_select"
            )
            
            if len(compare_models) >= 2:
                try:
                    # 품종별 모델 간 오차율 비교
                    st.markdown("#### 품종별 모델 간 오차율 비교")
                    
                    breed_comparison = []
                    
                    for model_name in compare_models:
                        model_df = model_data[model_name]
                        if not model_df.empty:
                            breed_stats = model_df.groupby('breed')['error_rate'].mean() * 100
                            
                            for breed, error_rate in breed_stats.items():
                                breed_comparison.append({
                                    '모델명': model_name,
                                    '품종': breed,
                                    '오차율': error_rate
                                })
                    
                    if breed_comparison:
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
                    else:
                        self.show_warning("품종별 비교 데이터를 생성할 수 없습니다.")
                    
                    # 지역별 모델 간 오차율 비교
                    st.markdown("#### 지역별 모델 간 오차율 비교")
                    
                    district_comparison = []
                    
                    for model_name in compare_models:
                        model_df = model_data[model_name]
                        if not model_df.empty:
                            district_stats = model_df.groupby('district')['error_rate'].mean() * 100
                            
                            for district, error_rate in district_stats.items():
                                district_comparison.append({
                                    '모델명': model_name,
                                    '지역': district,
                                    '오차율': error_rate
                                })
                    
                    if district_comparison:
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
                    else:
                        self.show_warning("지역별 비교 데이터를 생성할 수 없습니다.")
                except Exception as e:
                    self.show_error(f"모델 간 비교 분석 중 오류 발생: {str(e)}")