#VXMA BOT TRADING STRATEGY BY VAZ.
What's this version do?
|-v.0.1 	= Start from VXMA Pinescript Tradingview.
|-v.1.0.0	= Start Deploy Fully-Function
|-v.1.0.1	= Fix order params and add TP/SL Order
|-v.1.1		= Fix config.ini found '\n'
|-V.1.2		= BUY AND SELL SWITCH 
|- 			+TP AND SL SWITCH 
|- 			+TP2
|- 			+Try Improve BUY SELL condition and detail
|-v.1.2.1 = fix TP formula.
|-v.1.2.2 = TailingStopMarket order fully-function.
|- 			-คำนวน callbackRate for Tailing SL อัตโนมัติ
|-			-activationPrice : ตั้งไว้เมื่อราคาไปถึง RR = 1
|-v.TOP10 = ระบบจะเลือกคู่เทรดที่มีวอลุ่มสูงสุดให้ และถ้าชอบตัวไหนเป็นพิเศษสามารถเพิ่มให้บอทได้ที่ไฟล์ config ได้เลย
|- 			+ ระบบแจ้งเตือนทุกเช้า เมื่อแท่งวันปิด
|NEXT ???
|- Re-entry when SL and Trend did not changed
|- Tuning

สามารถตั้งค่าได้ดังต่อไปนี้นี้
[KEY]
API_KEY = 
API_SECRET = 
LINE_TOKEN = 
[STAT]
OPEN_LONG = True
OPEN_SHORT = True
USE_TP = True
USE_SL = True
Tailing_SL = True
MIN_BALANCE = $50
LOST_PER_TARDE = 10 
RiskReward_TP1 = 3
RiskReward_TP2 = 4.5
Percent_TP1 = 50
Percent_TP2 = 50
Pivot_lookback = 50
[BOT]
SYMBOL_NAME = BTC,ETH,XMR
LEVERAGE = 125 ถ้า leverage เกิน บอทจะใช้ leverage ที่เคยตั้งไว้โดยอัตโนมัติ
TF = 15m  สามรถเลือกเล่นได้ timeframe เดียว 
[TA]
ATR_Period = 12
ATR_Mutiply = 1.6
RSI_Period = 25
EMA_Fast = 30
SUBHAG_LINEAR = 30
SMOOTH = 30
Andean_Oscillator = 30


ในหัวข้อ [BOT] และ [TA] สามารถตั้งได้หลาย ๆ ค่าด้วย คอมม่า  (  , ) 
โดยจะต้องเรียงลำดับตามที่ต้องการ  (leverage 1,2,3,4 = symbol 1,2,3,4)
LOST_PER_TARDE  
ถ้าอยากใช้ % ให้ใช้ตัวเลขธรรมดา 	LOST_PER_TARDE = 5
ถ้าอยากใช้ $ ให้ใช้ $ นำหน้า	LOST_PER_TARDE = $10

Donate XMR : 87tT3DZqi4mhGuJjEp3Yebi1Wa13Ne6J7RGi9QxU21FkcGGNtFHkfdyLjaPLRv8T2CMrz264iPYQ2dCsJs2MGJ27GnoJFbm
