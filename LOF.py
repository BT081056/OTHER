import pandas as pd
import numpy as np
from sklearn.neighbors import LocalOutlierFactor as LOF
import time
 
data = pd.read_csv('data.csv')
print(data.columns)
data_cut = data.drop(columns = ['Unnamed: 0', 'datetime'])
data_list = []
for d in range(len(data_cut)):
    onedata = data_cut.loc[d].values
    data_list.append(onedata)


X = [[-1.1,5], [0.2,4], [100.1,3], [0.3,2]]
X = data_list
clf = LOF(n_neighbors=2)
t1 = time.time()
res = clf.fit_predict(X)
print(time.time() - t1)
print(clf.negative_outlier_factor_)
 

for i in res:
    if i != 1:
        break

'''
https://www.cnblogs.com/wj-1314/p/14049195.html
如果 X = [[-1.1], [0.2], [100.1], [0.3]]
[ 1  1 -1  1]
[ -0.98214286  -1.03703704 -72.64219576  -0.98214286]
 
如果 X = [[-1.1], [0.2], [0.1], [0.3]]
[-1  1  1  1]
[-7.29166666 -1.33333333 -0.875      -0.875     ]
 
如果 X = [[0.15], [0.2], [0.1], [0.3]]
[ 1  1  1 -1]
[-1.33333333 -0.875      -0.875      -1.45833333]
'''
