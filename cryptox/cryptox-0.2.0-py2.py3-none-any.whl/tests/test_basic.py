from context import mk
import pandas as pd

def find_usd_pairs(market):

    currency_pairs = market.get_currency_pairs()

    usd_pairs = []
    usd_currency = 'USDT' if market.currency_pair == 'poloniex' else 'USD'

    for pair in currency_pairs:
        if usd_currency in pair:
            usd_pairs.append(pair)

    return usd_pairs

def get_data(x):
    # create markets
    m = mk.Market(exchange=x)
    # get list of usd pairs
    m_pairs = find_usd_pairs(m)
    # create a pandas series with the list returned from find_usd_pairs
    m_series = pd.Series(m_pairs)
    # export the pandas series to csv files
    m_series.to_csv(path='./output/'+ x +'_usd_pairs.csv', index=False)
    # get 24 hour volume for all pairs that contain usd
    usd_24_hour_volume = m.day_volume(currency_pairs=m_pairs)
    # create dataframe containing 24 hour volume data
    df = pd.DataFrame.from_dict(usd_24_hour_volume, orient='index')
    # replace NaN values with (-)
    df = df.fillna(value='-')
    # output results to csv
    df.to_csv(path_or_buf='./output/'+ x +'_us_24_hour_volume.csv')

get_data('ccex')
get_data('poloniex')