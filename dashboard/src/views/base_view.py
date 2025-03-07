from abc import ABC, abstractmethod
import streamlit as st
from models.container import Container

class BaseView(ABC):
    """기본 뷰 추상 클래스"""
    
    @abstractmethod
    def render(self, container: Container) -> None:
        """뷰 렌더링"""
        pass
        
    def create_tabs(self, tab_names: list) -> list:
        """탭 생성"""
        return st.tabs(tab_names)
        
    def show_error(self, message: str) -> None:
        """오류 메시지 표시"""
        st.error(message)
        
    def show_warning(self, message: str) -> None:
        """경고 메시지 표시"""
        st.warning(message)
        
    def show_info(self, message: str) -> None:
        """정보 메시지 표시"""
        st.info(message)
        
    def show_success(self, message: str) -> None:
        """성공 메시지 표시"""
        st.success(message)
        
    def show_dataframe(self, df, height=300, use_container_width=True, hide_index=False, **kwargs):
        """데이터프레임 표시"""
        return st.dataframe(
            df,
            height=height,
            use_container_width=use_container_width,
            hide_index=hide_index,
            **kwargs
        )