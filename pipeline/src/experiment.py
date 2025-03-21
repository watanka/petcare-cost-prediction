import json
import os
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

class ExperimentTracker:
    def __init__(self, save_dir: str):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.metrics = {}
        
    def log_experiment(self, info: Dict[str, Any]) -> str:        
        # 실험 디렉토리 생성
        os.makedirs(self.save_dir, exist_ok=True)
        
       
        
        # 메타데이터 저장
        with open(self.save_dir / "metadata.json", "w") as f:
            json.dump(info, f, indent=2)
            
        return self.save_dir
    
    def get_experiment(self) -> Dict[str, Any]:
        """실험 결과 조회"""
        metadata_path = self.save_dir / "metadata.json"
        if not metadata_path.exists():
            raise ValueError(f"Experiment {self.save_dir} not found")
            
        with open(metadata_path, "r") as f:
            return json.load(f)
    
    def log_metric(self, key: str, value: float):
        """메트릭 로깅"""
        self.metrics[key] = value
        
    def save_metric(self):
        # 메트릭 저장
        metrics_file = self.save_dir / "metrics.json"
        with open(metrics_file, "w") as f:
            json.dump(self.metrics, f, indent=2)