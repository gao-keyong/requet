from matplotlib.pyplot import text
import pandas as pd
import random
import csv
import joblib
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import scale
from sklearn.model_selection import train_test_split

test_file_name='test_data/test_data.csv'#test文件名
test_file=pd.read_csv(test_file_name)

X_test=test_file.iloc[:,:-4]
name_list=["Status", "BuffWarning", "Resolution"]
for i in range(-3,0):
	RF = joblib.load('traindata/RF_'+name_list[i] + '_large.pkl')
	Y_test=test_file.iloc[:,i]
	Y_pred=RF.predict(X_test)
	# joblib.dump(RF, 'traindata/RF_'+name_list[i]+'.pkl', compress=3)
	df_truth = pd.DataFrame({'id': test_file.iloc[:,-4], 'label': Y_test})
	df_pred = pd.DataFrame({'id': test_file.iloc[:,-4], 'label': Y_pred})
	df_truth.to_csv('pred/1-'+ name_list[i] + "-truth" + '.csv',index=False)
	df_pred.to_csv('pred/1-'+ name_list[i] + "-pred" + '.csv',index=False)
	print(accuracy_score(Y_pred,Y_test))