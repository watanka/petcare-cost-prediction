import streamlit as st
import pandas as pd
from models.container import Container
from models.enums import VariableType, ChartType
from views.base_view import BaseView
from services.data_service import DataService
from widgets.widget_factory import WidgetFactory
from widgets.chart_widgets import ChartFactory
from utils.logger import get_logger

logger = get_logger(__name__)

class DataAnalysisView(BaseView):
    """데이터 분석 뷰"""
    
    def __init__(self):
        self.data_service = DataService()
        
    def render(self, container: Container) -> None:
        """데이터 분석 뷰 렌더링"""
        if container.insurance_claim_df is None:
            self.show_warning("분석할 데이터가 없습니다. 날짜를 선택해주세요.")
            return
            
        # 필터 옵션 설정
        variable_list = [
            ('gender', VariableType.CATEGORY.value),
            ('breed', VariableType.CATEGORY.value),
            ('neutralized', VariableType.CATEGORY.value),
            ('age', VariableType.NUMERIC.value),
            ('district', VariableType.CATEGORY.value),
        ]
        
        # 필터 적용
        options = []
        for variable_name, variable_type in variable_list:
            selected = WidgetFactory.create_filter_widget(
                container=container,
                variable_name=variable_name,
                variable_type=variable_type
            )
            options.append((variable_name, selected))
            
        # 필터링된 데이터 조회
        filtered_df = self.data_service.retrieve(
            container=container,
            variable_filter=options
        )
        
        if filtered_df is None or filtered_df.empty:
            self.show_warning("선택한 조건에 맞는 데이터가 없습니다.")
            return
            
        # 데이터 표시
        st.markdown("### 필터링된 데이터")
        self.show_dataframe(filtered_df)
        
        # 요약 통계 표시
        st.markdown("### 요약 통계")
        summary = self.data_service.get_summary_statistics(filtered_df)
        self.show_dataframe(summary)
        
        # 시각화
        st.markdown("### 데이터 시각화")
        
        # 시각화 옵션
        col1, col2 = st.columns(2)
        
        with col1:
            chart_type = st.selectbox(
                "차트 유형",
                options=[
                    "선 차트", 
                    "막대 차트", 
                    "산점도", 
                    "파이 차트"
                ],
                key="chart_type_select"
            )
            
        with col2:
            if chart_type in ["선 차트", "막대 차트", "산점도"]:
                x_column = st.selectbox(
                    "X축",
                    options=filtered_df.columns.tolist(),
                    index=filtered_df.columns.get_loc("issued_at") if "issued_at" in filtered_df.columns else 0,
                    key="x_column_select"
                )
                
                y_column = st.selectbox(
                    "Y축",
                    options=filtered_df.select_dtypes(include=['int64', 'float64']).columns.tolist(),
                    index=filtered_df.select_dtypes(include=['int64', 'float64']).columns.get_loc("price") if "price" in filtered_df.select_dtypes(include=['int64', 'float64']).columns else 0,
                    key="y_column_select"
                )
                
                color_column = st.selectbox(
                    "색상 구분",
                    options=["없음"] + filtered_df.select_dtypes(include=['object', 'category']).columns.tolist(),
                    key="color_column_select"
                )
                
                color = None if color_column == "없음" else color_column
                
            elif chart_type == "파이 차트":
                names_column = st.selectbox(
                    "범주",
                    options=filtered_df.select_dtypes(include=['object', 'category']).columns.tolist(),
                    key="names_column_select"
                )
                
                values_column = st.selectbox(
                    "값",
                    options=filtered_df.select_dtypes(include=['int64', 'float64']).columns.tolist(),
                    index=filtered_df.select_dtypes(include=['int64', 'float64']).columns.get_loc("price") if "price" in filtered_df.select_dtypes(include=['int64', 'float64']).columns else 0,
                    key="values_column_select"
                )
        
        # 차트 생성
        if chart_type == "선 차트":
            ChartFactory.create_chart(
                ChartType.LINE,
                filtered_df,
                x=x_column,
                y=y_column,
                color=color,
                title=f"{x_column}에 따른 {y_column} 변화"
            )
        elif chart_type == "막대 차트":
            ChartFactory.create_chart(
                ChartType.BAR,
                filtered_df,
                x=x_column,
                y=y_column,
                color=color,
                title=f"{x_column}별 {y_column} 비교"
            )
        elif chart_type == "산점도":
            ChartFactory.create_chart(
                ChartType.SCATTER,
                filtered_df,
                x=x_column,
                y=y_column,
                color=color,
                title=f"{x_column}와 {y_column}의 관계"
            )
        elif chart_type == "파이 차트":
            # 파이 차트를 위한 데이터 집계
            pie_data = filtered_df.groupby(names_column)[values_column].sum().reset_index()
            
            ChartFactory.create_chart(
                ChartType.PIE,
                pie_data,
                names=names_column,
                values=values_column,
                title=f"{names_column}별 {values_column} 비율"
            )
            
        # 시계열 분석 (issued_at 컬럼이 있는 경우)
        if "issued_at" in filtered_df.columns and "price" in filtered_df.columns:
            st.markdown("### 시계열 분석")
            
            # 날짜별 평균 가격 계산
            time_series_df = filtered_df.groupby("issued_at")["price"].mean().reset_index()
            
            # 선 차트로 시계열 데이터 표시
            ChartFactory.create_chart(
                ChartType.LINE,
                time_series_df,
                x="issued_at",
                y="price",
                title="날짜별 평균 가격 추이"
            )
            
            # 반려동물별 시계열 분석 (pet_id 컬럼이 있는 경우)
            if "pet_id" in filtered_df.columns:
                st.markdown("### 반려동물별 가격 추이")
                
                # 상위 5개 반려동물 선택
                top_pets = filtered_df.groupby("pet_id")["price"].count().nlargest(5).index.tolist()
                
                # 사용자가 선택할 수 있는 반려동물 목록
                selected_pets = st.multiselect(
                    "반려동물 선택",
                    options=filtered_df["pet_id"].unique().tolist(),
                    default=top_pets[:3] if len(top_pets) >= 3 else top_pets,
                    key="pet_select"
                )
                
                if selected_pets:
                    # 선택된 반려동물의 데이터만 필터링
                    pet_df = filtered_df[filtered_df["pet_id"].isin(selected_pets)]
                    
                    # 반려동물별 시계열 차트
                    ChartFactory.create_chart(
                        ChartType.LINE,
                        pet_df,
                        x="issued_at",
                        y="price",
                        color="pet_id",
                        title="반려동물별 가격 추이"
                    )