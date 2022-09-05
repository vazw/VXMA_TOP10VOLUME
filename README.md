#VXMA BOT TRADING STRATEGY BY VAZ.
```
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
|- 			
|-v2.0
|- Avoid Large Position amount
|- Input Max margin use
|- แจ้งเตือนยอดเงินทุกชั่วโมง \ Hourly notify
|-v.TOP10 = ระบบจะเลือกคู่เทรดที่มีวอลุ่มสูงสุดให้ และถ้าชอบตัวไหนเป็นพิเศษสามารถเพิ่มให้บอทได้ที่ไฟล์ config ได้เลย
|- 			+ ระบบแจ้งเตือนทุกเช้า เมื่อแท่งวันปิด
|-      +บอทจะใช้ leverage ที่เคยตั้งไว้ หรือสูงสุด
|-v.TOP10 = This Strategy will pick top 10 trading volume form exchange and use VXMA indicator for buy sell signall
|-    + there is notify everyday's morning at 07:00 am
|-  Please use with your own risk.
```
##สามารถตั้งค่าได้ดังต่อไปนี้นี้ \ this is this config.
```
[KEY]
time_delay = 60
API_KEY = Binance_api_key
API_SECRET = Binance_secret_key
LINE_TOKEN = Line_Notiytoken
[STAT]
OPEN_LONG = True เปิด False ปิด
OPEN_SHORT = True เปิด False ปิด
USE_TP = True  เปิด False ปิด
USE_SL = True เปิด False ปิด
Tailing_SL = True  เปิด False ปิด
Free_Balance = $100 จำนวนเงินที่บอทสามารถใช้ได้
MIN_BALANCE = $50 บอทจะยกเลิกการเข้า order หากเงินต่ำกว่า MIN_BALANCE 
LOST_PER_TARDE = 0.5 ถ้าอยากใช้ % ให้ใช้ตัวเลขธรรมดา 	 LOST_PER_TARDE = 5 คือจำนวนเงินที่จะเสีย หากไปถึงจุด SL
MAX_Margin_USE = $5 จำนวน Margin สูงสุดต่อไม้ ที่บอทจะเปิดได้
RiskReward_TP1 = 3 RiskReward คำนวนระยะห่างจากจุด SL อัตโนมัด
RiskReward_TP2 = 4.5
Percent_TP1 = 50 จำนวน % ที่จะออก TP
Percent_TP2 = 50
Pivot_lookback = 50 ระยะแท่งเทียนการตรวจหา swinghigh low ย้อนหลังเพื่อหาจุด SL
[BOT]
SYMBOL_NAME = BTC,XMR คู่เทรดที่สนใจ
Blacklist = ADA,1000SHIB,LUNA คู่ที่เกลียด
LEVERAGE = 125 lerverage สูงสุดที่บอทจะใช้
TF = 6h timeframe ที่จะเล่น
[TA]
ATR_Period = 12
ATR_Mutiply = 1.6
RSI_Period = 25
EMA_Fast = 30
SUBHAG_LINEAR = 30
SMOOTH = 30
Andean_Oscillator = 30
[weigh100]
RSI_W = 20 กำหนดน้ำหนักในการประเมินเทรน
ADX_W = 20 โดยบวกลบกันให้ได้ 100
VXMA_W = 40 ไม่มีผลกับการเข้า order
MACD_W = 10 เพราะสัญญาณซื้อขายจะมาจาก VXMA เท่านั้น
SMA200_W = 10
```
##LOST_PER_TARDE  
```
ถ้าอยากใช้ % ให้ใช้ตัวเลขธรรมดา 	 LOST_PER_TARDE = 5
ถ้าอยากใช้ $ ให้ใช้ $ นำหน้า		LOST_PER_TARDE = $10
```
###Donate XMR : 87tT3DZqi4mhGuJjEp3Yebi1Wa13Ne6J7RGi9QxU21FkcGGNtFHkfdyLjaPLRv8T2CMrz264iPYQ2dCsJs2MGJ27GnoJFbm
