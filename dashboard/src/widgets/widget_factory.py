from typing import List, Optional, Tuple, Any
import streamlit as st
from models.container import Container
from models.enums import VariableType

class WidgetFactory:
    """위젯 팩토리 클래스"""
    
    @staticmethod
    def create_filter_widget(
        container: Container,
        variable_name: str,
        variable_type: str,
        options: List[Any] = None
    ) -> Any:
        """필터 위젯 생성"""
        if variable_type == VariableType.NUMERIC.value:
            return WidgetFactory._create_numeric_filter(container, variable_name, options)
        elif variable_type == VariableType.CATEGORY.value:
            return WidgetFactory._create_category_filter(container, variable_name, options)
        else:
            raise ValueError(f"지원하지 않는 변수 유형: {variable_type}")
    
    @staticmethod
    def _create_numeric_filter(container: Container, variable_name: str, options: List[float] = None) -> Tuple[float, float]:
        """숫자형 필터 위젯 생성"""
        if options is None:
            if container.insurance_claim_df is None:
                return (0, 0)
            min_val = container.insurance_claim_df[variable_name].min()
            max_val = container.insurance_claim_df[variable_name].max()
        else:
            min_val = options[0]
            max_val = options[-1]
            
        return st.sidebar.slider(
            label=variable_name,
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val),
            key=f"slider_{variable_name}"
        )
    
    @staticmethod
    def _create_category_filter(container: Container, variable_name: str, options: List[str] = None) -> str:
        """범주형 필터 위젯 생성"""
        if options is None:
            if container.insurance_claim_df is None:
                return "ALL"
            options = container.insurance_claim_df[variable_name].unique().tolist()
            
        options.append("ALL")
        return st.sidebar.selectbox(
            label=variable_name,
            options=options,
            key=f"selectbox_{variable_name}"
        )