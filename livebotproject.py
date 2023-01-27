import backtrader as bt
from backtrader import Strategy
from datetime import datetime
import matplotlib.pyplot as plt
import yfinance as yf

class ScalpingStrategy(bt.Strategy):
    params = (
        ('target_profit', 0.01),
        ('stop_loss', 0.01),
        ('ticker', 'AAPL'),
        ('stop_loss_pct', 0.05),
    )

    def __init__(self):
        self.data_close = self.datas[0].close
        self.order = None
        self.stop_loss = None
        self.total_profit = 0.0
        self.total_loss = 0.0
        self.cash = 10000  # Initialize cash with some value

    def next(self):
        try:
            if not self.position:
                self.order = self.buy(size=100)
                self.stop_loss = self.data_close[0] - (self.data_close[0] * self.params.stop_loss_pct)
                self.sell(
                    exectype=bt.Order.Stop,
                    price=self.stop_loss,
                    parent=self.order
                )
                self.sell(
                    exectype=bt.Order.Limit,
                    price=self.data_close[0] + self.params.target_profit,
                    parent=self.order
                )
                self.cash -= self.data_close[0] * 100
                print(f'Cash: {self.cash}')
            elif self.order.isbuy() and self.data_close[0] >= self.order.created.price + self.params.target_profit:
                self.total_profit += self.data_close[0] - self.order.created.price
                self.close()
                self.cash += self.data_close[0] * 100
                print(f'Cash: {self.cash}')
            elif self.order.isbuy() and self.data_close[0] <= self.stop_loss:
                self.total_loss += self.order.created.price - self.data_close[0]
                self.close()
                self.cash += self.data_close[0] * 100
                print(f'Cash: {self.cash}')
            else:
                self.total_profit += self.data.close[0] - self.cost_basis
        except Exception as e:
            print(f'Error: {e}')

    def stop(self):
        profit_factor = self.total_profit / abs(self.total_loss)
        print(f'Profit Factor: {profit_factor}')
        with open("log.txt", "a") as f:
            f.write(f'Profit Factor: {profit_factor}\n')
            f.write(f'Cash: {self.cash}\n')


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(ScalpingStrategy)
    df = yf.download('AAPL', start='2020-01-01', end='2020-12-31')

    data = bt.feeds.PandasData(dataname = df)
   

    cerebro.adddata(data)

    cerebro.run()
    cerebro.plot()
    plt.show()
