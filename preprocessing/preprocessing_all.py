import datetime as dt
import time
import numpy as np
import pandas as pd
import re
from itertools import chain
from tqdm import tqdm
from multiprocessing import Process
# FILE_PATH = input("FILE_PATH:")


def preprocessing(FILE_PATH, I080_c = 5):
    # FILE_PATH = "0828_out.txt"
    START_TIME = dt.datetime(1, 1, 1, 8, 45, 0)
    START_TIMESTAMP = START_TIME.utcfromtimestamp(0)
    PROD_ID = "TXFI9"
    # PROD_ID = input("PROD_ID:")

    i080_feature = [
        "bid5p", "bid5q", "bid4p", "bid4q", "bid3p", "bid3q", "bid2p", "bid2q",
        "bid1p", "bid1q", "ask1p", "ask1q", "ask2p", "ask2q", "ask3p", "ask3q",
        "ask4p", "ask4q", "ask5p", "ask5q"
    ]

    i020_feature = ['lastQty', 'lastPrice', 'totalMatchQty', 'totalMatchBuy', 'totalMatchSell']
    i021_feature = ['DayHighPrice', 'DayLowPrice']

    def filter_i080(s, prod_id):
        if s[:4] == 'I080' and s[5:10] == prod_id and s[10] != '/':
            rb_position = 0
            lb_position = 0
            Seq_position = 0
            for i in range(len(s) - 4):
                if s[i] == ']':
                    rb_position = i
                elif s[i] == '[':
                    lb_position = i
                elif s[i] == 'S':
                    Seq_position = i
                    break
            curtime = list(map(int, s[lb_position + 1:rb_position - 5].split(':')))
            curtime = dt.datetime(1, 1, 1, curtime[0], curtime[1], curtime[2],
                                curtime[3] * 1000)
            if curtime < START_TIME:
                return False
            relativetime = (curtime - START_TIME).total_seconds()
            relativetime = relativetime if relativetime >= 0 else (
                relativetime + dt.timedelta(days=1)).total_seconds()
            s = s[rb_position + 1:Seq_position]
            s = s.replace('(', ',')
            s = s.replace(')', ',')
            s = s.replace('|', '')
            s = s.replace(' ', '')
            s = s[:-1]
            s = list(map(float, s.split(',')))
            for i in range(0, 20, 2):
                s[i] = s[i] / 100
            dic = dict(zip(i080_feature, s))
            dic["relativetime"] = relativetime
            dic["is_I080"] = 1
            return dic
        return False


    def filter_i020(s, prod_id):
        if s[:4] == 'I020' and s[5:10] == prod_id and s[10] != '/':
            curtime = list(map(int, s[19:31].split(':')))
            curtime = dt.datetime(1, 1, 1, curtime[0], curtime[1], curtime[2], curtime[3]*1000)
            if curtime < START_TIME:
                return False
            relativetime = (curtime - START_TIME).total_seconds()
            relativetime = relativetime if relativetime >= 0 else (
                relativetime + dt.timedelta(days=1)).total_seconds()
            comp_re = re.compile("lastQty=(\d+) lastPrice=(\d+) totalMatchQty=(\d+) totalMatchBuy=(\d+) totalMatchSell=(\d+)")
            i020_data = comp_re.findall(s[38:])
            i020_data = list(chain.from_iterable(i020_data))
            i020_data = list(map(int, i020_data))
            i020 = dict(zip(i020_feature, i020_data))
            i020['relativetime'] = relativetime
            i020['lastPrice'] = i020['lastPrice']/100
            i020['is_I020'] = 1
            return i020
        return False

    def filter_i021(s, prod_id):
        if s[:4] == 'I021' and s[5:10] == prod_id and s[10] != '/':
            curtime = list(map(int, s[19:31].split(':')))
            curtime = dt.datetime(1, 1, 1, curtime[0], curtime[1], curtime[2], curtime[3]*1000)
            if curtime < START_TIME:
                return False
            relativetime = (curtime - START_TIME).total_seconds()
            relativetime = relativetime if relativetime >= 0 else (
                relativetime + dt.timedelta(days=1)).total_seconds()
            comp_re = re.compile("DayHighPrice=(\d+) DayLowPrice=(\d+)")
            i021_data = comp_re.findall(s[38:])
            i021_data = list(chain.from_iterable(i021_data))
            i021_data = list(map(int, i021_data))
            i021 = dict(zip(i021_feature, i021_data))
            i021['relativetime'] = relativetime
            i021['DayHighPrice'] = i021['DayHighPrice']/100
            i021['DayLowPrice'] = i021['DayLowPrice']/100
            i021['is_I021'] = 1
            return i021
        return False

    with open(FILE_PATH, 'r', encoding='utf8', errors='ignore') as f:
        l = f.readline()
        df = pd.DataFrame(columns=["is_I020",
                        "is_I021",
                        "is_I080",
                        "relativetime",
                        "lastQty",
                        "lastPrice",
                        "totalMatchQty",
                        "totalMatchBuy",
                        "totalMatchSell",
                        "DayHighPrice",
                        "DayLowPrice",
                        "bid5p",
                        "bid5q",
                        "bid4p",
                        "bid4q",
                        "bid3p",
                        "bid3q",
                        "bid2p",
                        "bid2q",
                        "bid1p",
                        "bid1q",
                        "ask1p",
                        "ask1q",
                        "ask2p",
                        "ask2q",
                        "ask3p",
                        "ask3q",
                        "ask4p",
                        "ask4q",
                        "ask5p",
                        "ask5q"])
        c = 0
        DayHighPrice = 10000
        DayLowPrice = 10000
        rows = []
        while l and c < 300000:
            filterlist = [filter_i020,filter_i021,filter_i080]
            row = None
            # print(l)
            for filter in filterlist:
                row = filter(l, PROD_ID)
                if row:
                    if filter == filter_i021:
                        DayHighPrice = row['DayHighPrice']
                        DayLowPrice = row['DayLowPrice']
                    else:
                        c += 1
                        if not c % 2000:
                            print(c)
                        row['DayHighPrice'] = DayHighPrice
                        row['DayLowPrice'] = DayLowPrice
                        row = pd.Series(row)
                        rows.append(pd.DataFrame(row).T)
            l = f.readline()
        print("readfinish")
        df = pd.concat([df]+[row for row in rows], axis=0, ignore_index=True)
        df = df.fillna(0)
        df.to_csv(FILE_PATH[:-4] + "_out.csv", index=False)





    FILE_PATH = FILE_PATH[:-4] + "_out.csv"
    # FILE_PATH = "0828_out_out.csv"
    df = pd.read_csv(FILEPATH)
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
        # if i < 50:
        #     print(df.loc[i])

        for j in range(i+1, len(df) - 1):
            if df.loc[j, 'is_I080']:
                j_ask1p = df.loc[j, 'ask1p']
                if j_ask1p > prev_ask1p:
                    # if i < 50:
                    #     print("increase","i",i ,"j",j, "prev_ask1p", prev_ask1p, "j_ask1p", j_ask1p)
                    l_nextask1p_label.append("increase")
                    flag = True
                    break              
                elif j_ask1p < prev_ask1p:

                    # if i < 50:
                    #     print("decrease","i",i ,"j",j, "prev_ask1p", prev_ask1p, "j_ask1p", j_ask1p)

                    l_nextask1p_label.append("decrease")                
                    flag = True
                    break
                elif j_ask1p == prev_ask1p:
                    c = c + 1
                    if c == I080_c:

                        # if i < 50:
                        #     print("equal","i",i ,"j",j, "prev_ask1p", prev_ask1p, "j_ask1p", j_ask1p)

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
    df.to_csv('test'+FILEPATH+'_label_ask1p_bid1p_catagory.csv', index=False)

l = ["0822_out.txt", "0823_out.txt", "0826_out.txt", "0827_out.txt", "0828_out.txt", "0829_out.txt", "0902_out.txt", "0903_out.txt", "0904_out.txt", "0905_out.txt", "0906_out.txt"]
for f in tqdm(l):
    print(f)
    preprocessing(f, I080_c = 5)

