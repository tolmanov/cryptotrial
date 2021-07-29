from dataclasses import dataclass

from btc.conn.bin import client
from datetime import datetime
import pandas as pd

data = client.get_historical_klines("BTCUSDT", client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")

@dataclass
class Balance:
    btc: float
    usd: float

def toDateTime(timestamp):
    return datetime.fromtimestamp(timestamp / 1000)

def toTimeStamp(dt):
    return 1000 * int(datetime.timestamp(dt))

def get_processed_data():
    columns = ["OpenTime", "Open", "High", "Low", "Close", "Volume", "CloseTime", "QuoteAssetVolume",
               "NumberOfTrades", "TakerBuyBaseAssetVolume", "TakerBuyQuoteAssetVolume", "CanBeIgnored", ]
    df = pd.DataFrame(data, columns=columns)
    for col in ["OpenTime", "CloseTime"]:
        df[col] = df[col].apply(toDateTime)
    for col in ["Open", "Close", "High", "Low", "Volume", "QuoteAssetVolume"]:
        df[col] = df[col].apply(float)
    return df


def get_spread(cur_price, eps=15):
    """eps in basis points"""
    return cur_price*(1-eps/10000), cur_price*(1+eps/10000)

def calc_pnl(data):
    pass

def run_algo(df):
    x = Balance(btc=0, usd=0)
    df = df.set_index("OpenTime")
    # prices = df[["Open", "High", "Low"]].T.values
    prices = df[["Open", "High", "Low", "Close"]]
    prices['Bid'] = prices["Open"].apply(lambda x: get_spread(x)[0])
    prices['Ask'] = prices["Open"].apply(lambda x: get_spread(x)[1])
    prices['Buy'] = (prices['Bid'] > prices['Low']) & (prices['Bid'] < prices['High'])
    prices['Sell'] = (prices['Ask'] > prices['Low']) & (prices['Ask'] < prices['High'])
    prices['PnL'] = 0
    for data in prices.itertuples(index=True):
        if data.Buy:
            x.btc += 1
            x.usd -= data.Bid
        if data.Sell:
            x.btc -= 1
            x.usd += data.Ask
        prices.loc[data.Index, 'PnL'] = x.btc * data.Close + x.usd
    print(f"Balance: {x}")
    print(f"PnL={x.btc * prices.Close.iloc[-1] + x.usd}")
    return prices
    # tt = prices.apply(calc_pnl, axis=1)




if __name__ == '__main__':
    df = get_processed_data()
    run_algo(df)

