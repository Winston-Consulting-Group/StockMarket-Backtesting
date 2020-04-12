from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime
import os.path
import sys
import backtrader as bt
import backtrader.analyzers as btanalyzers
import backtrader.feeds as btfeeds
import backtrader.strategies as btstrats
import pyfolio as pf
from strategies.crossover_9_21_with_swing import Crossover9_21WithSwing

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    cerebro.addstrategy(Crossover9_21WithSwing, printlog=False)

    datapath = './data/test_data.txt'
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2010, 1, 1),
        todate=datetime.datetime(2014, 12, 31),
        reverse=False)

    cerebro.adddata(data)
    cerebro.broker.setcash(1000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    cerebro.broker.setcommission(commission=0.0)
    cerebro.run()
    cerebro.plot()

