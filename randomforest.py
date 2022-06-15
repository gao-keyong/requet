import pandas as pd
import random
import csv
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import scale
from sklearn.model_selection import train_test_split
train_times=10# 在训练集中建立train_times个随机森林，选择训练集中表现最好的用来跑test
Tree_num=80#随机森林里树的个数
train_file_name='traindata/train_data.csv'#train文件名
train_file=pd.read_csv(train_file_name)
test_file_name='traindata/train_data.csv'#test文件名
test_file=pd.read_csv(test_file_name)
X_train=train_file.iloc[:,:-3]
X_test=test_file.iloc[:,:-3]
for i in range(-3,0):
	x_train,x_test,y_train,y_test = train_test_split(train_file.iloc[:,:-3],train_file.iloc[:,i:i+1],test_size=0.3,random_state=2022)#test_size：用来控制选择训练集里test_size的数据作为用来评价随机森林时的测试集
	RF=RandomForestClassifier(n_estimators=Tree_num)
	RF.fit(x_train,y_train)
	y_pred=RF.predict(x_test)
	accuracy=accuracy_score(y_pred,y_test)
	for j in range(train_times):
		rf=RandomForestClassifier(n_estimators=Tree_num)
		rf.fit(x_train,y_train)
		tmp_y_pred=rf.predict(x_test)
		if accuracy<accuracy_score(tmp_y_pred,y_test):
			y_pred=tmp_y_pred
			accuracy=accuracy_score(tmp_y_pred,y_test)
			RF=rf
	Y_test=test_file.iloc[:,i:i+1]
	Y_pred=RF.predict(X_test)
	print(accuracy_score(Y_pred,Y_test))