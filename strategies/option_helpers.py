import pandas as pd
from datetime import datetime
import sys

class OptionHelpers:
    def __init__(self, all_data):
        self.all_data = all_data

    def update_data(self, all_data):
        self.all_data = all_data

    def get_chain_by_name(self, name):
        return self.all_data[name]

    def get_series_by_criteria(self, type, strike, expiration):
        series_id = type + "_" + strike + "_" + expiration
        if series_id in self.all_data:
            return self.all_data[series_id]

    def get_closest_expiration(self, days_until_expiration, current_date, strike=None):
        best_expiration = None
        best_days_from = sys.maxsize
        for key in self.all_data:
            all_chain_dates = [datetime.fromordinal(int(date)).date() for date in self.all_data[key].datetime]
            if current_date in all_chain_dates:
                (cur_type, cur_strike, cur_expiration) = key.split('_')
                if strike != None and cur_strike != strike:
                    continue
                cur_expiration_dt = datetime.strptime(cur_expiration, '%m/%d/%Y')
                difference = abs((cur_expiration_dt.date() - current_date).days - days_until_expiration)
                if difference < best_days_from:
                    best_days_from = difference
                    best_expiration = cur_expiration
        return best_expiration

    def get_series_by_delta(self, delta, expiration, type):
        #print("delta: " + str(delta) + " expiration: " + str(expiration) + " type:" + str(type))
        best_series = ""
        best_delta_difference = sys.maxsize
        for key in self.all_data:
            (cur_type, cur_strike, cur_expiration) = key.split('_')
            if cur_type == type and cur_expiration == expiration:
                delta_difference = abs(delta - self.all_data[key].delta)
                if delta_difference < best_delta_difference:
                    best_series = key
                    best_delta_difference = delta_difference
        #print(best_series)
        return best_series



