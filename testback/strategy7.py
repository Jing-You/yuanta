from testback import Testback
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# S7  假如ask1且bid1預測到上漲機率超過BIAS，直接價外買進，n個I080內停損或平倉。

class Strategy7(Testback):
    def __init__(self, data, buy_bias, stop_steps):
        super(Strategy7, self).__init__(data)
        self.buy_bias = buy_bias
        self.is_long = True
        self.stop_steps = stop_steps
    def can_buy(self):
        if self.possessing == 0 and self.row['nextask1p_label_pred_i'] >= self.buy_bias and self.row['nextbid1p_label_pred_i'] >= self.buy_bias:
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
        # print("ask1p", self.lastest_ask1p, "bid1p", self.lastest_bid1p, "cost", self.cost, "unrealized_profit", unrealized_profit)
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
    # plt.scatter(np.arange(len(data)), data.loc[:, 'nextask1p_label_pred_i'], label = 'ask1 increase')
    # # plt.scatter(np.arange(len(data)), data.loc[:, 'nextask1p_label_pred_d'], label = 'ask1 decrease')
    # plt.scatter(np.arange(len(data)), data.loc[:, 'nextbid1p_label_pred_i'], label = 'bid1 increase')
    # # plt.scatter(np.arange(len(data)), data.loc[:, 'nextbid1p_label_pred_d'], label = 'bid1 decrease')
    # plt.plot(np.arange(len(data)), [BIAS]*len(data))
    # plt.legend()
    # plt.show()
    # print("num of bid1 increase points that prob exceed: %.2f"%(BIAS), np.sum(data.loc[:, 'nextbid1p_label_pred_i'] > BIAS))
    # print("num of ask1 increase points that prob exceed: %.2f"%(BIAS), np.sum(data.loc[:, 'nextask1p_label_pred_i'] > BIAS))


    for stop_steps in [5, 10, 15, 20, 25]:
        print("stop_steps:  ", stop_steps)
        S7 = Strategy7(
            data=data,
            buy_bias=BIAS,
            stop_steps=stop_steps)
        S7.run()
