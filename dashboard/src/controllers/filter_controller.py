from typing import List, Tuple, Dict, Any
from models.container import Container
from models.enums import VariableType
from utils.logger import get_logger

logger = get_logger(__name__)

class FilterController:
    """필터 컨트롤러"""
    
    def __init__(self, container: Container):
        self.container = container
        
    def get_filter_options(self, variable_list: List[Tuple[str, str]]) -> List[Tuple[str, Any]]:
        """필터 옵션 목록 조회"""
        options = []
        
        for variable_name, variable_type in variable_list:
            if variable_type == VariableType.NUMERIC.value:
                options.append(self._get_numeric_filter_option(variable_name))
            elif variable_type == VariableType.CATEGORY.value:
                options.append(self._get_category_filter_option(variable_name))
            else:
                logger.warning(f"지원하지 않는 변수 유형: {variable_type}")
                
        return options
        
    def _get_numeric_filter_option(self, variable_name: str) -> Tuple[str, Tuple[float, float]]:
        """숫자형 필터 옵션 조회"""
        if self.container.insurance_claim_df is None:
            return (variable_name, (0, 0))
            
        min_val = self.container.insurance_claim_df[variable_name].min()
        max_val = self.container.insurance_claim_df[variable_name].max()
        
        return (variable_name, (min_val, max_val))
        
    def _get_category_filter_option(self, variable_name: str) -> Tuple[str, List[str]]:
        """범주형 필터 옵션 조회"""
        if self.container.insurance_claim_df is None:
            return (variable_name, ["ALL"])
            
        values = self.container.insurance_claim_df[variable_name].unique().tolist()
        values.append("ALL")
        
        return (variable_name, values)
        
    def apply_filters(self, df, filters: List[Tuple[str, Any]]) -> Any:
        """필터 적용"""
        if df is None:
            return None
            
        filtered_df = df.copy()
        
        for variable_name, selected in filters:
            if selected == 'ALL':
                continue
                
            if isinstance(selected, tuple) and len(selected) == 2:
                # 숫자형 필터 (범위)
                filtered_df = filtered_df[(filtered_df[variable_name] >= selected[0]) & 
                                         (filtered_df[variable_name] <= selected[1])]
            else:
                # 범주형 필터
                if hasattr(selected, 'value'):
                    selected = selected.value
                filtered_df = filtered_df[filtered_df[variable_name] == selected]
                
        return filtered_df