# 반려동물 양육비 예측 대시보드

## 주요 기능
- 반려동물 보험 청구 데이터 분석
- 변수별(지역, 견종별, 중성화여부, 연령) 청구금액 비교
- 모델 예측값의 변수별 오차율 시각화
- 모델별 예측값 비교 



## 설치 및 실행 방법
```bash
docker build -t petcare-dashboard .
docker run --rm -p8501:8501 petcare-dashboard
```


##  `data_storage` 구조
```
prediction
ㄴ{yyyy-mm-dd}
    ㄴ{model_name1}
        ㄴprediction.csv
    ㄴ...
records
ㄴ{yyyy-mm-dd}
    ㄴ insurance_claim.csv
ㄴ ...
```


## 데이터 구조
```csv
# insurance_claim.csv
claim_id,pet_id,gender,breed,neutralized,district,age,weight,price,issued_at
JG0105A,GRM001,남자,골든리트리버,n,중구,3,29.3,50000,2023-01-05
JG0212B,GRM001,남자,골든리트리버,n,중구,3,29.3,50000,2023-02-12
JG0411C,GRM001,남자,골든리트리버,n,중구,3,29.3,47000,2023-04-11
JG0508D,GRM001,남자,골든리트리버,n,중구,3,29.3,50000,2023-05-08
```

```csv
# prediction.csv
claim_id, predicted_price
YS0101A,98000
DJ0101C,73000
GC0101D,81000
```

## 코드 구조
```
dashboard/src/
├── app.py                  # 애플리케이션 진입점
├── config/                 # 설정 관리
│   ├── __init__.py
│   └── settings.py         # 설정 클래스
├── models/                 # 데이터 모델
│   ├── __init__.py
│   ├── container.py        # 데이터 컨테이너
│   ├── enums.py            # 열거형 정의
│   └── schema.py           # 데이터 스키마
├── services/               # 비즈니스 로직
│   ├── __init__.py
│   ├── data_service.py     # 데이터 처리 서비스
│   ├── prediction_service.py # 예측 관련 서비스
│   └── district_service.py # 지역 데이터 서비스
├── views/                  # UI 표시
│   ├── __init__.py
│   ├── base_view.py        # 기본 뷰 클래스
│   ├── dashboard_view.py   # 대시보드 메인 뷰
│   ├── data_analysis_view.py # 데이터 분석 뷰
│   ├── map_view.py         # 지도 시각화 뷰
│   └── prediction_view.py  # 예측 분석 뷰
├── controllers/            # 제어 로직
│   ├── __init__.py
│   ├── dashboard_controller.py # 대시보드 컨트롤러
│   └── filter_controller.py    # 필터 컨트롤러
├── utils/                  # 유틸리티 함수
│   ├── __init__.py
│   ├── logger.py           # 로깅 유틸리티
│   └── visualization.py    # 시각화 유틸리티
└── widgets/                # UI 컴포넌트
    ├── __init__.py
    ├── widget_factory.py   # 위젯 팩토리
    ├── filter_widgets.py   # 필터 위젯
    └── chart_widgets.py    # 차트 위젯
```

## 주요 컴포넌트 설명
1. 모델 (Models)
Container: 애플리케이션 전체에서 공유되는 데이터와 설정을 관리하는 중앙 저장소  
Enums: 애플리케이션에서 사용되는 열거형 상수 정의 (BI 유형, 변수 유형, 차트 유형 등)  
Schema: 데이터 구조 정의 및 유효성 검증을 위한 클래스  
2. 서비스 (Services)
DataService: 보험 청구 데이터 처리 및 필터링 로직  
PredictionService: 예측 데이터 처리 및 성능 평가 로직  
DistrictService: 지역별 데이터 처리 및 지도 데이터 관리 로직  
3. 뷰 (Views)
BaseView: 모든 뷰의 기본 클래스로 공통 UI 메서드 제공  
DashboardView: 메인 대시보드 UI 관리  
DataAnalysisView: 데이터 분석 탭 UI 관리  
MapView: 지도 시각화 탭 UI 관리  
PredictionView: 예측 평가 UI 관리  
4. 컨트롤러 (Controllers)
DashboardController: 데이터 로드 및 애플리케이션 흐름 제어  
FilterController: 필터 옵션 관리 및 필터링 로직 제어  
5. 유틸리티 (Utils)
logger: 로깅 기능 제공  
visualization: 시각화 관련 유틸리티 함수 제공  
6. 위젯 (Widgets)  
WidgetFactory: 다양한 UI 위젯 생성을 위한 팩토리 클래스  
FilterWidgets: 필터 관련 위젯 관리  
ChartWidgets: 차트 생성 및 관리  


## 시각화 예시
***시각화에 사용된 데이터는 예시로 만든 샘플데이터입니다.***
### 지역별 분석
![서울시 구별 보험금 청구 현황](img/by_district.png)

###  변수별 청구금액 시각화
![변수별 청구금액 분석](img/by_variable.png)

### 모델별 예측 결과와 실제 결과 비교
![모델별 예측결과와 실제 결과 비교](img/prediction_by_model.png)

### 모델별 예측 결과 비교(변수별 오차율)
![모델별 예측 결과 비교](img/model_comparison.png)

### 모델의 변수별 예측 오차율 분석
![모델의 변수별 예측 오차율 분석](img/prediction_error_by_breed.png)

