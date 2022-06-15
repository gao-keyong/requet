from scapy.all import *
from math import *
import pandas as pd
from tqdm import tqdm

GET_THRESH = 300  # bytes
DOWN_THRESH = 300  # bytes
VIDEO_CHUNK_GETSIZE = 700  # bytes
AUDIO_CHUNK_GETSIZE = 600  # bytes


class Chunk():
    def __init__(self, start_time=0, server_ip='', ttfb=0, download_time=0, slack_time=0, get_size=0, chunk_size=0, type="", protocol=""):
        self.start_time = start_time
        self.server_ip = server_ip
        self.ttfb = ttfb
        self.download_time = download_time
        self.slack_time = slack_time
        self.get_size = get_size
        self.chunk_size = chunk_size
        self.type = type
        self.protocol = protocol

    def __str__(self):
        return f"{self.start_time} {self.ttfb} {self.download_time} {self.slack_time} {self.get_size} {self.chunk_size} {self.type} {self.protocol}"

    def __repr__(self):
        return f"{self.start_time} {self.ttfb} {self.download_time} {self.slack_time} {self.get_size} {self.chunk_size} {self.type} {self.protocol}"


def isUplink(p):
    return p[IP].src.startswith('192.168.')


class ChunkDetection():
    def __init__(self, filename):
        self.__meta_time, self.__end_time, chunks = self.__readPcap(filename)
        self.__df_chunks = self.__getDfChunks(chunks)

    def __detectAV(self, c):
        if abs(c.get_size-VIDEO_CHUNK_GETSIZE) > abs(c.get_size-AUDIO_CHUNK_GETSIZE):
            flag = 0
        else:
            flag = 1
        if c.chunk_size <= 80*1024:
            flag = 2
        return flag

    def __readPcap(self, filename):
        print("Reading pcap file...")
        a = rdpcap(filename)
        meta_time = float(a[0].time)
        end_time = meta_time
        chunk = {}
        chunks = []
        downFlag = {}
        print("Parsing pcap file...")
        for p in tqdm(a):
            if p.haslayer(IP):
                ipSrc = p[IP].src
                ipDst = p[IP].dst
                pLen = p[IP].len
                pHdr = p[IP].ihl*4
                ip_time = float(p.time)
                end_time = ip_time
                if isUplink(p) and pLen-pHdr > GET_THRESH:
                    if ipDst in chunk:
                        chunk[ipDst].slack_time = ip_time - \
                            chunk[ipDst].download_time
                        avFlag = self.__detectAV(chunk[ipDst])
                        if avFlag == 0:
                            # chunk[ipDst].type='a'
                            chunks.append(chunk[ipDst])
                        elif avFlag == 1:
                            # chunk[ipDst].type='v'
                            chunks.append(chunk[ipDst])
                        else:
                            chunk.pop(ipDst)
                            downFlag.pop(ipDst)
                    chunk[ipDst] = Chunk(
                        start_time=ip_time, get_size=pLen-pHdr, server_ip=ipDst)
                    downFlag[ipDst] = False
                elif not isUplink(p) and pLen > DOWN_THRESH:
                    if ipSrc in chunk:
                        if not downFlag[ipSrc]:
                            chunk[ipSrc].ttfb = ip_time
                            downFlag[ipSrc] = True
                        chunk[ipSrc].download_time = ip_time
                        chunk[ipSrc].chunk_size += pLen - pHdr
                        chunk[ipSrc].protocol = p.proto

        for c in chunk.values():
            avFlag = self.__detectAV(c)
            if avFlag == 0:
                # c.type='a'
                chunks.append(c)
            elif avFlag == 1:
                # c.type='v'
                chunks.append(c)
        return meta_time, end_time, chunks

    def __getDfChunks(self, chunks):
        columns = ['start_time', 'type', 'ttfb',
                   'download_time', 'end_time', 'get_size', 'chunk_size']
        df_chunk = pd.DataFrame(columns=columns)
        for c in chunks:
            start_time = c.start_time
            type = c.type
            ttfb = c.ttfb
            end_time = c.download_time
            download_time = end_time - ttfb
            get_size = c.get_size
            chunk_size = c.chunk_size
            s = pd.Series([start_time, type, ttfb, download_time, end_time,
                          get_size, chunk_size], index=columns)
            df_chunk.loc[len(df_chunk)] = s

        av_getsize_gap = df_chunk.get_size.mean()

        for i in range(len(df_chunk)):
            df_chunk.loc[i, 'type'] = 'a' if df_chunk.loc[i,
                                                          'get_size'] < av_getsize_gap else 'v'

        df_chunk.sort_values(by='start_time', inplace=True)
        return df_chunk

    def getFeature(self, epoch_msec):
        t = epoch_msec/1000
        if t < self.__meta_time or t > self.__end_time:
            return None
        s = []
        for w in range(1, 21):
            period = w*10.0
            if t-period < self.__meta_time:
                total_number_of_chunks_v = -1
                avg_chunk_size_v = -1
                download_time_v = -1
                total_number_of_chunks_a = -1
                avg_chunk_size_a = -1
                download_time_a = -1
            else:
                total_number_of_chunks_v = self.__df_chunks[(self.__df_chunks['type'] == 'v') & (
                    self.__df_chunks['end_time'] > t-period) & (self.__df_chunks['start_time'] < t)].shape[0]

                if total_number_of_chunks_v == 0:
                    avg_chunk_size_v = 0
                else:
                    avg_chunk_size_v = self.__df_chunks[(self.__df_chunks['type'] == 'v') & (
                        self.__df_chunks['end_time'] > t-period) & (self.__df_chunks['start_time'] < t)]['chunk_size'].mean()

                download_time_v = self.__df_chunks[(self.__df_chunks['type'] == 'v') & (
                    self.__df_chunks['end_time'] > t-period) & (self.__df_chunks['start_time'] < t)]['download_time'].sum()

                total_number_of_chunks_a = self.__df_chunks[(self.__df_chunks['type'] == 'a') & (
                    self.__df_chunks['end_time'] > t-period) & (self.__df_chunks['start_time'] < t)].shape[0]

                if total_number_of_chunks_a == 0:
                    avg_chunk_size_a = 0
                else:
                    avg_chunk_size_a = self.__df_chunks[(self.__df_chunks['type'] == 'a') & (
                        self.__df_chunks['end_time'] > t-period) & (self.__df_chunks['start_time'] < t)]['chunk_size'].mean()

                download_time_a = self.__df_chunks[(self.__df_chunks['type'] == 'a') & (
                    self.__df_chunks['end_time'] > t-period) & (self.__df_chunks['start_time'] < t)]['download_time'].sum()

            s += [total_number_of_chunks_v, avg_chunk_size_v, download_time_v,
                  total_number_of_chunks_a, avg_chunk_size_a, download_time_a]
        return s
