import glob

import pandas as pd

dataset_list = ['A', 'B1', 'B2', 'C', 'D']

Sum = 0
Num = [0 for _ in range(0, 4)]

Resolution_list = ['q144p', 'q240p', 'q360p', 'q480p', 'q720p', 'q1080p', 'q1440p', 'q2160p']
status_list = ['Stall', 'Steady State', 'Buffer Decay', 'Buffer Increase']

for dataset in dataset_list:
    dataset_folder = 'data/' + dataset + '/'
    files = glob.glob(dataset_folder + '*.csv')

    for file in files:
        file = "data/A/baseline_Jan17_exp_28_merged.csv"
        fileid = file.split('.')[0]
        print(fileid)
        df = pd.read_csv(file)
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
        BuffWarnings = []
        Resolutions = []
        a, b, c = [], [], []
        for index, row in df.iterrows():
            hat_b[round(row['RelativeTime'] * 10) / 10] = df[(df['RelativeTime'] >= row['RelativeTime'] - T_smooth - delta) & (
                        df['RelativeTime'] <= row['RelativeTime'] + T_smooth + delta)].BufferHealth.median()
            # print(round(row['RelativeTime'] * 10) / 10)
        maxTime = round(df['RelativeTime'].max() * 10) / 10
        for index, row in df.iterrows():
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
            Resolutions.append(Resolution)

            mt = (hat_b[t_slope_1] - hat_b[t_slope_2]) / (t_slope_1 - t_slope_2)
            m.append(mt)

            a.append(hat_b[t_slope_1])
            b.append(hat_b[t_slope_2])
            c.append((t_slope_1 - t_slope_2))

            b_t = row['BufferHealth']
            if b_t < BuffWarningThresh:
                BuffWarnings.append(1)
            else:
                BuffWarnings.append(0)

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
            status.append(state)
        df['status'] = status
        df['BuffWarning'] = BuffWarnings
        df['Resolution'] = Resolutions

        df.to_csv(fileid + '_tag.csv', index=None, header=True)
        break
    break


print(Sum, Num)
