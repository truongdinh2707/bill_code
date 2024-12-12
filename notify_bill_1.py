import datetime as dt
import requests
import pandas as pd
import talib
import ta

def calc_signal(symbol = 'ETHUSDT', timeframe = '15m', limit = 200):
    # Fetch from klines so we don't need an API exchange connection
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={timeframe}&limit={limit}'

    response = requests.get(url)
    ohlcv = response.json()

    # Convert the data to a pandas DataFrame
    data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data.set_index('timestamp', inplace=True)
    data['close'] = data['close'].astype(float)

    # Calculate Momentum over 14 hours based on last 200 hours of data
    data['momentum'] = talib.MOM(data['close'], timeperiod=14)
    current_momentum = data['momentum'].iloc[-1]

    # Calculate ADX, +DI and -DI
    adx = talib.ADX(data['high'], data['low'],
                    data['close'], timeperiod=72)
    plus_di = talib.PLUS_DI(
        data['high'], data['low'], data['close'], timeperiod=72)
    minus_di = talib.MINUS_DI(
        data['high'], data['low'], data['close'], timeperiod=72)

    # Establish market conditions using ADX and Momentum
    current_adx = adx.iloc[-1]
    current_plus_di = plus_di.iloc[-1]
    current_minus_di = minus_di.iloc[-1]

    # Sideways if ADX is less than 20 and momentum is between -200 and 200
    market_condition = ''
    if current_adx < 20 and current_momentum < 200 and current_momentum > -200:
        market_condition = 'Sideways'
    # Upward if ADX is 20 or greater and momentum is 200 or greater
    elif current_plus_di > current_minus_di and current_momentum >= 200:
        market_condition = 'Upward'
    # Downward if ADX is 20 or greater and momentum is -200 or less
    elif current_plus_di < current_minus_di and current_momentum <= -200:
        market_condition = 'Downward'

    # Calculate close price
    current_close = data['close'].iloc[-1]

    # Calculate Bollinger upper and lower bands
    bollinger_indicator = ta.volatility.BollingerBands(
        data['close'])
    upper_band = bollinger_indicator.bollinger_hband()
    lower_band = bollinger_indicator.bollinger_lband()

    # Strategy: Increase position size as ADX / Momentum increases
    # Only trade when price moves outside Bollinger bands

    # Sidways market and price drops below lower Bollinger band
    if market_condition == 'Sideways' and current_close < lower_band.iloc[-1]:
        position_size = .05  # Set position size to 5% for sideways buy / sell orders
        action = 'Buy'
        signal = 'Sideways Oversold (Buy with 5% position)'
    # Sidways market and price rises above upper Bollinger band
    elif market_condition == 'Sideways' and current_close > upper_band.iloc[-1]:
        position_size = .05
        action = 'Sell'
        signal = 'Sideways Overbought (Sell with 5% position)'
    # Downward market and price drops below lower Bollinger band, raise position size to 10%
    elif market_condition == 'Downward' and current_close < lower_band.iloc[-1]:
        position_size = .10
        action = 'Sell'
        signal = 'Overbought (Sell)'
    # Upward market and price rises above upper Bollinger band, raise position size to 10%
    elif market_condition == 'Upward' and current_close > upper_band.iloc[-1]:
        position_size = .10
        action = 'Sell'
        signal = 'Overbought (Sell)'
    # Else hold
    else:
        action = 'Hold'
        signal = 'Neutral'
        
    message = f"{dt.datetime.now().strftime('%Y-%m-%d %H:%M')} {symbol}\nMarket Condition: {market_condition}\nAction: {action}\nSignal: {signal}\nClose Price: {current_close}\nLower Band: {round(lower_band.iloc[-1], 2)}\nUpper Band: {round(upper_band.iloc[-1], 2)}"
    return message

def notify_signal(bot_token = 'AAFnKBMH6wyrF2LSR7ZjF_elByf3XiJAFUo', chat_id = '1088035988', message = 'SIGNAL FOR BILL'):
    try:
        url = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=markdown&text=' + message
        response = requests.get(url)
        response_json = response.json()
        if not response_json.get('ok'):
            print(f"Error sending notification.")
    except Exception as e:
        print(f"Error sending notification: {e}")
        
if __name__ == "__main__":
    # Telegram Config
    bot_token = 'AAFnKBMH6wyrF2LSR7ZjF_elByf3XiJAFUo'
    chat_id = '1088035988'
    # Fetch Historical Data from Binance / Binance US / Your Exchange
    symbols = ['BTCUSDT', 'ETHUSDT']
    timeframe = '15m'
    limit = 200

    for symbol in symbols:
        mess = calc_signal(symbol, timeframe, limit)
        print(mess)
        # Send Notify to Telegram
        notify_signal(bot_token, chat_id, mess)
        # End Loop
        print('------------------------------------------------')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    