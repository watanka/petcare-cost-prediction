from typing import List, Tuple, Any
import streamlit as st
from models.container import Container
from models.enums import VariableType
from widgets.widget_factory import WidgetFactory

class FilterWidgets:
    """필터 위젯 관리 클래스"""
    
    @staticmethod
    def create_filters(container: Container, variable_list: List[Tuple[str, str]]) -> List[Tuple[str, Any]]:
        """필터 위젯 생성"""
        options = []
        
        for variable_name, variable_type in variable_list:
            selected = WidgetFactory.create_filter_widget(
                container=container,
                variable_name=variable_name,
                variable_type=variable_type
            )
            options.append((variable_name, selected))
            
        return options
    
    @staticmethod
    def create_date_filter(container: Container) -> str:
        """날짜 필터 위젯 생성"""
        if not container.available_dates:
            return None
            
        return st.sidebar.selectbox(
            "데이터 날짜 선택",
            options=["선택하세요"] + container.available_dates,
            index=0,
            key="date_filter"
        )
    
    @staticmethod
    def create_model_filter(model_list: List[str]) -> str:
        """모델 필터 위젯 생성"""
        if not model_list:
            return None
            
        return st.selectbox(
            "모델 선택",
            options=model_list,
            key="model_filter"
        )
    
    @staticmethod
    def create_multi_model_filter(model_list: List[str], default_count: int = 3) -> List[str]:
        """다중 모델 필터 위젯 생성"""
        if not model_list:
            return []
            
        default_models = model_list[:min(default_count, len(model_list))]
        
        return st.multiselect(
            "모델 선택 (다중)",
            options=model_list,
            default=default_models,
            key="multi_model_filter"
        )