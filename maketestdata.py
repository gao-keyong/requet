import pandas as pd
import random
import chunkdetection
import csv
import glob
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import scale
# dataset_list=['A', 'B1', 'B2', 'C', 'D']
# len_list = {
# 	'A': 10,
# 	'B1': 5,
# 	'B2': 4,
# 	'C': 10,
# 	'D': 10
# }


def make_test_data(tag_folder, test_set_folder, result_folder):
    ans = []
    # for dataset in dataset_list:
    dataset_folder = tag_folder + '/'
    files = glob.glob(dataset_folder + '*_tag.csv')
    # cnt=0
    for i in range(len(files)):
        file_name = files[i]
        print("Processing file: " + file_name)
        # if (i >= len_list[dataset]):
        # 	break
        file = pd.read_csv(file_name)  # wxh's csv name
        feature_file = test_set_folder+'/'+'/PCAP_FILES/' + \
            file_name.split('/')[-1][:-15]+'.pcap'  # yhy's pcap name
        feature_class = chunkdetection.ChunkDetection(feature_file)
        lable_size = file.shape[0]
        for i in range(0, lable_size, 50):
            feature = feature_class.getFeature(file.iloc[i, 0])
            if not feature:
                continue
            feature.append(file_name + "-" + str(file.iloc[i, 0]))
            feature.extend(file.iloc[i, 1:])
            ans.append(feature)
    # output   be careful of filename
    out_file = open(result_folder+'/test_data.csv', 'w', newline='')
    writer = csv.writer(out_file)
    keys = ['label'+str(i) for i in range(120)]
    keys.extend(['filename_time', 'status', 'BuffWarning', 'Resolution'])
    writer.writerow(keys)
    for i in ans:
        writer.writerow(i)
    out_file.close()
