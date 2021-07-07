# refer https://towardsdatascience.com/a-comprehensive-guide-to-downloading-stock-prices-in-python-2cd93ff821d4
# the best one so far.

import pandas as pd
from yahoofinancials import YahooFinancials

assets = ['QQQ', 'GLD', 'VO', 'VB', 'VTI', 'SPY', 'TLT', 'SHY']
yahoo_financials = YahooFinancials(assets)

data = yahoo_financials.get_historical_price_data(start_date='2000-01-01',
                                                  end_date='2020-12-31',
                                                  time_interval='daily')  # 'weekly'

for symbol in assets:
    df = pd.DataFrame(data[symbol]['prices'])
    df = df.drop('date', axis=1).set_index('formatted_date')
    # df.head()
    df.reindex(columns=['open', 'high', 'low', 'close', 'adjclose', 'volume']) \
        .to_csv(f'../data/{symbol}.csv')  # works
