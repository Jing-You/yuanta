import datetime as dt
import time
import numpy as np
import pandas as pd
import re
from itertools import chain
from tqdm import tqdm
from multiprocessing import Process

FILEPATH = '0906_out_out.csv'
def labelingclass(df, I080_c = 5):
    # FILE_PATH = "0828_out_out.csv"
    # df = pd.read_csv(FILEPATH)
    # print(FILEPATH)
    # print(df)
    l_nextask1p_label = []
    l_nextbid1p_label = []
    prev_ask1p = 10000
    prev_bid1p = 10000

    for i in tqdm(range(len(df))):
        flag = False

        if df.loc[i, 'is_I080']:
            prev_ask1p = df.loc[i, 'ask1p']

        c = 0

        for j in range(i+1, len(df) - 1):
            if df.loc[j, 'is_I080']:
                j_ask1p = df.loc[j, 'ask1p']
                if j_ask1p > prev_ask1p:
                    l_nextask1p_label.append("increase")
                    flag = True
                    break              
                elif j_ask1p < prev_ask1p:


                    l_nextask1p_label.append("decrease")                
                    flag = True
                    break
                elif j_ask1p == prev_ask1p:
                    c = c + 1
                    if c == I080_c:


                        l_nextask1p_label.append("equal")                
                        flag = True
                        break
        if not flag:
            l_nextask1p_label.append("equal")

    for i in tqdm(range(len(df))):
        flag = False
        c = 0
        if df.loc[i, 'is_I080']:
            prev_bid1p = df.loc[i, 'bid1p']
        for j in range(i+1, len(df) - 1):
            if df.loc[j, 'is_I080']:
                j_bid1p = df.loc[j, 'bid1p']
                if j_bid1p > prev_bid1p:
                    l_nextbid1p_label.append("increase")
                    flag = True
                    break              
                elif j_bid1p < prev_bid1p:
                    l_nextbid1p_label.append("decrease")                
                    flag = True
                    break
                elif j_bid1p == prev_bid1p:
                    c = c + 1
                    if c == I080_c:
                        l_nextbid1p_label.append("equal")                
                        flag = True
                        break
        if not flag:
            l_nextbid1p_label.append("equal")
    df["nextbid1p_label"] = l_nextbid1p_label
    df["nextask1p_label"] = l_nextask1p_label
    return df
    # df.to_csv('test'+FILEPATH+'_label_ask1p_bid1p_catagory.csv', index=False)

# l = ["0822_out_out.csv", "0823_out_out.csv", "0826_out_out.csv", "0827_out_out.csv", "0828_out_out.csv", "0829_out_out.csv", "0902_out_out.csv", "0903_out_out.csv", "0904_out_out.csv", "0905_out_out.csv", "0906_out_out.csv"]


def bid_ask_price_diff2(df):
    l_bid_ask_price_diff2 = []

    for i in tqdm(range(len(df))):
        if df.loc[i, "is_I080"]:
            l_bid_ask_price_diff2.append(np.abs(df.loc[i, 'bid1p'] - df.loc[i, 'ask1p']) > 1)
        elif len(l_bid_ask_price_diff2):
            l_bid_ask_price_diff2.append(l_bid_ask_price_diff2[-1])
        else:
            l_bid_ask_price_diff2.append(False)
    # print(l_bid_ask_price_diff2)
    # df["nextbid1p_label"] = l_nextbid1p_label
    # df["nextask1p_label"] = l_nextask1p_label
    df["bid_ask_price_diff2"] = l_bid_ask_price_diff2
    return df

def bid1q_becomes_two_times(df):
    l_bid1p_become_two_times = [False]
    prev_bid1p = df.loc[0, 'bid1q']
    for i in range(1, len(df)):
        if df.loc[i, 'is_I080']:
            l_bid1p_become_two_times.append(df.loc[i, 'bid1q'] >= 2*prev_bid1p)
            prev_bid1p = df.loc[i, 'bid1q']
        else:
            l_bid1p_become_two_times.append(l_bid1p_become_two_times[-1])
    df["bid1q_becomes_two_times"] = l_bid1p_become_two_times
    return df

def bid1q_becomes_three_times(df):
    l_bid1p_become_three_times = [False]
    prev_bid1p = df.loc[0, 'bid1q']
    for i in range(1, len(df)):
        if df.loc[i, 'is_I080']:
            l_bid1p_become_three_times.append(df.loc[i, 'bid1q'] >= 3*prev_bid1p)
            prev_bid1p = df.loc[i, 'bid1q']
        else:
            l_bid1p_become_three_times.append(l_bid1p_become_three_times[-1])
    df["bid1q_becomes_three_times"] = l_bid1p_become_three_times
    return df

def ask1q_becomes_two_times(df):
    l_ask1p_become_two_times = [False]
    prev_ask1p = df.loc[0, 'ask1q']
    for i in range(1, len(df)):
        if df.loc[i, 'is_I080']:
            l_ask1p_become_two_times.append(df.loc[i, 'ask1q'] >= 2*prev_ask1p)
            prev_ask1p = df.loc[i, 'ask1q']
        else:
            l_ask1p_become_two_times.append(l_ask1p_become_two_times[-1])
    df["ask1q_becomes_two_times"] = l_ask1p_become_two_times
    return df

def ask1q_becomes_three_times(df):
    l_ask1p_become_three_times = [False]
    prev_ask1p = df.loc[0, 'ask1q']
    for i in range(1, len(df)):
        if df.loc[i, 'is_I080']:
            l_ask1p_become_three_times.append(df.loc[i, 'ask1q'] >= 3*prev_ask1p)
            prev_ask1p = df.loc[i, 'ask1q']
        else:
            l_ask1p_become_three_times.append(l_ask1p_become_three_times[-1])
    df["ask1q_becomes_three_times"] = l_ask1p_become_three_times
    return df

def feature_increase(df, feature, bias, newfeaturename):
    l_feature_become_three_times = [False]
    prev_feature = df.loc[0, feature]
    for i in range(1, len(df)):
        if df.loc[i, 'is_I080']:
            l_feature_become_three_times.append(df.loc[i, feature] > bias + prev_feature)
            prev_feature = df.loc[i, feature]
        else:
            l_feature_become_three_times.append(l_feature_become_three_times[-1])
    df[newfeaturename] = l_feature_become_three_times
    return df

def feature_decrease(df, feature, bias, newfeaturename):
    l_feature_become_three_times = [False]
    prev_feature = df.loc[0, feature]
    for i in range(1, len(df)):
        if df.loc[i, 'is_I080']:
            l_feature_become_three_times.append(df.loc[i, feature] < bias + prev_feature)
            prev_feature = df.loc[i, feature]
        else:
            l_feature_become_three_times.append(l_feature_become_three_times[-1])
    df[newfeaturename] = l_feature_become_three_times
    return df

# l = ["0822_out_out.csv", "0823_out_out.csv"]
l = ["0822_out_out.csv", "0823_out_out.csv", "0826_out_out.csv", "0827_out_out.csv", "0828_out_out.csv", "0829_out_out.csv", "0902_out_out.csv", "0903_out_out.csv", "0904_out_out.csv", "0905_out_out.csv", "0906_out_out.csv"]

for file in tqdm(l):
    df = pd.read_csv(file)
    df = feature_increase(df, 'bid1q', 5, 'bid1qincrease5')
    df = feature_increase(df, 'bid1q', 10, 'bid1qincrease10')
    df = feature_increase(df, 'bid1q', 20, 'bid1qincrease20')
    df = feature_increase(df, 'bid1q', 30, 'bid1qincrease30')
    df = feature_increase(df, 'ask1q', 5, 'ask1qincrease5')
    df = feature_increase(df, 'ask1q', 10, 'ask1qincrease10')
    df = feature_increase(df, 'ask1q', 20, 'ask1qincrease20')
    df = feature_increase(df, 'ask1q', 30, 'ask1qincrease30')
    df = feature_decrease(df, 'bid1q', 5, 'bid1qdecrease5')
    df = feature_decrease(df, 'bid1q', 10, 'bid1qdecrease10')
    df = feature_decrease(df, 'bid1q', 20, 'bid1qdecrease20')
    df = feature_decrease(df, 'bid1q', 30, 'bid1qdecrease30')
    df = feature_decrease(df, 'ask1q', 5, 'ask1qdecrease5')
    df = feature_decrease(df, 'ask1q', 10, 'ask1qdecrease10')
    df = feature_decrease(df, 'ask1q', 20, 'ask1qdecrease20')
    df = feature_decrease(df, 'ask1q', 30, 'ask1qdecrease30')
    df = labelingclass(df, 10)
    df = bid_ask_price_diff2(df)
    df = bid1q_becomes_two_times(df)
    df = bid1q_becomes_three_times(df)
    df = ask1q_becomes_two_times(df)
    df = ask1q_becomes_three_times(df)
    df.to_csv('test4_'+file+'_label_ask1p_bid1p_catagory.csv', index=False)