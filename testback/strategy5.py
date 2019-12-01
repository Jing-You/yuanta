from testback import Testback
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# S5  假如bid1預測到下跌機率超過BIAS，高掛空單，看n1個I080內有沒有機會下到空單，成交後，n2個I080內停損或平倉。

class Strategy5(Testback):
    def __init__(self, data, order_bias, order_steps, stop_steps):
        super(Strategy5, self).__init__(data)
        self.order_bias = order_bias
        self.is_long = False
        self.stop_steps = stop_steps
        self.order_steps = order_steps

    def can_buy(self):
        return self.lastest_price >= self.order_price

    def can_sell(self):
        return (self.possessing_time > self.stop_steps or self.can_make_profit()) and self.possessing > 0

    def buy(self):
        self.possessing += 1
        self.possessing_time = 0
        self.cost = self.lastest_price

    def sell(self):
        self.possessing -= 1
        unrealized_profit = self.unrealized_profit()
        if unrealized_profit > 0:
            self.earnings.append(unrealized_profit)
        else:
            self.losings.append(unrealized_profit)

    def can_order(self):
        return self.num_order == 0 and self.row['nextask1p_label_pred_d'] >= self.order_bias

    def order(self):
        self.order_price = self.lastest_ask1p
        self.num_order += 1

    def can_cancel_order(self):
        return self.order_time > self.order_steps

    def cancel_order(self):
        self.num_order = 0


if __name__ == "__main__":

    BIAS = 0.4
    data = pd.read_csv("./data/0828_tick5_timestep40_askbid1p_withProb.csv")
    order_steps = 5

    # plt.scatter(np.arange(len(data)), data.loc[:, 'nextask1p_label_pred_i'], label = 'ask1 increase')
    # # plt.scatter(np.arange(len(data)), data.loc[:, 'nextask1p_label_pred_d'], label = 'ask1 decrease')
    # plt.scatter(np.arange(len(data)), data.loc[:, 'nextbid1p_label_pred_i'], label = 'bid1 increase')
    # # plt.scatter(np.arange(len(data)), data.loc[:, 'nextbid1p_label_pred_d'], label = 'bid1 decrease')
    # plt.plot(np.arange(len(data)), [BIAS]*len(data))
    # plt.legend()
    # plt.show()
    # print("num of bid1 increase points that prob exceed: %.2f"%(BIAS), np.sum(data.loc[:, 'nextbid1p_label_pred_i'] > BIAS))
    # print("num of ask1 increase points that prob exceed: %.2f"%(BIAS), np.sum(data.loc[:, 'nextask1p_label_pred_i'] > BIAS))
    for order_steps in [5, 10, 15]:
        for stop_steps in [5, 10]:
            print("order_steps:  ", order_steps)
            print("stop_steps:  ", stop_steps)
            S5 = Strategy5(
                data=data,
                order_bias=BIAS,
                order_steps = order_steps,
                stop_steps = stop_steps)
            S5.run()
            print("-"*20)
