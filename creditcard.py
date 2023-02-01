# -*- coding: utf-8 -*-
"""creditcard.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1p2zMGldsRPMUgzocNuk2wLEdzTMaf_wk
"""

# import 

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn

data = pd.read_csv("/content/drive/MyDrive/creditcard/creditcard.csv")

data.head()

# 소수점 두자리만 좀 잘라서 보자.
pd.set_option("display.float", "{:.2f}".format)

# 결측치 확인하기

data.isnull().sum()

# class label 확인하기

data['Class'].value_counts()

percent = (data['Class'].value_counts()[1] / data['Class'].value_counts()[0]) * 100
print(percent)

LABELS = ["Normal","Fraud"]

count_classes = pd.value_counts(data['Class'], sort= True)
count_classes.plot(kind='bar',rot=0)
plt.title("Transaction class distribution")
plt.xticks(range(2), LABELS)
plt.xlabel("Class")
plt.ylabel("Frequency")

corr = data.corr()
fig = plt.figure(figsize = (24,24))

sns.heatmap(corr, vmax=1, square = True, annot = True, vmin=-1)
plt.show()

# 눈 여겨 볼 만한 correlations 은 
# Time & V3 (-0.42), Amount & V2 (-0.53), Amount & V4 (0.4)

# seaborn scheme 로 세팅하고 font_scale 세팅.
plt.style.use('seaborn')
sns.set(font_scale=2.5)

# Commented out IPython magic to ensure Python compatibility.
#ignore warnings
import warnings
warnings.filterwarnings('ignore')

# 브라우저에서 결과 바로 볼 수 있게 해줌.
# %matplotlib inline

fraud = data[data['Class']==1]
normal = data[data['Class']==0]

print(f'shape of fraud : {fraud.shape}')
print(f'shape of non-fraud : {normal.shape}')

# fraud 와 normal 의 'Amount'를 비교해보자 한다.

pd.concat([fraud.Amount.describe(), normal.Amount.describe()], axis=1)

"""- fraud transaction 의 amount가 좀 더 높다."""

# fraud 와 normal 의 'Time'을 비교해보자 한다
pd.concat([fraud.Time.describe(), normal.Time.describe()], axis=1)

plt.figure(figsize=(14, 12))

plt.subplot(2, 2, 1)
data[data.Class == 1].Time.hist(bins=35, color='blue', alpha=0.6, label="Fraudulant Transaction")
plt.legend()

plt.subplot(2, 2, 2)
data[data.Class == 0].Time.hist(bins=35, color='blue', alpha=0.6, label="Non Fraudulant Transaction")
plt.legend()

"""## 전처리"""

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

scalar = StandardScaler()

X = data.drop('Class',axis=1)
y = data.Class

# 먼저 validation과 test 데이터로 나눈다.

X_train_v, X_test, y_train_v, y_test = train_test_split(X, y,test_size=0.3, random_state=42)


# 그 다음 validation data 에서 train 데이터를 나눈다.

X_train, X_validate, y_train, y_validate = train_test_split(X_train_v, y_train_v, test_size=0.2, random_state=42)

# scaler를 한다.
X_train = scalar.fit_transform(X_train)
X_validate = scalar.transform(X_validate)
X_test = scalar.transform(X_test)

# label도 나누어서 변수에 저장한다.
w_p = y_train.value_counts()[0] / len(y_train)
w_n = y_train.value_counts()[1] / len(y_train)

print(f"Fraud transaction 비율: {w_n}")
print(f"Non-Fraud transaction 비율: {w_p}")

from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, f1_score

def print_score(label, prediction, train=True):
    if train:
        clf_report = pd.DataFrame(classification_report(label, prediction, output_dict=True))
        print("Train Result:\n================================================")
        print(f"Accuracy Score: {accuracy_score(label, prediction) * 100:.2f}%")
        print("_______________________________________________")
        print(f"Classification Report:\n{clf_report}")
        print("_______________________________________________")
        print(f"Confusion Matrix: \n {confusion_matrix(y_train, prediction)}\n")

    elif train==False:
        clf_report = pd.DataFrame(classification_report(label, prediction, output_dict=True))
        print("Test Result:\n================================================")        
        print(f"Accuracy Score: {accuracy_score(label, prediction) * 100:.2f}%")
        print("_______________________________________________")
        print(f"Classification Report:\n{clf_report}")
        print("_______________________________________________")
        print(f"Confusion Matrix: \n {confusion_matrix(label, prediction)}\n")

"""## 모델링"""

# ANN 모델

from tensorflow import keras

model = keras.Sequential([
    keras.layers.Dense(256, activation='relu', input_shape=(X_train.shape[-1],)),
    keras.layers.BatchNormalization(),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(256, activation='relu'),
    keras.layers.BatchNormalization(),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(256, activation='relu'),
    keras.layers.BatchNormalization(),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(1, activation='sigmoid'),
])

model.summary()

METRICS = [
#     keras.metrics.Accuracy(name='accuracy'),
    keras.metrics.FalseNegatives(name='fn'),
    keras.metrics.FalsePositives(name='fp'),
    keras.metrics.TrueNegatives(name='tn'),
    keras.metrics.TruePositives(name='tp'),
    keras.metrics.Precision(name='precision'),
    keras.metrics.Recall(name='recall')
]

model.compile(optimizer=keras.optimizers.Adam(1e-4), loss='binary_crossentropy', metrics=METRICS)

callbacks = [keras.callbacks.ModelCheckpoint('fraud_model_at_epoch_{epoch}.h5')]
class_weight = {0:w_p, 1:w_n}

r = model.fit(
    X_train, y_train, 
    validation_data=(X_validate, y_validate),
    batch_size=2048, 
    epochs=300, 
#     class_weight=class_weight,
    callbacks=callbacks,
)

score = model.evaluate(X_test, y_test)
print(score)

plt.figure(figsize=(12,16))

plt.subplot(4,2,1)
plt.plot(r.history['loss'],label='Loss')
plt.plot(r.history['val_loss'],label='val_Loss')
plt.title('Loss Function evolution during training')
plt.legend()

plt.subplot(4,2,2)
plt.plot(r.history['fn'],label='fn')
plt.plot(r.history['val_fn'],label='val_fn')
plt.title('Accuracy evolution during training')
plt.legend()

plt.subplot(4,2,3)
plt.plot(r.history['precision'],label='precision')
plt.plot(r.history['val_precision'],label='val_precision')
plt.title('Precision evolution during training')
plt.legend()

plt.subplot(4,2,4)
plt.plot(r.history['recall'],label='recall')
plt.plot(r.history['val_recall'],label='val_recall')
plt.title('Recall evolution during training')
plt.legend()

# 모델 예측
y_train_pred=model.predict(X_train)
y_test_pred=model.predict(X_test)

print_score(y_train,y_train_pred.round(), train=True)
print_score(y_test,y_test_pred.round(),train=False)

# score를 모아두는 dictionary 만들기
scores_dict = {
    'ANNs' : {
        'Train' : f1_score(y_train,y_train_pred.round()),
        'Test' : f1_score(y_test,y_test_pred.round()),
    },
}

"""## XGBoost"""

from xgboost import XGBClassifier

xgb_clf = XGBClassifier()
xgb_clf.fit(X_train,y_train,eval_metric='aucpr')

y_train_pred= xgb_clf.predict(X_train)
y_test_pred = xgb_clf.predict(X_test)

print_score(y_train,y_train_pred, train=True)
print_score(y_test,y_test_pred, train=False)

# xgboost도 dictionary에 추가해주기.
scores_dict['XGBoost'] = {
        'Train': f1_score(y_train,y_train_pred),
        'Test': f1_score(y_test, y_test_pred),
}

