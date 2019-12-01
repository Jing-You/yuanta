import pandas as pd
import numpy as np
# from abc import ABC
import abc
from tqdm import tqdm
"""
S1  假如ask1預測到上漲機率超過BIAS，直接價外買進，bid1漲一點或是有其他人價外買進或是1秒左右平倉。
S2  假如ask1預測到下跌機率超過BIAS，高掛空單，看有沒有機會下到空單。收到I080 or 此價位退至ask2則抽單。
S3  假如bid1預測到下跌機率超過BIAS，直接價內賣出，跌一點或1秒左右平倉。
S4  假如bid1預測到上漲機率超過BIAS，高掛多單，看有沒有機會下到多單。收到I080 or 此價位退至bid2則抽單。
S5  假如ask1且bid1預測到上漲機率超過BIAS，直接價外買進，bid1漲一點或是有其他人價外買進或是1秒左右平倉。
S6  假如ask1且bid1預測到下跌機率超過BIAS，直接價內賣出，ask1跌一點或是有其他人價外買進或是1秒左右平倉。
S7  假如ask1預測到上漲機率超過BIAS，低掛多單，bid1漲一點或是有其他人價外買進或是1秒左右平倉。
S8  假如bid1預測到下跌機率超過BIAS，高掛空單，bid1漲一點或是有其他人價外買進或是1秒左右平倉。

"""

class Testback(abc.ABC):
    def __init__(self, data):
        self._data = data
        self.earning = 0
        self.losing = 0
        self.cost = 0
        self.possessing = 0
        self.possessing_time = 0
        self.num_exchange = 0
        self._row = None
    @abc.abstractmethod
    def can_buy(self):
        pass
    @abc.abstractmethod
    def can_sell(self):
        pass
    def profit_factor(self):
        pass
    @abc.abstractmethod
    def buy(self):
        pass
    @abc.abstractmethod
    def sell(self):
        pass

    def run(self):
        for i in tqdm(range(len(self._data))):
            self._row = self._data.loc[i]
            if self.can_buy():
                self.buy()
            if self.can_sell():
                self.sell()