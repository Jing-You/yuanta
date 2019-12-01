from testback import Testback
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# S1  假如ask1預測到上漲機率超過BIAS，直接價外買進，bid1漲一點或是有其他人價外買進或是1秒左右平倉。

class Strategy1(Testback):
    def __init__(self, data, buy_bias):
        super(Strategy1, self).__init__(data)
        self.buy_bias = buy_bias
    def can_buy(self):
        if self.possessing == 0 and self._row['nextask1p_label_pred_i'] >= self.buy_bias:
            return True
        else:
            return False
    def can_sell(self):
        if self.possessing == 1 and self._row['nextask1p_label_pred_i']:
            return True
        else:
            return False
    def buy(self):
        self.possessing += 1
        self.possessing_time = 0
        self.num_exchange += 1
        self.cost = self._row['']
    def sell(self):
        pass


if __name__ == "__main__":


    BIAS  = 0.4
    data = pd.read_csv("./data/0828_tick5_timestep40_askbid1p_withProb.csv")
    plt.scatter(np.arange(len(data)), data.loc[:, 'nextask1p_label_pred_i'], label = 'ask1 increase')
    # plt.scatter(np.arange(len(data)), data.loc[:, 'nextask1p_label_pred_d'], label = 'ask1 decrease')
    plt.scatter(np.arange(len(data)), data.loc[:, 'nextbid1p_label_pred_i'], label = 'bid1 increase')
    # plt.scatter(np.arange(len(data)), data.loc[:, 'nextbid1p_label_pred_d'], label = 'bid1 decrease')
    plt.plot(np.arange(len(data)), [BIAS]*len(data))
    plt.legend()
    plt.show()
    print("num of bid1 increase points that prob exceed: %.2f"%(BIAS), np.sum(data.loc[:, 'nextbid1p_label_pred_i'] > BIAS))
    print("num of ask1 increase points that prob exceed: %.2f"%(BIAS), np.sum(data.loc[:, 'nextask1p_label_pred_i'] > BIAS))

    # S1 = Strategy1(
    #     data=data,
    #     buy_bias=0.7)

    # S1.run()
