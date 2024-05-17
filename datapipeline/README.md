### 양육비 예측
-----

### time log
4/24 : mlflow 적용, 우리카드 데이터 EDA  
4/25 : poetry 환경 구성, dockerfile 작성 api 설계  
4/26 : BI 작성
4/29 : CI/CD 구성
scheduler(main 함수를 트리거할 scheduler) 구성, api 설계

### TODO  
- [o] poetry 환경 설정
- [o] dockerfile 작성
- [ ] 데이터 검증 추가
- [ ] CI/CD 구성
- [ ] 스케쥴러-DB 모니터링하며, 조건성립시 main.py 실행 기능 구현
- [ ] 모델 고도화


### 프로젝트 구조
```
petcare_cost_prediction  
├── docs  
├── hydra  
├── petcare_cost_prediction  
|   ├── dataset  
|   ├── jobs  
|   |   ├── __init__.py  
|   |   ├── optimize.py  
|   |   ├── predict.py  
|   |   ├── register.py  
|   |   ├── retrieve.py  
|   |   └── train.py  
|   ├── middleware  
|   ├── models  
|   └── configurations  
├── tests  
├── Dockerfile  
├── Dockerfile.mlflow  
├── main.py  
|   ├── __init__.py
|   ├── base_model.py
|   ├── models.py
|   └── preprocess.py
└── pipeline.drawio  
```

### API Endpoint
- /predict `POST`: request: 관련 정보(입력 또는 DB로부터 수집) 기반 양육비 예측 결과 요청
- /analyze `GET` : 분석 페이지(streamlit)로 연결 -> 관리자 쪽에서 분석 결과 확인
- /experiment `GET` : mlflow 실험관리 -> 관리자 쪽에서 실험 결과 확인


### Getting Started
mlflow server



#### 목적
- 품종, 나이, 산책횟수, 건강 정보 등의 정보가 주어졌을 때 평균 양육비를 예측한다.

#### 데이터
```
show tables; 
select distinct user_id, disease_name, birth, gender, neuter_yn, weight_kg, created_at from pet_insurance_claim as pi left join pet as p
on pi.user_id=p.user_id
where type_of_claims="치료비";
```


#### 환경 관리
- poetry
- docker
- MLflow
- Hydra



#### 사용 모델
Tree 모델: LightGBM

claim_price, disease_name, accident_content, pet_breed_id, birth, gender, neuter_yn, weight_kg, 