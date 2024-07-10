## 치료비 예측 모델 파이프라인
- 반려동물 건강정보를 기반으로 보험청구비를 예측하는 머신러닝 모델 파이프라인입니다.
- 모델학습에 부족한 데이터량을 점진적으로 보완하기 위해 재학습 파이프라인을 구성하였습니다.

### Getting started
``` bash
docker-compose up
```

### 시스템 구성도
![시스템 구성도](system-architecture.png)

- **Backend Server**
    - `/inference` : 건강정보를 인풋으로 받아 보험비 예측 결과를 반환합니다.
    - `/statistics` : 보유중인 데이터를 분석하여, 해당 견종의 연령별 자주 걸리는 질병명을 반환합니다.

- **Monitoring Server**
    - DB서버에 새로 기록된 데이터를 모니터링합니다.
    - DB서버의 특정 조건이 충족될 시, 재학습을 요청함.
        - 요청 방식
            1. `/train` 엔드포인트를 backend server쪽에 만들어 처리하게 한다.
            2. k8s를 활용하여 새로운 pod를 띄워 재학습을 진행한다. 
- **DataPipeline**
    - DB에서 데이터를 불러오고, 새로운 모델을 학습한다.
- **Experiment Tracking Server**
    - 실험 결과를 시각적으로 확인한다.
- **ML Inference Server**
    - Backend Server의 inference요청을 전달받아, 추론을 진행한다. deployment를 통해 새로운 모델 웨이트 배포 시, 롤링 업데이트를 통해 반영된다.
