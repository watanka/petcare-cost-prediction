import streamlit as st
from models.container import Container
from models.enums import BI
from views.base_view import BaseView
from views.data_analysis_view import DataAnalysisView
from views.map_view import MapView
from views.prediction_view import PredictionView

class DashboardView(BaseView):
    """대시보드 메인 뷰"""
    
    def __init__(self):
        self.data_analysis_view = DataAnalysisView()
        self.map_view = MapView()
        self.prediction_view = PredictionView()
        
    def render(self, container: Container) -> None:
        """대시보드 렌더링"""
        st.markdown("# 양육비 예측 대시보드")
        
        # BI 선택
        bi_options = [None, BI.INSURANCE_CLAIM.value, BI.INSURANCE_CLAIM_PREDICTION_EVALUATION.value]
        selected_bi = st.sidebar.selectbox(
            label="BI",
            options=bi_options,
            key="bi_select"
        )
        
        if selected_bi == BI.INSURANCE_CLAIM.value:
            self._render_insurance_claim_view(container)
        elif selected_bi == BI.INSURANCE_CLAIM_PREDICTION_EVALUATION.value:
            self._render_prediction_evaluation_view(container)
        else:
            st.info("분석 유형을 선택해주세요.")
            
    def _render_insurance_claim_view(self, container: Container) -> None:
        """보험 청구 데이터 분석 뷰 렌더링"""
        tabs = self.create_tabs(["데이터 분석", "지역별 분석"])
        
        with tabs[0]:
            self.data_analysis_view.render(container)
            
        with tabs[1]:
            self.map_view.render(container)
            
    def _render_prediction_evaluation_view(self, container: Container) -> None:
        """예측 평가 뷰 렌더링"""
        self.prediction_view.render(container)