import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def generate_insurance_claims(n_samples=2000):
    breeds = ['포메라니안', '푸들', '치와와', '골든리트리버', '비숑', '말티즈', '진돗개', '시바견']
    # 지역구 알파벳 코드
    districts = {
        '강남구': 'GN', '서초구': 'SC', '송파구': 'SP', '강동구': 'GD',
        '강서구': 'GS', '양천구': 'YC', '구로구': 'GR', '영등포구': 'YD',
        '동작구': 'DJ', '관악구': 'GA', '서대문구': 'SD', '마포구': 'MP',
        '은평구': 'EP', '노원구': 'NW', '도봉구': 'DB', '강북구': 'GB',
        '성북구': 'SB', '동대문구': 'DM', '중랑구': 'JR', '성동구': 'SD',
        '광진구': 'GJ', '용산구': 'YS', '중구': 'JG', '종로구': 'JN',
        '금천구': 'GC'
    }
    
    # 견종별 체중 범위 설정
    weight_ranges = {
        '포메라니안': (1.4, 4.0),
        '푸들': (3.5, 8.0),
        '치와와': (1.4, 2.7),
        '골든리트리버': (25.0, 40.0),
        '비숑': (2.5, 5.2),
        '말티즈': (2.0, 5.0),
        '진돗개': (15.0, 25.0),
        '시바견': (7.0, 11.0)
    }
    
    # 날짜 범위 설정 (2023년 1월 1일부터)
    start_date = datetime(2023, 1, 1)
    
    data = []
    # 헤더 추가
    data.append("claim_id,gender,breed,neutralized,district,age,weight,price")
    
    for i in range(n_samples):
        gender = random.choice(['남자', '여자'])
        breed = random.choice(breeds)
        neutralized = random.choice(['y', 'n'])
        district = random.choice(list(districts.keys()))
        age = random.randint(0, 14)
        weight = round(random.uniform(*weight_ranges[breed]), 1)
        
        # 날짜 생성 (1월 1일부터 순차적으로)
        current_date = start_date + timedelta(days=i//8)  # 하루에 약 8건의 청구
        date_str = current_date.strftime("%m%d")  # 월일만 사용
        
        # claim_id 생성: 지역구코드(2) + 날짜(4) + 알파벳 일련번호(1)
        serial_letter = chr(65 + (i % 8))  # A~H
        claim_id = f"{districts[district]}{date_str}{serial_letter}"
        
        # 보험금 청구액 계산
        base_price = 50000
        age_factor = age * 1000
        weight_factor = weight * 500
        
        # 중성화된 경우 추가 비용
        neutralized_factor = 5000 if neutralized == 'y' else 0
        
        # 견종별 추가 비용
        breed_factors = {
            '골든리트리버': 15000,
            '진돗개': 10000,
            '시바견': 8000,
            '푸들': 5000,
            '비숑': 5000,
            '말티즈': 3000,
            '포메라니안': 3000,
            '치와와': 2000
        }
        
        price = base_price + age_factor + weight_factor + neutralized_factor + breed_factors[breed]
        price = max(30000, min(150000, price))  # 가격 범위 제한
        price = (price // 1000) * 1000  # 1000원 단위로 반올림
        
        row = f"{claim_id},{gender},{breed},{neutralized},{district},{age},{weight},{price}"
        data.append(row)
    
    return data

def generate_predictions(insurance_df_path='../data_storage/insurance_claim.csv'):
    # 보험 청구 데이터 읽기
    df = pd.read_csv(insurance_df_path)
    
    # 지역별 기본 가격 설정 (강남권, 강북권, 서남권 등 권역별로 차등)
    district_factors = {
        '강남구': 1.3, '서초구': 1.3, '송파구': 1.25, '강동구': 1.2,  # 강남권
        '용산구': 1.2, '마포구': 1.15, '서대문구': 1.1, '중구': 1.15, '종로구': 1.15,  # 도심권
        '강서구': 1.0, '양천구': 1.0, '구로구': 0.95, '영등포구': 1.05, '금천구': 0.95,  # 서남권
        '성북구': 1.0, '동대문구': 1.0, '중랑구': 0.95, '성동구': 1.05, '광진구': 1.05,  # 동북권
        '은평구': 0.95, '노원구': 1.0, '도봉구': 0.95, '강북구': 0.95, '동작구': 1.0, '관악구': 0.95  # 그 외 지역
    }
    
    # 견종별 가격 영향도
    breed_factors = {
        '골든리트리버': 1.25,
        '진돗개': 1.2,
        '시바견': 1.15,
        '푸들': 1.1,
        '비숑': 1.1,
        '말티즈': 1.05,
        '포메라니안': 1.05,
        '치와와': 1.0
    }
    
    predictions = []
    # 헤더 추가
    predictions.append("claim_id,predicted_price")
    
    for _, row in df.iterrows():
        # 기본 가격
        base_price = row['price']
        
        # 1. 지역 요소 (가장 큰 영향, ±30%)
        district_factor = district_factors[row['district']]
        
        # 2. 나이 요소 (두 번째로 큰 영향, ±20%)
        # 중년 강아지(4-8세)가 가장 비싸고, 어리거나 나이든 강아지는 더 저렴
        age = row['age']
        if 4 <= age <= 8:
            age_factor = 1.2
        elif 2 <= age <= 10:
            age_factor = 1.1
        else:
            age_factor = 1.0
            
        # 3. 품종 요소 (세 번째로 큰 영향, ±25%)
        breed_factor = breed_factors[row['breed']]
        
        # 4. 중성화 요소 (네 번째로 큰 영향, ±10%)
        neutralized_factor = 1.1 if row['neutralized'] == 'y' else 1.0
        
        # 5. 체중 요소 (가장 작은 영향, ±5%)
        # 품종별 평균 체중을 기준으로 정상 범위면 1.0, 과체중이면 1.05, 저체중이면 0.95
        weight = row['weight']
        weight_ranges = {
            '포메라니안': (1.4, 4.0),
            '푸들': (3.5, 8.0),
            '치와와': (1.4, 2.7),
            '골든리트리버': (25.0, 40.0),
            '비숑': (2.5, 5.2),
            '말티즈': (2.0, 5.0),
            '진돗개': (15.0, 25.0),
            '시바견': (7.0, 11.0)
        }
        breed_range = weight_ranges[row['breed']]
        avg_weight = (breed_range[0] + breed_range[1]) / 2
        if weight > avg_weight * 1.2:
            weight_factor = 1.05
        elif weight < avg_weight * 0.8:
            weight_factor = 0.95
        else:
            weight_factor = 1.0
            
        # 최종 예측 가격 계산
        predicted_price = int(base_price * district_factor * age_factor * breed_factor * neutralized_factor * weight_factor)
        
        # 가격 범위 제한 및 반올림
        predicted_price = max(30000, min(200000, predicted_price))
        predicted_price = (predicted_price // 1000) * 1000
        
        # 약간의 랜덤성 추가 (±5%)
        random_factor = random.uniform(0.95, 1.05)
        predicted_price = int(predicted_price * random_factor / 1000) * 1000
        
        predictions.append(f"{row['claim_id']},{predicted_price}")
    
    return predictions

def save_to_csv(file_path='../data_storage/insurance_claim.csv'):
    data = generate_insurance_claims()
    with open(file_path, 'w', encoding='utf-8') as f:
        for row in data:
            f.write(row + '\n')
            
def save_predictions_to_csv(file_path='../data_storage/prediction.csv'):
    predictions = generate_predictions()
    with open(file_path, 'w', encoding='utf-8') as f:
        for row in predictions:
            f.write(row + '\n')

if __name__ == "__main__":
    save_to_csv()
    save_predictions_to_csv()