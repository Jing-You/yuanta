import pandas as pd
import numpy as np
# from abc import ABC
import abc
from tqdm import tqdm

"""
S1  假如ask1預測到上漲機率超過BIAS，直接價外買進，n個I080內停損或平倉。
S2  假如ask1預測到上漲機率超過BIAS，低掛多單，看n1個I080內有沒有機會下到空單，成交後，n2個I080內停損或平倉。
S3  假如ask1預測到下跌機率超過BIAS，高掛空單，看n1個I080內有沒有機會下到空單，成交後，n2個I080內停損或平倉。
S4  假如bid1預測到下跌機率超過BIAS，直接價內賣出，n個I080內停損或平倉。
S5  假如bid1預測到下跌機率超過BIAS，高掛空單，看n1個I080內有沒有機會下到空單，成交後，n2個I080內停損或平倉。
S6  假如bid1預測到上漲機率超過BIAS，低掛多單，看n1個I080內有沒有機會下到多單，成交後。n2個I080內停損或平倉。
S7  假如ask1和bid1預測到上漲機率超過BIAS，直接價外買進，n個I080內停損或平倉。
S8  假如ask1和bid1預測到下跌機率超過BIAS，直接價內賣出，n個I080內停損或平倉。
S9  假如ask1預測到下跌機率超過BIAS，直接價內賣出，n個I080內停損或平倉。
S10  假如ask1預測到上漲機率超過BIAS且ask1上漲機率大於ask1下跌機率，直接價外買進，n個I080內停損或平倉。
S11  假如bid1預測到下跌機率超過BIAS且bid1上漲機率小於bid1下跌機率，直接價外買進，n個I080內停損或平倉。
"""

class Testback(abc.ABC):
    def __init__(self, data):
        self.data = data
        self.earnings = []
        self.losings = []
        self.cost = 0
        self.possessing = 0
        self.possessing_time = 0
        self.order_price = 0
        self.num_order = 0
        self.order_time = 0
        self.is_long = False
        self.row = None
        self.lastest_ask1p = self.data.loc[0, 'DayHighPrice']
        self.lastest_bid1p = self.data.loc[0, 'DayLowPrice']
        self.lastest_price = 0
        self.order_cnt = 0
    @abc.abstractmethod
    def can_order(self):
        pass

    @abc.abstractmethod
    def order(self):
        pass

    @abc.abstractmethod
    def can_cancel_order(self):
        pass

    @abc.abstractmethod
    def cancel_order(self):
        pass

    @abc.abstractmethod
    def can_buy(self):
        pass

    @abc.abstractmethod
    def can_sell(self):
        pass

    @abc.abstractmethod
    def buy(self):
        pass

    @abc.abstractmethod
    def sell(self):
        # print("ask1p", self.lastest_ask1p, "bid1p", self.lastest_bid1p, "cost", self.cost, "lastest_price", self.lastest_price,"unrealized_profit", unrealized_profit)
        pass

    def can_make_profit(self):
        return self.unrealized_profit() > 0

    def unrealized_profit(self):
        if self.is_long == True:
            return self.lastest_price - self.cost
        else:
            return - self.lastest_price + self.cost

    def _update(self):
        if self.possessing > 0 and self.row['is_I080']:
            self.possessing_time += 1
        if self.num_order > 0 and self.row['is_I080']:
            self.order_time += 1
    def run(self):
        for i in tqdm(range(len(self.data))):
        # for i in range(len(self.data)):
            self.row = self.data.loc[i]
            if self.row['is_I080'] == True:
                self.lastest_ask1p = self.row['ask1p']
                self.lastest_bid1p = self.row['bid1p']
            elif self.row['is_I020'] == True:
                self.lastest_price = self.row['lastPrice']

            if self.can_order():
                self.order_cnt += 1
                self.order()
            elif self.can_cancel_order():
                self.cancel_order()
            elif self.can_buy():
                # print("# %d"%(i), "can buy")
                self.buy()
            elif self.can_sell():
                # print("# %d"%(i), "can sell")
                # print("before possesing", self.possessing,"possesing_time", self.possessing_time)
                self.sell()
                # print("after possesing, possesing_time", self.possessing, self.possessing_time)

            self._update()
            # if i > 200:
            #     self.show_result()

            #     exit()

        self.show_result()

    def profit_factor(self):
        if len(self.losings) == 0:
            return np.sum(self.earnings)
        else:
            return abs(sum(self.earnings) / sum(self.losings))

    def expected_profit(self):
        return (sum(self.earnings) + sum(self.losings)) / (len(self.earnings) + len(self.losings))

    def num_exchange(self):
        return len(self.earnings) + len(self.losings)

    def winrate(self):
        if len(self.earnings) + len(self.losings) == 0:
            return 0
        else:
            return len(self.earnings) / (len(self.earnings) + len(self.losings))

    def show_result(self):
        print("""\

order_cnt:        %d
num_exchange:       %d
profit_factor:      %.3f
expected_profit:    %.3f
winrate:            %.3f

"""%(self.order_cnt,  self.num_exchange(), self.profit_factor(), self.expected_profit(), self.winrate()))
        # print("earning", self.earnings)
        # print("losing", self.losings)

