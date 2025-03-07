import streamlit as st
from controllers.dashboard_controller import DashboardController
from views.dashboard_view import DashboardView
from utils.logger import get_logger

logger = get_logger(__name__)

def main():
    """애플리케이션 메인 함수"""
    # 페이지 설정
    st.set_page_config(
        page_title="양육비 예측 대시보드",
        page_icon="🐶",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 컨트롤러 및 뷰 초기화
    controller = DashboardController()
    view = DashboardView()
    
    # 컨테이너 초기화 및 데이터 로드
    container = controller.initialize_container()
    
    # 날짜 선택 위젯 (사이드바)
    if container.available_dates:
        selected_date = st.sidebar.selectbox(
            "데이터 날짜 선택",
            options=["선택하세요"] + container.available_dates,
            index=0,
            key="date_select"
        )
        
        # 날짜가 선택된 경우 데이터 로드
        if selected_date != "선택하세요":
            if controller.load_insurance_claim_data(container, selected_date):
                # 예측 모델 데이터 로드 시도
                controller.load_prediction_models(container, selected_date)
                
                # 대시보드 렌더링
                view.render(container)
            else:
                st.error(f"{selected_date} 날짜의 데이터를 로드할 수 없습니다.")
        else:
            st.info("데이터를 로드하려면 날짜를 선택하세요.")
    else:
        st.error("사용 가능한 데이터 날짜가 없습니다.")

if __name__ == "__main__":
    main()
