### 양육비 예측
-----


#### 목적
- 품종, 나이, 산책횟수, 건강 정보 등의 정보가 주어졌을 때 평균 양육비를 예측한다.

#### 데이터
```
show tables; 
select distinct user_id, disease_name, birth, gender, neuter_yn, weight_kg, created_at from pet_insurance_claim as pi left join pet as p
on pi.user_id=p.user_id
where type_of_claims="치료비";
```


#### 사용 모델
Tree 모델

