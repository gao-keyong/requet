import glob

import pandas as pd

# dataset_list = ['A', 'B1', 'B2', 'C', 'D']
dataset_list = ['']

colnames = ['RelativeTime', 'PacketsSent', 'PacketsReceived', 'BytesSent', 'BytesReceived']

######
# NET INFO
######
NUM_OF_NET_INFO = 26
# Then, we have some NetworkInfo, each one related to the connection of the client to
# a server (only the top NUM_OF_NET_INFO are represented)

for interval in range(0, NUM_OF_NET_INFO):
    int_str = str(interval)
    network_info = ['IPSrc' + int_str, 'IPDst' + int_str, 'Protocol' + int_str,
                    'PacketsSent' + int_str, 'PacketsReceived' + int_str,
                    'BytesSent' + int_str, 'BytesReceived' + int_str]
    colnames.extend(network_info)

######
# PLAYBACK INFO
######
playback_info_event = ['Buffering', 'Paused', 'Playing', 'CollectData'];
colnames.extend(playback_info_event);

playback_info_generic = ['EpochTime',
                         'StartTime', 'PlaybackProgress', 'Length'];
colnames.extend(playback_info_generic);

playback_info_quality = ['UnlabelledQuality', 'q144p', 'q240p',
                         'q360p', 'q480p', 'q720p', 'q1080p', 'q1440p', 'q2160p'];
colnames.extend(playback_info_quality);

playback_info_health_and_progress = ['BufferHealth',
                                     'BufferProgress', 'BufferValid'];
colnames.extend(playback_info_health_and_progress)

# The correct number of columns should be calculated as follows
NUM_OF_INTERVAL_INFO_COLS = 5
NUM_OF_NET_INFO_COLS = 7

NUM_OF_GENERIC_PLAYBACK_EVENT_COLS = 4
NUM_OF_GENERIC_PLAYBACK_COLS = 4
NUM_OF_PLAYBACK_QUALITY_COLS = 9
NUM_OF_PLAYBACK_HEALTH_AND_PROGRESS_COLS = 3
NUM_OF_PLAYBCAK_COLS = NUM_OF_GENERIC_PLAYBACK_EVENT_COLS + \
                       NUM_OF_GENERIC_PLAYBACK_COLS + \
                       NUM_OF_PLAYBACK_QUALITY_COLS + NUM_OF_PLAYBACK_HEALTH_AND_PROGRESS_COLS

NUM_COLS = NUM_OF_INTERVAL_INFO_COLS + \
           NUM_OF_NET_INFO_COLS * NUM_OF_NET_INFO + NUM_OF_PLAYBCAK_COLS

if len(colnames) != NUM_COLS:
    raise Exception("Expected number of columns ", NUM_COLS, ", constructed ",
                    len(colnames))


for dataset_to_use in dataset_list:
    datasets_folder = "ReaquestTestSet10"
    dataset_folder = datasets_folder + '/' + dataset_to_use + '/MERGED_FILES/'
    files = glob.glob(dataset_folder + 'baseline_*_merged.txt')

    print("Files found in folder : ", dataset_folder, ":", files)
    i = 1
    for file in files:
        outfilename = file + ".csv"
        fin = open(file, "rt")
        fout = open(outfilename, "wt")
        # From https://pythonexamples.org/python-replace-string-in-file/
        for line in fin:
            fout.write(line.replace('[', '').replace(']', ''))
        fin.close()
        fout.close()
        df = pd.read_csv(outfilename, header=None)
        df.columns = colnames
        # df = df[df['CollectData'] != 1]  # !why
        # df = df[df['UnlabelledQuality'] != 1]
        print("Concatenating (", i, "/", len(files), "): ", file)
        df.to_csv('test_data' + dataset_to_use + '/' + file.split('/')[-1].split('.')[0] + '.csv', index=False)
        # df.to_csv('data/' + dataset_to_use + '/' + file.split('.')[0] + '_full.csv', index=None, header=True)
        i = i + 1
