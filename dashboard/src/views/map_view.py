import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Patch
import plotly.express as px
from models.container import Container
from views.base_view import BaseView
from services.district_service import DistrictService
from utils.logger import get_logger

logger = get_logger(__name__)

class MapView(BaseView):
    """지도 시각화 뷰"""
    
    def __init__(self):
        self.district_service = DistrictService()
        
    def render(self, container: Container) -> None:
        """지도 시각화 뷰 렌더링"""
        if container.insurance_claim_df is None:
            self.show_warning("분석할 데이터가 없습니다. 날짜를 선택해주세요.")
            return
            
        # 구별 통계 데이터 조회
        district_stats = self.district_service.retrieve(
            container=container,
            filtered_df=container.insurance_claim_df,
            prediction_df=container.prediction_df
        )
        
        if district_stats is None or district_stats.empty:
            self.show_warning("지도 시각화를 위한 데이터가 없습니다.")
            return
            
        # 서울시 지도 데이터 로드
        seoul_map = self.district_service.load_seoul_map(container)
        
        if seoul_map is None:
            self.show_error("서울시 지도 데이터를 로드할 수 없습니다.")
            return
            
        # 지도 시각화
        st.markdown("### 서울시 구별 보험 청구금액 분포")
        
        # 시각화 유형 선택
        viz_type = st.radio(
            "시각화 유형",
            options=["Matplotlib", "Plotly"],
            horizontal=True,
            key="map_viz_type"
        )
        
        if viz_type == "Matplotlib":
            self._render_matplotlib_map(seoul_map, district_stats)
        else:
            self._render_plotly_map(seoul_map, district_stats)
            
        # 구별 통계 데이터 표시
        st.markdown("### 구별 통계 데이터")
        self.show_dataframe(
            district_stats,
            column_config={
                "district": st.column_config.TextColumn("지역", width="medium"),
                "avg_claim_price": st.column_config.NumberColumn("평균 청구금액", format="%d원"),
                "claim_count": st.column_config.NumberColumn("청구 건수", format="%d건"),
                "avg_predicted_price": st.column_config.NumberColumn("평균 예측금액", format="%d원"),
                "price_diff": st.column_config.NumberColumn("차이", format="%d원"),
                "error_rate": st.column_config.NumberColumn("오차율", format="%.2f%%"),
            }
        )
        
    def _render_matplotlib_map(self, seoul_map: gpd.GeoDataFrame, district_stats: pd.DataFrame) -> None:
        """Matplotlib을 사용한 지도 시각화"""
        # 지도 데이터와 통계 데이터 병합
        merged_map = seoul_map.merge(district_stats, left_on='SIG_KOR_NM', right_on='district')
        
        # 시각화할 컬럼 선택
        column_to_plot = st.selectbox(
            "시각화할 데이터",
            options=["avg_claim_price", "claim_count", "avg_predicted_price", "price_diff", "error_rate"],
            format_func=lambda x: {
                "avg_claim_price": "평균 청구금액",
                "claim_count": "청구 건수",
                "avg_predicted_price": "평균 예측금액",
                "price_diff": "차이",
                "error_rate": "오차율"
            }.get(x, x),
            key="map_column_select"
        )
        
        # 컬러맵 선택
        colormap = st.selectbox(
            "컬러맵",
            options=["viridis", "plasma", "inferno", "magma", "cividis", "Blues", "Greens", "Reds", "YlOrRd"],
            key="map_colormap_select"
        )
        
        # 그림 크기 설정
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        
        # 지도 시각화
        merged_map.plot(
            column=column_to_plot,
            cmap=colormap,
            linewidth=0.8,
            ax=ax,
            edgecolor='0.8',
            legend=True
        )
        
        # 제목 설정
        title_map = {
            "avg_claim_price": "평균 청구금액",
            "claim_count": "청구 건수",
            "avg_predicted_price": "평균 예측금액",
            "price_diff": "차이",
            "error_rate": "오차율"
        }
        ax.set_title(f'서울시 구별 {title_map.get(column_to_plot, column_to_plot)}', fontsize=15)
        
        # 축 제거
        ax.set_axis_off()
        
        # 최대/최소값 구 표시
        if not merged_map.empty:
            max_district = merged_map.loc[merged_map[column_to_plot].idxmax(), 'district']
            min_district = merged_map.loc[merged_map[column_to_plot].idxmin(), 'district']
            
            max_value = merged_map[column_to_plot].max()
            min_value = merged_map[column_to_plot].min()
            
            format_func = lambda x: f"{x:,.0f}원" if column_to_plot in ["avg_claim_price", "avg_predicted_price", "price_diff"] else \
                          f"{x:,.0f}건" if column_to_plot == "claim_count" else \
                          f"{x:.2f}%" if column_to_plot == "error_rate" else \
                          f"{x}"
            
            legend_elements = [
                Patch(facecolor='red', edgecolor='black', label=f'최대: {max_district} ({format_func(max_value)})'),
                Patch(facecolor='blue', edgecolor='black', label=f'최소: {min_district} ({format_func(min_value)})')
            ]
            
            ax.legend(handles=legend_elements, loc='lower right')
        
        # Streamlit에 표시
        st.pyplot(fig)
        
    def _render_plotly_map(self, seoul_map: gpd.GeoDataFrame, district_stats: pd.DataFrame) -> None:
        """Plotly를 사용한 지도 시각화"""
        # 지도 데이터와 통계 데이터 병합
        merged_map = seoul_map.merge(district_stats, left_on='SIG_KOR_NM', right_on='district')
        
        # 시각화할 컬럼 선택
        column_to_plot = st.selectbox(
            "시각화할 데이터",
            options=["avg_claim_price", "claim_count", "avg_predicted_price", "price_diff", "error_rate"],
            format_func=lambda x: {
                "avg_claim_price": "평균 청구금액",
                "claim_count": "청구 건수",
                "avg_predicted_price": "평균 예측금액",
                "price_diff": "차이",
                "error_rate": "오차율"
            }.get(x, x),
            key="plotly_map_column_select"
        )
        
        # 컬러맵 선택
        colormap = st.selectbox(
            "컬러맵",
            options=["viridis", "plasma", "inferno", "magma", "cividis", "Blues", "Greens", "Reds", "YlOrRd"],
            key="plotly_map_colormap_select"
        )
        
        # 제목 설정
        title_map = {
            "avg_claim_price": "평균 청구금액",
            "claim_count": "청구 건수",
            "avg_predicted_price": "평균 예측금액",
            "price_diff": "차이",
            "error_rate": "오차율"
        }
        
        # 단위 설정
        unit_map = {
            "avg_claim_price": "원",
            "claim_count": "건",
            "avg_predicted_price": "원",
            "price_diff": "원",
            "error_rate": "%"
        }
        
        # 호버 데이터 형식 설정
        hover_data = {
            "district": True,
            column_to_plot: True
        }
        
        # 값 형식 설정
        if column_to_plot == "error_rate":
            merged_map[column_to_plot] = merged_map[column_to_plot].round(2)
        
        # Plotly 지도 생성
        fig = px.choropleth_mapbox(
            merged_map,
            geojson=merged_map.geometry,
            locations=merged_map.index,
            color=column_to_plot,
            color_continuous_scale=colormap,
            mapbox_style="carto-positron",
            zoom=9,
            center={"lat": 37.5665, "lon": 126.9780},
            opacity=0.7,
            labels={column_to_plot: f"{title_map.get(column_to_plot, column_to_plot)} ({unit_map.get(column_to_plot, '')})"},
            hover_name="district",
            hover_data=hover_data,
            title=f'서울시 구별 {title_map.get(column_to_plot, column_to_plot)}'
        )
        
        fig.update_layout(
            margin={"r": 0, "t": 30, "l": 0, "b": 0},
            height=600
        )
        
        # Streamlit에 표시
        st.plotly_chart(fig, use_container_width=True)