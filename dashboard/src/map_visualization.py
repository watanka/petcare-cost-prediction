import geopandas as gpd
import streamlit as st
import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib as mpl
import pandas as pd
import plotly.express as px

# 한글 폰트 설정
def set_korean_font():
    # 폰트 파일 경로
    font_path = 'data_storage/font/NanumGothic-Regular.ttf'
    
    # 폰트 파일이 존재하는지 확인
    if os.path.exists(font_path):
        # 폰트 등록
        font_prop = fm.FontProperties(fname=font_path)
        font_name = font_prop.get_name()
        
        # 폰트 설정
        plt.rcParams['font.family'] = font_name
        
        # 폰트 등록 (다른 방식)
        fm.fontManager.addfont(font_path)
        mpl.rc('font', family=font_name)
        
        print(f"한글 폰트 '{font_name}' 설정 완료")
        return font_name
    else:
        print(f"폰트 파일을 찾을 수 없습니다: {font_path}")
        return None



def load_seoul_map():
    """
    서울시 행정구역 shapefile을 로드하는 함수
    """
    set_korean_font()
    # shapefile 경로
    shapefile_path = 'data_storage/geodata/LARD_ADM_SECT_SGG_11_202502.shp'
    
    # GeoPandas로 shapefile 로드
    seoul_map = gpd.read_file(shapefile_path, encoding='cp949')
    
    # 필요한 컬럼만 선택 (구 이름과 geometry)
    seoul_map = seoul_map[['SGG_NM', 'geometry']]
    
    # 컬럼명 변경
    seoul_map = seoul_map.rename(columns={'SGG_NM': 'district'})
    
    # 한글 폰트가 없는 경우 영문으로 변환
    seoul_map['district'] = seoul_map['district']
    
    return seoul_map

def visualize_seoul_district_stats(district_stats, value_column, title, cmap='Blues', save_path=None):
    """
    서울시 구별 통계를 지도로 시각화하는 함수
    
    Parameters:
    -----------
    district_stats : pandas.DataFrame
        구별 통계 데이터 (district 컬럼 필수)
    value_column : str
        시각화할 값이 있는 컬럼명
    title : str
        그래프 제목
    cmap : str
        컬러맵 이름
    save_path : str
        저장할 파일 경로 (None이면 저장하지 않음)
    """
    # 서울시 지도 로드
    seoul_map = load_seoul_map()    
    
    # 데이터 병합
    merged_data = seoul_map.merge(district_stats, on='district', how='left')
    
    # 시각화
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    # 컬러맵 설정
    if 'error' in value_column.lower():
        # 오차율은 발산형 컬러맵 사용 (음수/양수 구분)
        cmap = 'RdBu_r'
        vmin = -merged_data[value_column].abs().max()
        vmax = merged_data[value_column].abs().max()
    else:
        # 일반 값은 순차형 컬러맵 사용
        vmin = merged_data[value_column].min()
        vmax = merged_data[value_column].max()
    
    # 지도 그리기
    merged_data.plot(
        column=value_column,
        ax=ax,
        legend=True,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        edgecolor='black',
        linewidth=0.5,
        missing_kwds={'color': 'lightgrey'}
    )
    
    # 구 이름 표시
    for idx, row in merged_data.iterrows():
        # 구 중심점 좌표 계산
        centroid = row['geometry'].centroid
        # 구 이름 표시
        ax.text(
            centroid.x, 
            centroid.y, 
            row['district'], 
            fontsize=8,
            ha='center', 
            va='center'
        )
    
    # 제목 및 레이아웃 설정
    ax.set_title(title, fontsize=15)
    ax.set_axis_off()
    plt.tight_layout()
    
    # 파일 저장
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"지도가 {save_path}에 저장되었습니다.")
    
    return fig

def display_seoul_map_streamlit(district_stats: pd.DataFrame):
    """
    Streamlit에서 서울시 구별 통계를 지도로 시각화
    """
    st.subheader("서울시 구별 보험금 청구 현황")
    
    # 표시할 데이터 선택
    col1, col2 = st.columns([1, 3])
    
    value_map = {
        "평균 청구금액": "avg_claim_price",
        # "평균 예측금액": "avg_predicted_price",
        "청구 건수": "claim_count",
        "오차율": "error_rate"
    }

    with col1:
        display_option = st.selectbox(
            "표시할 데이터",
            ["평균 청구금액", "평균 예측금액", "청구 건수", "오차율"],
            index=0
        )
        
        # 컬러맵 선택
        colormap = st.selectbox(
            "컬러맵",
            ["Blues", "Reds", "Greens", "Purples", "Oranges", "RdBu_r", "viridis", "plasma"],
            index=0
        )
        
        # 이미지 저장 버튼
        save_image = st.button("이미지 저장")

        title = f"서울시 구별 {display_option}"
    
    # 시각화
    with col2:
        fig = visualize_seoul_district_stats(
            district_stats,
            value_map[display_option],
            title,
            cmap=colormap,
            save_path="img/district_analysis.png" if save_image else None
        )
        st.pyplot(fig)
    
    # 데이터 테이블 표시
    st.subheader("구별 통계 데이터")
    st.dataframe(
        district_stats[[
            'district', 
            'avg_claim_price', 
            # 'avg_predicted_price', 
            'claim_count', 
            # 'error_rate'
        ]].sort_values('district'),
        height=300
    )
    
    # 통계 요약
    st.subheader("통계 요약")
    col1, col2 = st.columns(2)
    
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
    

