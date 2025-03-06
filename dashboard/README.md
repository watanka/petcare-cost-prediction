# 반려동물 양육비 예측 대시보드

## 주요 기능
- 반려동물 보험 청구 데이터 분석
- 변수별(지역, 견종별, 중성화여부, 연령) 청구금액 비교
- 실제 청구 금액과 모델별 예측 금액 비교

## TODO
- 모델 결과별로 실제값과 확인할 수 있도록 구성


##  `data_storage` 구조
```
prediction
ㄴ{yyyy-mm-dd}
    ㄴ{model_name1}
        ㄴprediction.csv
    ㄴ...
data
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
build -> container(insurance_claim_df, prediction_df), setup_options, 
data_stat_service 
prediction_service
district_stat_service



예측 금액 관련  
- 품종별 뿐만 아니라 각 변수별 평균 청구액과 예측금액이 비교가능할 수 있어야함.
- 같은 고객에 대해 시계열 예측 금액을 비교할 수 있도록 구성해야함. 데이터 학습에 lag feature 추가

## 시각화 예시

### 지역별 분석
![서울시 구별 보험금 청구 현황](img/by_district.png)

###  변수별 청구금액 시각화
![변수별 청구금액 분석](img/by_variable.png)

### 모델별 예측 결과와 실제 결과 비교 시각화
![모델별 예측 결과 비교]

## 설치 및 실행 방법
```bash
docker build -t petcare-dashboard .
docker run --rm -p8501:8501 petcare-dashboard
```


옵션 버튼 만드는 기능

ServiceFactory

NumericService
- Age
CategoryService
- GenderRepository
- NeutralizedRepository
- BreedRepository
- DistrictRepository


데이터 정제 기능

ClaimPriceService(ClaimPriceRepository.select)
- retrieve_claim_prices
ClaimPricePredictionService(ClaimPricePredictionRepository.select)
- calculate_district_statistics -> pd.DataFrame
- aggregate_price_evaluation -> pd.DataFrame