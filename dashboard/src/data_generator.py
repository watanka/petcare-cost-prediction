import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import string

def generate_pet_insurance_data(n_pets=200, claims_per_pet=(8, 12)):
    """
    반려동물 보험 청구 데이터 생성
    
    Parameters:
    -----------
    n_pets : int
        생성할 반려동물 수
    claims_per_pet : tuple
        각 반려동물당 생성할 청구 건수 범위 (최소, 최대)
    """
    # 품종 정보
    breeds = {
        '푸들': {'code': 'PD', 'weight_range': (3.5, 8.0), 'base_price': 42000},
        '말티즈': {'code': 'MT', 'weight_range': (2.0, 5.0), 'base_price': 40000},
        '비숑': {'code': 'BC', 'weight_range': (2.5, 5.2), 'base_price': 45000},
        '치와와': {'code': 'CH', 'weight_range': (1.4, 2.7), 'base_price': 35000},
        '포메라니안': {'code': 'PM', 'weight_range': (1.4, 4.0), 'base_price': 38000},
        '골든리트리버': {'code': 'GR', 'weight_range': (25.0, 40.0), 'base_price': 55000},
        '진돗개': {'code': 'JD', 'weight_range': (15.0, 25.0), 'base_price': 48000},
        '시바견': {'code': 'SB', 'weight_range': (7.0, 11.0), 'base_price': 50000}
    }
    
    # 성별 코드
    gender_codes = {'남자': 'M', '여자': 'F'}
    
    # 지역구 정보 (경제적 수준에 따른 가중치)
    districts = {
        '강남구': {'code': 'GN', 'price_factor': 1.30},
        '서초구': {'code': 'SC', 'price_factor': 1.25},
        '송파구': {'code': 'SP', 'price_factor': 1.20},
        '용산구': {'code': 'YS', 'price_factor': 1.15},
        '마포구': {'code': 'MP', 'price_factor': 1.10},
        '영등포구': {'code': 'YD', 'price_factor': 1.05},
        '성동구': {'code': 'SD', 'price_factor': 1.00},
        '광진구': {'code': 'GJ', 'price_factor': 1.00},
        '강동구': {'code': 'GD', 'price_factor': 0.95},
        '양천구': {'code': 'YC', 'price_factor': 0.95},
        '강서구': {'code': 'GS', 'price_factor': 0.90},
        '구로구': {'code': 'GR', 'price_factor': 0.90},
        '동작구': {'code': 'DJ', 'price_factor': 0.90},
        '서대문구': {'code': 'SM', 'price_factor': 0.90},
        '중구': {'code': 'JG', 'price_factor': 0.90},
        '종로구': {'code': 'JN', 'price_factor': 0.90},
        '성북구': {'code': 'SB', 'price_factor': 0.85},
        '동대문구': {'code': 'DM', 'price_factor': 0.85},
        '노원구': {'code': 'NW', 'price_factor': 0.85},
        '강북구': {'code': 'GB', 'price_factor': 0.80},
        '도봉구': {'code': 'DB', 'price_factor': 0.80},
        '은평구': {'code': 'EP', 'price_factor': 0.80},
        '관악구': {'code': 'GA', 'price_factor': 0.80},
        '금천구': {'code': 'GC', 'price_factor': 0.80},
        '중랑구': {'code': 'JR', 'price_factor': 0.80}
    }
    
    # 중성화 여부에 따른 가격 가중치
    neutralized_factors = {'y': 1.05, 'n': 1.0}
    
    # 나이에 따른 가격 가중치 함수
    def age_price_factor(age):
        if age <= 1:
            return 0.9  # 어린 강아지
        elif 2 <= age <= 5:
            return 1.0  # 청년기
        elif 6 <= age <= 9:
            return 1.1  # 중년기
        else:
            return 1.2  # 노년기
    
    # 데이터 생성
    all_data = []
    
    # 시작 날짜 설정 (2023년 1월 1일부터)
    start_date = datetime(2023, 1, 1)
    
    # 각 반려동물 생성
    for pet_idx in range(n_pets):
        # 반려동물 기본 정보 선택
        gender = random.choice(['남자', '여자'])
        breed = random.choice(list(breeds.keys()))
        neutralized = random.choice(['y', 'n'])
        district = random.choice(list(districts.keys()))
        
        # 반려동물 나이 (0~14세)
        age = random.randint(0, 14)
        
        # 반려동물 체중 (품종별 범위 내에서 랜덤)
        weight_range = breeds[breed]['weight_range']
        weight = round(random.uniform(*weight_range), 1)
        
        # pet_id 생성 (품종코드 + 성별코드 + 일련번호)
        breed_code = breeds[breed]['code']
        gender_code = gender_codes[gender]
        pet_id = f"{breed_code}{gender_code}{pet_idx+1:03d}"
        
        # 각 반려동물별 청구 건수 결정
        n_claims = random.randint(*claims_per_pet)
        
        # 청구 날짜 생성 (최근 1년 내 랜덤 날짜)
        claim_dates = []
        for _ in range(n_claims):
            days_offset = random.randint(0, 364)
            claim_date = start_date + timedelta(days=days_offset)
            claim_dates.append(claim_date)
        
        # 날짜순 정렬
        claim_dates.sort()
        
        # 각 청구 건에 대한 데이터 생성
        for i, issued_at in enumerate(claim_dates):
            # 기본 가격 (품종별)
            base_price = breeds[breed]['base_price']
            
            # 지역 가중치 (가장 큰 영향)
            district_factor = districts[district]['price_factor']
            
            # 나이 가중치 (두 번째 영향)
            age_factor = age_price_factor(age)
            
            # 중성화 가중치 (네 번째 영향)
            neutralized_factor = neutralized_factors[neutralized]
            
            # 최종 가격 계산
            price = base_price * district_factor * age_factor * neutralized_factor
            
            # 약간의 랜덤성 추가 (±5%)
            random_factor = random.uniform(0.95, 1.05)
            price = int(price * random_factor / 1000) * 1000  # 1000원 단위로 반올림
            
            # claim_id 생성 (지역코드 + 날짜(MMDD) + 일련번호(알파벳))
            district_code = districts[district]['code']
            date_code = issued_at.strftime("%m%d")
            serial_letter = chr(65 + i % 26)  # A부터 시작하는 알파벳
            claim_id = f"{district_code}{date_code}{serial_letter}"
            
            # 데이터 추가
            all_data.append({
                'claim_id': claim_id,
                'pet_id': pet_id,
                'gender': gender,
                'breed': breed,
                'neutralized': neutralized,
                'district': district,
                'age': age,
                'weight': weight,
                'price': price,
                'issued_at': issued_at.strftime("%Y-%m-%d")
            })
    
    # DataFrame 생성
    df = pd.DataFrame(all_data)
    
    return df

def save_to_csv(file_path='../data_storage/insurance_claim.csv'):
    """
    생성된 데이터를 CSV 파일로 저장
    """
    df = generate_pet_insurance_data()
    df.to_csv(file_path, index=False)
    print(f"데이터가 {file_path}에 저장되었습니다.")
    return df

if __name__ == "__main__":
    save_to_csv()