from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime
import os.path
import sys
import backtrader as bt

class CrossoverStrategy(bt.Strategy):
    params = (
        ('printlog', False),
    )

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order_pending = None
        self.buy_price = None
        self.buy_commission = None
        self.simple_moving_avg_indicator_9 = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=9)
        self.simple_moving_avg_indicator_21 = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=21)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                self.buy_price = order.executed.price
                self.buy_commission = order.executed.comm
            else:
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order_pending = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])
        if self.order_pending:
            return
        if not self.position:
            if self.simple_moving_avg_indicator_9[0] > self.simple_moving_avg_indicator_21[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order_pending = self.buy()
        else:
            if self.simple_moving_avg_indicator_21[0] > self.simple_moving_avg_indicator_9[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order_pending = self.sell()

    def stop(self):
        self.log('(MA Period ?) Ending Value %.2f' %
                 (self.broker.getvalue()), doprint=True)


if __name__ == '__main__':
    cerebro = bt.Cerebro()

    cerebro.addstrategy(CrossoverStrategy, printlog=True)

    datapath = './test_data.txt'
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2000, 1, 1),
        todate=datetime.datetime(2010, 12, 31),
        reverse=False)

    cerebro.adddata(data)
    cerebro.broker.setcash(1000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    cerebro.broker.setcommission(commission=0.0)
    cerebro.run()
    cerebro.plot()
