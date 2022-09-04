import ccxt
import time
import pandas as pd
pd.set_option('display.max_rows', None)
import pandas_ta as ta
import numpy as np
from datetime import datetime as dt
import warnings
warnings.filterwarnings('ignore')
import math 
from backtesting import Backtest , Strategy
from backtesting.lib import barssince , crossover
import VXMA as indi

#Bot setting
BOT_NAME = 'VXMA'
#Change Symbol Here
SYMBOL_NAME = 'ETH'
#Change Time Frame Here
TF = '6h'
#API CONNECT
exchange = ccxt.binance()
symboli = SYMBOL_NAME + "/USDT"
exchange.load_markets()
market = exchange.markets[symboli]
print(f"Fetching new bars for {dt.now().isoformat()}")
bars = exchange.fetch_ohlcv(symboli, timeframe=TF, since = None, limit = 2002)
df = pd.DataFrame(bars[:-1], columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

def indicator():
    global df
    indi.indicator(df)
    print(df.tail(500))
    return df.vxma
  
def signalbuy():
    trade = df.buy
    return trade
    
def signalsell():
    trade = df.sell
    return trade

class run_bot(Strategy):

    def init(self):
        super().init()
        self.A2 = self.I(indicator)
        self.A0 = self.I(signalbuy)
        self.A1 = self.I(signalsell)
        
    def next(self) :
        if self.A0:
            self.position.close()
            self.buy(size=1)
        elif self.A1:
            self.position.close()
            self.sell(size=1)

bt = Backtest(df,run_bot,cash = 100000)
stat = bt.run()
# stat = bt.optimize(
        # ema = range(1,200,2),
        # linear = range(1,200,2),
        # smooth = range(1,200,2),
        # atr_p = range(1,50,1),
        # AOL =   range(1,200,2),
        # rsi =   range(1,50,1),
        # maximize = 'Win Rate [%]')
print(stat)
bt.plot()
