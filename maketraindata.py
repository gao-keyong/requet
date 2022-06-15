import pandas as pd
import random
import chunkdetection
import csv
import glob
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import scale
dataset_list=['A']
ans=[]
for dataset in dataset_list:
	dataset_folder = 'reqdata/' + dataset + '/'
	files = glob.glob(dataset_folder + '*_tag.csv')
	#cnt=0
	for file_name in files:
		file=pd.read_csv(file_name)#wxh's csv name
		feature_file='RequetDataSet-master\\'+dataset+'\\PCAP_FILES\\'+file_name.split('\\')[1][:-15]+'.pcap'#yhy's pcap name
		feature_class=chunkdetection.ChunkDetection(feature_file)
		lable_size=file.shape[0]
		for i in range(0,lable_size,50):
			feature=feature_class.getFeature(file.iloc[i,0])
			if not feature:
				continue
			feature.extend(file.iloc[i,1:])
			ans.append(feature)
out_file=open('traindata/train_data.csv','w',newline='')# output   be careful of filename
writer=csv.writer(out_file)
keys=['label'+str(i) for i in range(120)]
keys.extend(['status','BuffWarning','Resolution'])
writer.writerow(keys)
for i in ans:
	writer.writerow(i)
out_file.close()