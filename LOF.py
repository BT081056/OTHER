'''
https://www.cnblogs.com/wj-1314/p/14049195.html
'''

import pandas as pd
import numpy as np
from sklearn.neighbors import LocalOutlierFactor as LOF
import time
import random
Col_len = 5
x1 = []
for c in range(20):
    x_ = []
    for d in range(Col_len):
        if c == 55:
            value1 =  random.randint(7,9)
        else:
            value1 = random.randint(0,5)
        x_.append(value1)
    x1.append(x_)


x2 = []
for c in range(3):
    x_ = []
    for d in range(Col_len):
        value1 =  random.randint(0,5)
        x_.append(value1)
    x2.append(x_)

#x2 = [[1, 1, 2, 0, 0, 2, 2, 2, 0, 2],
# [0, 0, 2, 2, 2, 2, 3, 0, 2, 0],
# [0, 3, 1, 1, 2, 2, 1, 2, 0, 1]]

x3 = []
for c in range(3):
    x_ = []
    for d in range(Col_len):
        value1 =  random.randint(5,7)
        x_.append(value1)
    x3.append(x_)
#
#x3 = [[8, 6, 3, 5, 2, 5, 4, 8, 2, 5],
# [4, 8, 5, 8, 2, 8, 7, 4, 6, 6],
# [2, 2, 4, 7, 3, 9, 3, 9, 8, 7]]


np.ones(x1.shape[0], dtype=int)
X_train = x1
X_test = x3

clf = LOF(n_neighbors=2, contamination='auto', novelty=True)
clf.fit(X_train)
Train_Pred = clf.predict(X_train)

limit_score = max(clf.score_samples(X_train)[Train_Pred == -1])



y_pred_test = clf.score_samples(X_test)
y_score_test = clf.predict(X_test)

print(y_pred_test,y_score_test)
