from typing import List, Dict, Optional
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from models.enums import ChartType

class ChartFactory:
    """차트 팩토리 클래스"""
    
    @staticmethod
    def create_chart(chart_type: ChartType, data: pd.DataFrame, **kwargs) -> None:
        """차트 생성 및 표시"""
        if chart_type == ChartType.BAR:
            fig = ChartFactory._create_bar_chart(data, **kwargs)
        elif chart_type == ChartType.LINE:
            fig = ChartFactory._create_line_chart(data, **kwargs)
        elif chart_type == ChartType.SCATTER:
            fig = ChartFactory._create_scatter_chart(data, **kwargs)
        elif chart_type == ChartType.PIE:
            fig = ChartFactory._create_pie_chart(data, **kwargs)
        else:
            raise ValueError(f"지원하지 않는 차트 유형: {chart_type}")
            
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def _create_bar_chart(data: pd.DataFrame, x: str, y: str, color: Optional[str] = None, 
                         title: str = "", **kwargs) -> go.Figure:
        """막대 차트 생성"""
        fig = px.bar(
            data,
            x=x,
            y=y,
            color=color,
            title=title,
            **kwargs
        )
        return fig
    
    @staticmethod
    def _create_line_chart(data: pd.DataFrame, x: str, y: str, color: Optional[str] = None, 
                          title: str = "", **kwargs) -> go.Figure:
        """선 차트 생성"""
        fig = px.line(
            data,
            x=x,
            y=y,
            color=color,
            title=title,
            **kwargs
        )
        return fig
    
    @staticmethod
    def _create_scatter_chart(data: pd.DataFrame, x: str, y: str, color: Optional[str] = None, 
                             size: Optional[str] = None, title: str = "", **kwargs) -> go.Figure:
        """산점도 생성"""
        fig = px.scatter(
            data,
            x=x,
            y=y,
            color=color,
            size=size,
            title=title,
            **kwargs
        )
        return fig
    
    @staticmethod
    def _create_pie_chart(data: pd.DataFrame, names: str, values: str, 
                         title: str = "", **kwargs) -> go.Figure:
        """파이 차트 생성"""
        fig = px.pie(
            data,
            names=names,
            values=values,
            title=title,
            **kwargs
        )
        return fig