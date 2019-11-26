import datetime as dt
import time
import numpy as np
import pandas as pd
import re
from itertools import chain

FILE_PATH = input("FILE_PATH:")
START_TIME = dt.datetime(1, 1, 1, 8, 45, 0)
START_TIMESTAMP = START_TIME.utcfromtimestamp(0)
PROD_ID = input("PROD_ID:")

i020_feature = ['lastQty', 'lastPrice', 'totalMatchQty', 'totalMatchBuy', 'totalMatchSell']


i080_feature = [
    "bid5p", "bid5q", "bid4p", "bid4q", "bid3p", "bid3q", "bid2p", "bid2q",
    "bid1p", "bid1q", "ask1p", "ask1q", "ask2p", "ask2q", "ask3p", "ask3q",
    "ask4p", "ask4q", "ask5p", "ask5q"
]





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
                    if not c % 100:
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