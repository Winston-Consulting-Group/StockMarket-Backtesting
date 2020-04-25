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
from .option_helpers import OptionHelpers

class DeltaSpread(bt.Strategy):
    params = (
        ('printlog', False),
    )

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.count = 0
        self.dataclose = self.datas[0].close
        self.order_pending = None
        self.buy_price = None
        self.buy_commission = None
        self.current_position = False
        self.option_helpers = OptionHelpers(self.dnames)
        self.option_chain = None
        self.option_chain_key = None
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
        elif order.status in [order.Canceled]:
            self.log('Order Canceled')
        elif order.status in [order.Margin]:
            self.log('Order Margin problem')
        elif order.status in [order.Rejected]:
            self.log('Order Rejected')
        self.order_pending = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def default_next(self):
        self.log('Close, %.2f' % self.dataclose[0])
        self.option_helpers.update_data(self.dnames)
        if not self.current_position:
            chain_date = self.option_helpers.get_closest_expiration(60, self.datas[0].datetime.date(0))
            self.option_chain_key = self.option_helpers.get_series_by_delta(0.2, chain_date, "call")
            self.option_chain = self.option_helpers.get_chain_by_name(self.option_chain_key)
        (cur_type, cur_strike, cur_expiration) = self.option_chain_key.split('_')


        if self.order_pending:
            return
        if not self.current_position:
            if self.simple_moving_avg_indicator_9[0] < self.simple_moving_avg_indicator_21[0]:
                self.count = 0
                self.current_position = True
                self.log('SELL CREATE, %.2f' % self.option_chain.close[0])
                self.order_pending = self.sell(data=self.option_chain)
        else:
            cur_expiration_dt = datetime.datetime.strptime(cur_expiration, '%m/%d/%Y')
            time_to_expiry = cur_expiration_dt.date() - self.datas[0].datetime.date(0)
            if time_to_expiry.days < 5 or self.dataclose[0] >= float(cur_strike):
                self.current_position = False
                self.log('BUY CREATE, %.2f' % self.option_chain.close[0])
                self.order_pending = self.buy(data=self.option_chain)

    def prenext(self):
        self.default_next()

    def next(self):
        self.default_next()

    def stop(self):
        self.log('(MA Period ?) Ending Value %.2f' %
                 (self.broker.getvalue()), doprint=True)


