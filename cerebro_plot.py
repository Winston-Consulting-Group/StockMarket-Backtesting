from __future__ import (absolute_import, division, print_function, unicode_literals)
import datetime
import os.path
import sys
import backtrader as bt
import backtrader.analyzers as btanalyzers
import backtrader.feeds as btfeeds
import backtrader.strategies as btstrats
import pyfolio as pf
import datetime
import backtrader.feeds as btfeed
import pandas as pd
from strategies.crossover_9_21_with_swing import Crossover9_21WithSwing
import warnings; warnings.simplefilter('ignore')

all_option_data_october = pd.read_csv('./data/options_data/all_options_data.csv', parse_dates=True, index_col=7, nrows=100000)

underlying = bt.feeds.YahooFinanceCSVData(
    dataname='./data/SPY.csv',
    fromdate=datetime.datetime(2018, 10, 1),
    todate=datetime.datetime(2020, 10, 31),
    reverse=False)

def create_data_feed(pd_data, series_name):
    option_feed = bt.feeds.PandasData(
        dataname=pd_data,
        fromdate=datetime.datetime(2018, 10, 1),
        todate=datetime.datetime(2018, 10, 31),
        high=None,
        low=None,
        open=8,
        close=10,
        volume=None,
        openinterest=None,
        name=series_name)
    return option_feed

def add_options_data():
    option_types = ['call', 'put']
    option_expirations = all_option_data_october['expiration'].unique()
    option_strikes = all_option_data_october['strike'].unique()
    for type in option_types:
        is_type = all_option_data_october['type'] == 'call'
        filtered_by_type = all_option_data_october[is_type]
        for expiration in option_expirations:
            is_expiration = filtered_by_type['expiration'] == expiration
            filtered_by_type_expiration = filtered_by_type[is_expiration]
            for strike in option_strikes:
                is_strike = filtered_by_type_expiration['strike'] == strike
                filtered_by_type_expiration_strike = filtered_by_type_expiration[is_strike]
                if not filtered_by_type_expiration_strike.shape[0] >= 10:
                    series_name = type + "_" + str(strike) + "_" + str(expiration)
                    single_option_data = create_data_feed(filtered_by_type_expiration_strike, series_name)
                    cerebro.adddata(single_option_data)
                    return

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(Crossover9_21WithSwing, printlog=True)

    #cerebro.adddata(underlying)
    add_options_data()
    cerebro.broker.setcash(100000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    cerebro.broker.setcommission(commission=0.0)

    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
    results = cerebro.run()
    cerebro.plot()
