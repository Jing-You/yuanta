from testback import Testback
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# S10  假如ask1預測到上漲機率超過BIAS且ask1上漲機率大於ask1下跌機率，直接價外買進，n個I080內停損或平倉。

class Strategy10(Testback):
    def __init__(self, data, buy_bias, stop_steps):
        super(Strategy10, self).__init__(data)
        self.buy_bias = buy_bias
        self.is_long = True
        self.stop_steps = stop_steps
    def can_buy(self):
        if self.possessing == 0 and self.row['nextask1p_label_pred_i'] >= self.buy_bias\
            and self.row['nextask1p_label_pred_i'] >= self.row['nextask1p_label_pred_d']:
            return True
        else:
            return False

    def can_sell(self):
        return (self.possessing_time > self.stop_steps or self.can_make_profit()) and self.possessing > 0

    def buy(self):
        self.possessing += 1
        self.possessing_time = 0
        self.cost = self.lastest_ask1p

    def sell(self):
        self.possessing -= 1
        unrealized_profit = self.unrealized_profit()
        if unrealized_profit > 0:
            self.earnings.append(unrealized_profit)
        else:
            self.losings.append(unrealized_profit)
    
    def can_order(self):
        return False

    def order(self):
        pass

    def can_cancel_order(self):
        return False
    def cancel_order(self):
        pass

if __name__ == "__main__":


    BIAS  = 0.4
    data = pd.read_csv("./data/0828_tick5_timestep40_askbid1p_withProb.csv")

    for stop_steps in [5, 10, 15, 20, 25]:
        print("stop_steps:  ", stop_steps)
        S10 = Strategy10(
            data=data,
            buy_bias=BIAS,
            stop_steps=stop_steps)
        S10.run()
