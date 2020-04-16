from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime
import os.path
import sys
import backtrader as bt
import backtrader.analyzers as btanalyzers
import backtrader.feeds as btfeeds
import backtrader.strategies as btstrats
from strategies.crossover_9_21_with_swing import Crossover9_21WithSwing

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    cerebro.addstrategy(Crossover9_21WithSwing, printlog=True)

    datapath = './data/SPY.csv'
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2018, 10, 1),
        todate=datetime.datetime(2020, 3, 31),
        reverse=False)

    options_chain = bt.feeds.GenericCSVData(
        dataname='./data/options_data/monthly_data/SPY_20181001_to_20181031.csv',
        fromdate=datetime.datetime(2018, 10, 1),
        todate=datetime.datetime(2020, 10, 31),
        dtformat=('%m/%d/%Y'),
        datetime=7,
        time=-1,
        high=-1,
        low=-1,
        open=9,
        close=11,
        volume=12,
        openinterest=13,
        reverse=False)

    cerebro.adddata(data)
    cerebro.adddata(options_chain)
    cerebro.broker.setcash(1000000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    cerebro.broker.setcommission(commission=0.0)
    cerebro.run()
    cerebro.plot()

