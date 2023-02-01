# creditcard_fraud_detection
kaggle / 카드 사기 탐지

## EDA
- Time, V1 ~ V28, Amount 변수가 있다.
- V1 ~ V28은 개인 정보를 위해 변수가 공개되지 않는다.
- 결측치는 존재하지 않았다.
- Fraud로 labeling 된 데이터는 전체의 0.17%로 불균형한 데이터다.
- Correlation 결과 눈여겨 볼 만한 feature는 Time & V3 (-0.42), Amount & V2 (-0.53), Amount & V4 (0.4)이다.
- 
## 전처리
- validation과 test데이터를 먼저 나누고 validation data 안에서 train data 를 형성한다.
- Standard Scaler를 적용한다.
- print_score 함수를 만들어 모델링에서 사용한다.

## 모델링
- 모델링 결과를 scores_dict 에 모아두고 나중에 결과를 비교하고자 한다.
- 모델링에는 ANN, XGBoost, CatBoost, LightGBM 을 사용하였다.

## 결과
![모델링결과](https://user-images.githubusercontent.com/69780999/216016606-580594a1-4e23-4519-8509-28287eb33824.PNG)

