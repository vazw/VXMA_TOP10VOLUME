from posixpath import split
from typing import List
from urllib.parse import MAX_CACHE_SIZE
import ccxt
import time
import pandas as pd
pd.set_option('display.max_rows', None)
import numpy as np
from line_notify import LineNotify 
import configparser
from datetime import datetime as dt
import warnings
warnings.filterwarnings('ignore')
import os
from tabulate import tabulate
import logging
import mplfinance as mplf
import VXMA as Indi

seconds = time.time()
local_time = time.ctime(seconds)
logging.basicConfig(filename='log.log', format='%(asctime)s - %(message)s', level=logging.INFO)
print('VXMA bot (Form Tradingview)By Vaz.')
print('Donate XMR : 87tT3DZqi4mhGuJjEp3Yebi1Wa13Ne6J7RGi9QxU21FkcGGNtFHkfdyLjaPLRv8T2CMrz264iPYQ2dCsJs2MGJ27GnoJFbm')
#call config
config = configparser.ConfigParser()
config.read('config.ini')
#key setting
API_KEY = config['KEY']['API_KEY']
API_SECRET = config['KEY']['API_SECRET']
LINE_TOKEN = config['KEY']['LINE_TOKEN']
notify = LineNotify(LINE_TOKEN)
#Bot setting
USELONG = config['STAT']['Open_LONG']
USESHORT = config['STAT']['Open_SHORT']
USETP = config['STAT']['USE_TP']
USESL = config['STAT']['USE_SL']
Tailing_SL = config['STAT']['Tailing_SL']
MIN_BALANCE = config['STAT']['MIN_BALANCE']
RISK = config['STAT']['LOST_PER_TARDE']
TPRR1 = config['STAT']['RiskReward_TP1']
TPRR2 = config['STAT']['RiskReward_TP2']
TPPer = int(config['STAT']['Percent_TP1'])
TPPer2 = int(config['STAT']['Percent_TP2'])
Pivot = config['STAT']['Pivot_lookback']
#STAT setting
SYMBOL_NAME = list((config['BOT']['SYMBOL_NAME'].split(",")))
LEVERAGE = config['BOT']['LEVERAGE']
TF = config['BOT']['TF']
tf = TF
leverage = int(LEVERAGE)
BOT_NAME = 'VXMA_SMART'
# API CONNECT
exchange = ccxt.binance({
"apiKey": API_KEY,
"secret": API_SECRET,
'options': {
'defaultType': 'future'
},
'enableRateLimit': True
})

exchange.precisionMode = ccxt.DECIMAL_PLACES

Sside = 'BOTH'
Lside = 'BOTH'
messmode = ''
min_balance = 50

currentMODE = exchange.fapiPrivate_get_positionside_dual()
if currentMODE['dualSidePosition']:
    print('You are in Hedge Mode')
    Sside = 'SHORT'
    Lside = 'LONG'
    messmode = 'You are in Hedge Mode'
else:
    print('You are in One-way Mode')
    messmode = 'You are in One-way Mode'

if MIN_BALANCE[0]=='$':
    min_balance=float(MIN_BALANCE[1:len(MIN_BALANCE)])
    print("MIN_BALANCE=",min_balance)

wellcome = 'VXMA Bot Started :\n' + messmode + '\nTrading pair : ' + str(SYMBOL_NAME) + '\nTimeframe : ' + str(TF) + '\nLeverage : ' + str(LEVERAGE) +'\nBasic Setting\n----------\nRisk : ' + str(RISK) + '\nRisk:Reward : ' + str(TPRR1) + '\nBot Will Stop Entry when balance < ' + str(min_balance) + '\nGOODLUCK'
notify.send(wellcome)

def get_symbol():
    symbols = pd.DataFrame()
    syms = []
    print('fecthing Symbol of Top 10 Volume...')
    market = exchange.fetchTickers(params={'type':'future'})
    if len(SYMBOL_NAME) > 0:
        for i in SYMBOL_NAME:
            symbo = i +'/USDT'
            syms.append(symbo)
    for x,y in market.items()    :
        if y['symbol'][len(y['symbol'])-4:len(y['symbol'])] == "USDT":
            symbols = symbols.append(y , ignore_index=True)
    symbols = symbols.set_index('symbol')
    symbols['datetime'] = pd.to_datetime(symbols['timestamp'], unit='ms', utc=True).map(lambda x: x.tz_convert('Asia/Bangkok'))
    symbols = symbols.sort_values(by=['quoteVolume'],ascending=False)
    symbols.drop(['timestamp','high','low','average'],axis=1,inplace=True)
    symbols.drop(['bid','bidVolume','ask','askVolume'],axis=1,inplace=True)
    symbols.drop(['vwap','open','baseVolume','info'],axis=1,inplace=True)
    symbols.drop(['close','previousClose','datetime'],axis=1,inplace=True)
    symbols = symbols.head(10)
    newsym = []
    if len(syms) > 0:
        for symbol in syms:
            newsym.append(symbol)
    for symbol in symbols.index:
        newsym.append(symbol)
    print(tabulate(symbols, headers = 'keys', tablefmt = 'grid'))
    newsym = list(dict.fromkeys(newsym))
    print(f'Interested : {newsym}')
    return newsym
#clearconsol
def clearconsol():
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls') 
    return

def candle(df,symbol):
    data = df.tail(365)
    rcs = {"axes.labelcolor":"none",
            "axes.spines.left": False,
            "axes.spines.right": False,
            "axes.titlesize": '20'}
    color = mplf.make_marketcolors(up='green',down='red',volume='inherit',wick='white',edge='white')    
    s = mplf.make_mpf_style(base_mpf_style='nightclouds', rc=rcs ,marketcolors=color,y_on_right=True)
    vxmal = mplf.make_addplot(data.vxma,secondary_y=False,color='yellow')
    mplf.plot(data,type='candle',title=symbol,addplot=vxmal, style=s,volume=True,savefig='candle.png',tight_layout=True)
    notify.send(f'info : {symbol}',image_path=('./candle.png'))
    return 

#Position Sizing
def buysize(df,balance,symbol):
    last = len(df.index) - 1
    freeusd = float(balance['free']['USDT'])
    swinglow = Indi.swinglow(df,Pivot)
    if RISK[0]=='$' :
        risk = float(RISK[1:len(RISK)])
    else :
        percent = float(RISK)
        risk = (percent/100)*freeusd
    amount = abs(risk  / (df['Close'][last] - float(swinglow)))
    qty_precision = exchange.markets[symbol]['precision']['amount']
    lot = round(amount,qty_precision)
    return lot

def sellsize(df,balance,symbol):
    last = len(df.index) - 1
    freeusd = float(balance['free']['USDT'])
    swinghigh = Indi.swinghigh(df,Pivot)
    if RISK[0]=='$' :
        risk = float(RISK[1:len(RISK)])
    else :
        percent = float(RISK)
        risk = (percent/100)*freeusd
    amount = abs(risk  / (float(swinghigh) - df['Close'][last]))
    qty_precision = exchange.markets[symbol]['precision']['amount']
    lot = round(amount,qty_precision)
    return lot

#TP with Risk:Reward    
def RRTP(df,symbol,direction,step):
    if direction :
        swinglow = Indi.swinglow(df,Pivot)
        if step == 1 :
            ask = float(exchange.fetchBidsAsks([symbol])[symbol]['info']['askPrice'])
            target = ask *(1+((ask-float(swinglow))/ask)*float(TPRR1))
        if step == 2 :
            ask = float(exchange.fetchBidsAsks([symbol])[symbol]['info']['askPrice'])
            target = ask *(1+((ask-float(swinglow))/ask)*float(TPRR2))
    else :
        swinghigh = Indi.swinghigh(df,Pivot)
        if step == 1 :
            bid = float(exchange.fetchBidsAsks([symbol])[symbol]['info']['bidPrice'])
            target = bid *(1-((swinghigh-bid)/bid)*float(TPRR1))
        if step == 2 :
            bid = float(exchange.fetchBidsAsks([symbol])[symbol]['info']['bidPrice'])
            target = bid *(1-((swinghigh-bid)/bid)*float(TPRR2))    
    return target

def RR1(df,symbol,direction):
    if direction :
        swinglow = Indi.swinglow(df,Pivot)
        ask = float(exchange.fetchBidsAsks([symbol])[symbol]['info']['askPrice'])
        target = ask *(1+((ask-float(swinglow))/ask)*1)
    else :
        swinghigh = Indi.swinghigh(df,Pivot)
        bid = float(exchange.fetchBidsAsks([symbol])[symbol]['info']['bidPrice'])
        target = bid *(1-((float(swinghigh)-bid)/bid)*1)
    return target

def callbackRate(df):
    swinghigh = Indi.swinghigh(df,Pivot)
    swinglow = Indi.swinglow(df,Pivot)
    rate = round((float(swinghigh)-float(swinglow))/swinghigh*100,1)
    if rate > 5 :
        rate = 5
    elif rate < 0.1 :
        rate = 0.1
    return rate 

#OpenLong=Buy
def OpenLong(df,balance,symbol,lev):
    print('Entry Long')
    amount = float(buysize(df,balance,symbol))
    ask = float(exchange.fetchBidsAsks([symbol])[symbol]['info']['askPrice'])
    try:
        exchange.set_leverage(lev,symbol)
    except:
        time.sleep(1)
        lever = exchange.fetch_positions_risk([symbol])
        for x in range(len(lever)):
            if (lever[x]['symbol']) == symbol:
                leverrage = round(lever[x]['leverage'],0)
                print(leverrage)
                exchange.set_leverage(int(leverrage),symbol)
                break
    free = float(balance['free']['USDT'])
    amttp1 = amount*(TPPer/100)
    amttp2 = amount*(TPPer2/100)
    swinglow = Indi.swinglow(df,Pivot)
    if free > min_balance :
        try:
            order = exchange.createMarketOrder(symbol,'buy',amount,params={'positionSide':Lside})
            logging.info(order)
        except ccxt.InsufficientFunds as e:
            logging.debug(e)
            return    
        if USESL :
            if currentMODE['dualSidePosition']:
                orderSL         = exchange.create_order(symbol,'stop','sell',amount,float(swinglow),params={'stopPrice':float(swinglow),'triggerPrice':float(swinglow),'positionSide':Lside})
                if Tailing_SL :
                    ordertailingSL  = exchange.create_order(symbol, 'TRAILING_STOP_MARKET','sell',amount,params ={'activationPrice':float(RR1(df,symbol,True)) ,'callbackRate': float(callbackRate(df)),'positionSide':Lside})
            else:
                orderSL         = exchange.create_order(symbol,'stop','sell',amount,float(swinglow),params={'stopPrice':float(swinglow),'triggerPrice':float(swinglow),'reduceOnly': True ,'positionSide':Lside})
                if Tailing_SL :
                    ordertailingSL  = exchange.create_order(symbol, 'TRAILING_STOP_MARKET','sell',amount,params ={'activationPrice':float(RR1(df,symbol,True)) ,'callbackRate': float(callbackRate(df)),'reduceOnly': True ,'positionSide':Lside})
            if Tailing_SL :
                logging.info(ordertailingSL)
            logging.info(orderSL)
        if USETP :
            orderTP  = exchange.create_order(symbol,'TAKE_PROFIT_MARKET','sell',amttp1,float(RRTP(df,symbol,True,1)),params={'stopPrice':float(RRTP(df,symbol,True,1)),'triggerPrice':float(RRTP(df,symbol,True,1)),'positionSide':Lside})
            orderTP2 = exchange.create_order(symbol,'TAKE_PROFIT_MARKET','sell',amttp2,float(RRTP(df,symbol,True,2)),params={'stopPrice':float(RRTP(df,symbol,True,2)),'triggerPrice':float(RRTP(df,symbol,True,2)),'positionSide':Lside})
            logging.info(orderTP)
            logging.info(orderTP2)
        time.sleep(1)
        margin=ask*amount/lev
        total = float(balance['total']['USDT'])
        msg ="BINANCE:\n" + "BOT         : " + BOT_NAME + "\nCoin        : " + symbol + "\nStatus      : " + "OpenLong[BUY]" + "\nAmount    : " + str(amount) +"("+str(round((amount*ask),2))+" USDT)" + "\nPrice        :" + str(ask) + " USDT" + str(round(margin,2))+  " USDT"+ "\nBalance   :" + str(round(total,2)) + " USDT"
    else :
        msg = "MARGIN-CALL!!!\nยอดเงินต่ำกว่าที่กำหนดไว้  : " + str(min_balance) + '\nยอดปัจจุบัน ' + str(round(free,2)) + ' USD\nบอทจะทำการยกเลิกการเข้า Position ทั้งหมด' 
    notify.send(msg)
    candle(df,symbol)
    clearconsol()
    return

#OpenShort=Sell
def OpenShort(df,balance,symbol,lev):
    print('Entry Short')
    amount = float(buysize(df,balance,symbol))
    bid = float(exchange.fetchBidsAsks([symbol])[symbol]['info']['bidPrice'])
    try:
        exchange.set_leverage(lev,symbol)
    except:
        time.sleep(1)
        lever = exchange.fetch_positions_risk([symbol])
        for x in range(len(lever)):
            if (lever[x]['symbol']) == symbol:
                leverrage = round(lever[x]['leverage'],0)
                print(leverrage)
                exchange.set_leverage(int(leverrage),symbol)
                break
    free = float(balance['free']['USDT'])
    amttp1 = amount*(TPPer/100)
    amttp2 = amount*(TPPer2/100)
    swinghigh = Indi.swinghigh(df,Pivot)
    if free > min_balance :
        try:
            order = exchange.createMarketOrder(symbol,'sell',amount,params={'positionSide':Sside})
            logging.info(order)
        except ccxt.InsufficientFunds as e:
            logging.debug(e)
            return        
        if USESL :
            if currentMODE['dualSidePosition']:
                orderSL         = exchange.create_order(symbol,'stop','buy',amount,float(swinghigh),params={'stopPrice':float(swinghigh),'triggerPrice':float(swinghigh),'positionSide':Sside})
                if Tailing_SL :
                    ordertailingSL  = exchange.create_order(symbol,'TRAILING_STOP_MARKET','buy',amount,params ={'activationPrice':float(RR1(df,symbol,False)) ,'callbackRate': float(callbackRate(df)),'positionSide':Sside})
            else :
                orderSL         = exchange.create_order(symbol,'stop','buy',amount,float(swinghigh),params={'stopPrice':float(swinghigh),'triggerPrice':float(swinghigh),'reduceOnly': True ,'positionSide':Sside})
                if Tailing_SL :
                    ordertailingSL  = exchange.create_order(symbol,'TRAILING_STOP_MARKET','buy',amount,params ={'activationPrice':float(RR1(df,symbol,False)) ,'callbackRate': float(callbackRate(df)),'reduceOnly': True ,'positionSide':Sside})
            if Tailing_SL :    
                logging.info(ordertailingSL)
            logging.info(orderSL)
        if USETP :
            orderTP = exchange.create_order(symbol,'TAKE_PROFIT_MARKET','buy',amttp1,float(RRTP(df,symbol,False,1)),params={'stopPrice':float(RRTP(df,symbol,False,1)),'triggerPrice':float(RRTP(df,symbol,False,1)),'positionSide':Sside})
            logging.info(orderTP)
            orderTP2 = exchange.create_order(symbol,'TAKE_PROFIT_MARKET','buy',amttp2,float(RRTP(df,symbol,False,2)),params={'stopPrice':float(RRTP(df,symbol,False,2)),'triggerPrice':float(RRTP(df,symbol,False,2)),'positionSide':Sside})
            logging.info(orderTP2)
        time.sleep(1)
        margin=bid*amount/lev
        total = float(balance['total']['USDT'])
        msg ="BINANCE:\n" + "BOT         : " + BOT_NAME + "\nCoin        : " + symbol + "\nStatus      : " + "OpenShort[SELL]" + "\nAmount    : " + str(amount) +"("+str(round((amount*bid),2))+" USDT)" + "\nPrice        :" + str(bid) + " USDT" + str(round(margin,2))+  " USDT"+ "\nBalance   :" + str(round(total,2)) + " USDT"
    else :
        msg = "MARGIN-CALL!!!\nยอดเงินต่ำกว่าที่กำหนดไว้  : " + str(min_balance) + '\nยอดปัจจุบัน ' + str(round(free,2)) + ' USD\nบอทจะทำการยกเลิกการเข้า Position ทั้งหมด' 
    notify.send(msg)
    candle(df,symbol)
    clearconsol()
    return
#CloseLong=Sell
def CloseLong(df,balance,symbol,status):
    print('Close Long')
    amount = float(status["positionAmt"][len(status.index) -1])
    upnl = float(status["unrealizedProfit"][len(status.index) -1])
    bid = float(exchange.fetchBidsAsks([symbol])[symbol]['info']['bidPrice'])
    order = exchange.createMarketOrder(symbol,'sell',amount,params={'positionSide':Lside})
    time.sleep(1)
    logging.info(order)
    total = float(balance['total']['USDT'])
    msg ="BINANCE:\n" + "BOT         : " + BOT_NAME + "\nCoin        : " + symbol + "\nStatus      : " + "CloseLong[SELL]" + "\nAmount    : " + str(amount) +"("+str(round((amount*bid),2))+" USDT)" + "\nPrice        :" + str(bid) + " USDT" + "\nRealized P/L: " + str(round(upnl,2)) + " USDT"  +"\nBalance   :" + str(round(total,2)) + " USDT"
    notify.send(msg)
    candle(df,symbol)
    clearconsol()
    return
#CloseShort=Buy
def CloseShort(df,balance,symbol,status):
    print('Close Short')
    amount = abs(float(status["positionAmt"][len(status.index) -1] if status["symbol"][len(status.index) -1] == symbol else status["positionAmt"][len(status.index) -1]))
    upnl = float(status["unrealizedProfit"][len(status.index) -1] if status["symbol"][len(status.index) -1] == symbol else status["positionAmt"][len(status.index) -1])
    ask = float(exchange.fetchBidsAsks([symbol])[symbol]['info']['askPrice'])
    order = exchange.createMarketOrder(symbol,'buy',amount,params={'positionSide':Sside})
    time.sleep(1)
    logging.info(order)
    total = float(balance['total']['USDT'])
    msg ="BINANCE:\n" + "BOT         : " + BOT_NAME + "\nCoin        : " + symbol + "\nStatus      : " + "CloseShort[BUY]" + "\nAmount    : " + str(amount) +"("+ str(round((amount*ask),2))+" USDT)" + "\nPrice        :" + str(ask) + " USDT" + "\nRealized P/L: " + str(round(upnl,2)) + " USDT"  +"\nBalance   :" + str(round(total,2)) + " USDT"
    notify.send(msg)
    candle(df,symbol)
    clearconsol()
    return

def feed(symbol,timeframe):
    bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since = None, limit = 1002)
    df = pd.DataFrame(bars[:-1], columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True).map(lambda x: x.tz_convert('Asia/Bangkok'))
    df = df.set_index('timestamp')
    score , df = Indi.indicator(df)
    print(df.tail(2))
    print(f"Benchmarking new bars for {symbol , timeframe , dt.now().isoformat()}")
    is_in_Long = False
    is_in_Short = False
    is_in_position = False
    last = len(df.index) -1
    balance = exchange.fetch_balance()
    positions = balance['info']['positions']
    current_positions = [position for position in positions if float(position['positionAmt']) != 0]
    status = pd.DataFrame(current_positions, columns=["symbol", "entryPrice","positionSide", "unrealizedProfit", "positionAmt", "initialMargin" ,"isolatedWallet"])   
    previous = len(status.index)-1
    print('checking current position on hold...')
    print(tabulate(status, headers = 'keys', tablefmt = 'grid'))
    posim = symbol.replace('/','')
    amt = 0
    print("checking for buy and sell signals")
    for i in status.index:
        if status['symbol'][i] == posim:
            amt = float(status['positionAmt'][i])
            print(amt)
        # NO Position
        if not status.empty and amt != 0 :
            is_in_position = True
        else: 
            is_in_position = False
            is_in_Short = False
            is_in_Long = False
        # Long position
        if is_in_position and amt > 0  :
            is_in_Long = True
            is_in_Short = False
        # Short position
        if is_in_position and amt < 0  :
            is_in_Short = True
            is_in_Long = False  
        if df['buy'][last] :
            print("changed to Bullish, buy")
            if is_in_Short :
                CloseShort(df,balance,symbol,status)
            if not is_in_Long and USELONG:
                exchange.cancel_all_orders(symbol)
                time.sleep(1)
                OpenLong(df,balance,symbol,leverage)
                is_in_Long = True
            else:
                print("already in position, nothing to do")
        if df['sell'][last]:
            print("changed to Bearish, Sell")
            if is_in_Long :
                CloseLong(df,balance,symbol,status)
            if not is_in_Short and USESHORT :
                exchange.cancel_all_orders(symbol)
                time.sleep(1)
                OpenShort(df,balance,symbol,leverage)
                is_in_Short = True
            else:
                print("already in position, nothing to do")
    return score , df
  
def main():
    symbolist = get_symbol()
    totalscore = []
    for symbol in symbolist:
        if local_time[11:-8] == '07:00':
            get_tasks()
            break
        score, df = feed(symbol,tf)
        score = round(score,1)
        print(symbol,f" Score : {score}/10")
        totalscore.append(f'{symbol} : {score}/10')
    return totalscore

def get_dailytasks():
    symbolist = get_symbol()
    totalscore = []
    for symbol in symbolist:
        score, df = feed(symbol,'1d')
        score = round(score,1)
        print(symbol,f" Score : {score}/10")
        totalscore.append(f'{symbol} : {score}/10')
        candle(df,symbol)
    msg = str(totalscore).replace(",","\n")
    notify.send(f'คู่เทรดที่น่าสนใจในวันนี้\n{msg}')    
    return totalscore

def get_tasks():
    responses = get_dailytasks()
    for response in responses:
        print(response)

if __name__ == "__main__":
    while True:
        main()

            