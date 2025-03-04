# 반려동물 양육비 예측 대시보드

## 주요 기능
- 반려동물 보험 청구 데이터 분석
- 지역별, 견종별, 연령별 양육비 예측
- 품종별 실제 청구액과 예측액 비교 분석

## TODO  
청구 금액 시각화
- 지역별 청구 금액 시각화 (UI 찾기)

예측 금액 관련  
- 품종별 뿐만 아니라 각 변수별 평균 청구액과 예측금액이 비교가능할 수 있어야함.
- 같은 고객에 대해 시계열 예측 금액을 비교할 수 있도록 구성해야함. 데이터 학습에 lag feature 추가

## 시각화 예시

### 지역별 분석
![서울시 구별 보험금 청구 현황](img/district_analysis.png)

### 견종별 분석
![견종별 보험금 분석](img/breed_analysis.png)

### 변수별 청구금액
![변수별 청구금액 분석](img/by_variable.png)

## 설치 및 실행 방법
```bash
docker build -t petcare-dashboard .
docker run --rm -p8501:8501 petcare-dashboard
```

