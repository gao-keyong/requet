import os
import glob


import pandas as pd

from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)

# dataset_list = ['A', 'B1', 'B2', 'C', 'D']
dataset_list = ['']

Sum = 0
Num = [0 for _ in range(0, 4)]

mintime_stall = 10
thr_ss = 15
Resolution_list = ['q144p', 'q240p', 'q360p', 'q480p', 'q720p', 'q1080p', 'q1440p', 'q2160p']
status_list = ['Stall', 'Steady State', 'Buffer Decay', 'Buffer Increase']


def smooth_status(status_origin, m_t):
    status_smooth = status_origin.copy()
    now_index = 0
    # last_index = 0
    while now_index < len(status_smooth):
        if status_smooth[now_index] == 0:
            last_index = now_index
            end = min(len(status_smooth), now_index + mintime_stall * 10 + 1)
            for j in range(now_index + 1, end):
                if status_smooth[j] == 0:
                    last_index = j
            for j in range(now_index + 1, last_index + 1):
                status_smooth[j] = 0
            if last_index != now_index:
                now_index = last_index
            else:
                now_index = now_index + 1
        else:
            now_index = now_index + 1
    
    now_index = 0
    while now_index < len(status_smooth):
        if status_smooth[now_index] == 1:
            last_index = now_index
            end = min(len(status_smooth), now_index + mintime_stall * 10 + 1)
            for j in range(now_index + 1, end):
                if status_smooth[j] == 1:
                    last_index = j
            for j in range(now_index + 1, last_index + 1):
                status_smooth[j] = 1
            if last_index != now_index:
                now_index = last_index
            else:
                now_index = now_index + 1
        else:
            now_index = now_index + 1

    num = [0 for _ in range(len(status_smooth))]
    num[0] = 1
    for now_index in range(1, len(status_smooth)):
        if status_smooth[now_index] == 1:
            if status_smooth[now_index - 1] == 1:
                num[now_index] = num[now_index - 1] + 1
            else:
                num[now_index] = 1
                if num[now_index - 1] <= thr_ss * 10:
                    for j in range(now_index - 1, -1, -1):
                        if status_smooth[j] == 1:
                            status_smooth[j] = 3 if m_t[j] >= 0 else 2
                        else:
                            break
    
    return status_smooth

for dataset in dataset_list:
    dataset_folder = 'test_data/' + dataset + '/'
    files = glob.glob(dataset_folder + '*_tag.csv')
    for file in files:
        # print(file)
        os.remove(file)
    

for dataset in dataset_list:
    dataset_folder = 'test_data/' + dataset + '/'
    files = glob.glob(dataset_folder + '*.csv')

    for file in files:
        # file = "reqdata/A/baseline_Jan17_exp_28_merged.csv"
        fileid = file.split('.')[0]
        # if fileid.split('_')[-1] == 'tag':
        #     continue
        # if os.path.exists(fileid + '_tag.csv'):
        #     continue
        print(fileid)
        df = pd.read_csv(file)
        df_new = pd.DataFrame(columns=["EpochTime",  "BuffWarning", "status", "Resolution"])
        stallThreshold = 0.08
        delta = 0.0001
        epsilon = 0.15
        T_smooth = 15
        T_slope = 5
        buff_ss = 10
        BuffWarningThresh = 20
        hat_b = {}
        m = []
        status = []
        for index, row in df.iterrows():
            hat_b[round(row['RelativeTime'] * 10) / 10] = df[(df['RelativeTime'] >= row['RelativeTime'] - T_smooth - delta) & (
                        df['RelativeTime'] <= row['RelativeTime'] + T_smooth + delta)].BufferHealth.median()
            # print(round(row['RelativeTime'] * 10) / 10)
        maxTime = round(df['RelativeTime'].max() * 10) / 10
        for index, row in df.iterrows():
            if row["BufferValid"] == "-1":
                continue
            if index > 0:
                if row["EpochTime"] == df.iloc[index - 1]["EpochTime"] or 0 == df.iloc[index - 1]["EpochTime"]:
                    continue
            # df_new.append(row)
            new_row = [row["EpochTime"]]
            t = round(row['RelativeTime'] * 10) / 10
            t_slope_1 = round((t + T_slope) * 10) / 10
            t_slope_2 = round((t - T_slope) * 10) / 10
            if t_slope_1 > maxTime:
                t_slope_1 = maxTime
            if t_slope_2 < 0:
                t_slope_2 = 0
            # print(t_slope_1, t_slope_2)
            Resolution = len(Resolution_list)
            for i in range(len(Resolution_list)):
                if row[Resolution_list[i]] == 1:
                    Resolution = i
                    break
            # Resolutions.append(Resolution)

            mt = (hat_b[t_slope_1] - hat_b[t_slope_2]) / (t_slope_1 - t_slope_2)
            m.append(mt)

            b_t = row['BufferHealth']
            if b_t < BuffWarningThresh:
                new_row.append(1)
            else:
                new_row.append(0)
            
            if b_t < stallThreshold:
                state = 0
            elif -epsilon <= mt <= epsilon and b_t > buff_ss:
                state = 1
            elif mt < 0:
                state = 2
            else:
                state = 3
            Sum = Sum + 1
            Num[state] = Num[state] + 1
            new_row.append(state)
            status.append(state)
            new_row.append(Resolution)
            df_new.loc[len(df_new)] = new_row
            
        status = smooth_status(status, m)
        df_new['status'] = status
        # df_new['BuffWarning'] = BuffWarnings
        # df_new['Resolution'] = Resolutions
        
        df_new.to_csv(fileid + '_tag.csv', index=None, header=True)
    #     break
    # break

print(Sum, Num)
