# import pandas as pd
# import numpy as np
# from datetime import datetime

# def generate_pet_data(n_samples=2000):
#     np.random.seed(42)
    
#     # 서울시 구별 보험비 기본 비율 설정 (강남구를 기준으로 상대적 비율)
#     district_insurance_ratio = {
#         '강남구': 1.3, '서초구': 1.25, '송파구': 1.2, '용산구': 1.15,
#         '마포구': 1.1, '영등포구': 1.05, '성동구': 1.0, '광진구': 1.0,
#         '강동구': 0.95, '양천구': 0.95, '강서구': 0.9, '구로구': 0.9,
#         '동작구': 0.9, '서대문구': 0.9, '중구': 0.9, '종로구': 0.9,
#         '성북구': 0.85, '동대문구': 0.85, '노원구': 0.85, '강북구': 0.8,
#         '도봉구': 0.8, '은평구': 0.8, '관악구': 0.8, '금천구': 0.8,
#         '중랑구': 0.8
#     }
    
#     # 품종별 보험비 기본 금액 설정 (월 기준)
#     breed_base_insurance = {
#         '말티즈': 40000,
#         '비숑': 45000,
#         '치와와': 35000,
#         '푸들': 42000,
#         '포메라니안': 38000,
#         '골든리트리버': 55000,
#         '진돗개': 48000,
#         '시바견': 50000
#     }
    
#     # 품종별 평균 체중 범위 설정
#     breed_weights = {
#         '말티즈': (2.5, 1),
#         '비숑': (4, 1),
#         '치와와': (2, 0.5),
#         '푸들': (5, 1.5),
#         '포메라니안': (2.5, 0.8),
#         '골든리트리버': (30, 5),
#         '진돗개': (20, 3),
#         '시바견': (10, 2)
#     }
    
#     # 기본 데이터 생성
#     breeds = np.random.choice(list(breed_weights.keys()), size=n_samples)
#     districts = np.random.choice(list(district_insurance_ratio.keys()), size=n_samples)
#     ages = np.random.randint(0, 15, size=n_samples)
    
#     # 체중 생성
#     weights = []
#     for breed in breeds:
#         mean, std = breed_weights[breed]
#         weight = np.random.normal(mean, std)
#         weight = max(0.5, round(weight, 1))
#         weights.append(weight)
    
#     # 보험비 계산
#     insurance_costs = []
#     for breed, district, age in zip(breeds, districts, ages):
#         # 기본 보험료
#         base_cost = breed_base_insurance[breed]
        
#         # 지역 가중치
#         district_ratio = district_insurance_ratio[district]
        
#         # 나이 가중치 (나이가 많을수록 보험료 증가)
#         age_ratio = 1 + (age * 0.1)  # 매년 10%씩 증가
        
#         # 최종 보험료 계산 (약간의 랜덤성 추가)
#         final_cost = base_cost * district_ratio * age_ratio
#         random_factor = np.random.uniform(0.95, 1.05)  # ±5% 랜덤 변동
#         final_cost = int(round(final_cost * random_factor, -3))  # 1000원 단위로 반올림
        
#         insurance_costs.append(final_cost)
    
#     data = {
#         'gender': np.random.choice(['남자', '여자'], size=n_samples),
#         'breed': breeds,
#         'neutralized': np.random.choice(['y', 'n'], size=n_samples),
#         'district': districts,
#         'age': ages,
#         'weight': weights,
#         'insurance_cost': insurance_costs
#     }
    
#     df = pd.DataFrame(data)
#     return df

# # 데이터 생성 및 CSV 파일로 저장
# df = generate_pet_data()
# df.to_csv('pet_data.csv', index=False, encoding='utf-8-sig')


import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder

# 데이터 로드
df = pd.read_csv('data/insurance_claim.csv')

# claim_id 추가 (1부터 시작하는 일련번호)
df['claim_id'] = range(1, len(df) + 1)

# 원본 데이터에 claim_id 추가하여 저장
df.to_csv('data/insurance_claim.csv', index=False)

# 예측 모델 생성
# 특성(X)과 타겟(y) 분리
X = df.drop(['price', 'claim_id'], axis=1)
y = df['price']

# 범주형 변수 원-핫 인코딩
categorical_cols = ['gender', 'breed', 'neutralized', 'district']
encoder = OneHotEncoder(sparse_output=False, drop='first')
encoded_cats = encoder.fit_transform(X[categorical_cols])
encoded_df = pd.DataFrame(encoded_cats, columns=encoder.get_feature_names_out(categorical_cols))

# 수치형 변수와 결합
numerical_cols = ['age', 'weight']
X_processed = pd.concat([encoded_df.reset_index(drop=True), X[numerical_cols].reset_index(drop=True)], axis=1)

# 모델 학습
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_processed, y)

# 예측 수행
predictions = model.predict(X_processed)

# 예측 결과를 담은 DataFrame 생성
prediction_df = pd.DataFrame({
    'claim_id': df['claim_id'],
    'predicted_price': predictions.round().astype(int)
})

# prediction.csv 파일로 저장
prediction_df.to_csv('data/prediction.csv', index=False)

print("처리가 완료되었습니다.")
print(f"원본 데이터에 claim_id가 추가되었습니다: data/insurance_claim.csv")
print(f"예측 결과가 저장되었습니다: prediction.csv")