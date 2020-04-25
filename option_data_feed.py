from backtrader.feeds import GenericCSVData

class OptionDataFeed(GenericCSVData):
    lines = ('last', 'bid', 'ask', 'impliedvol', 'delta', 'gamma', 'theta', 'vega',)
    params = (
            ('last', 10),
            ('bid', 11),
            ('ask', 12),
            ('impliedvol', 15),
            ('delta', 16),
            ('gamma', 17),
            ('theta', 18),
            ('vega', 19),)
