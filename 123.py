import ccxt, time, os
from datetime import datetime

apiKey = os.getenv('API_KEY')
secret = os.getenv('API_SECRET')
exchange = ccxt.mexc({'apiKey': apiKey, 'secret': secret})

def get_balance():
    balance = exchange.fetch_balance()
    return balance['total']['USDT']

def get_positions():
    balance = exchange.fetch_balance()
    positions = []
    for symbol in balance['total']:
        amount = balance['total'][symbol]
        if symbol != 'USDT' and amount > 0:
            positions.append(symbol)
    return positions

def get_symbols():
    markets = exchange.load_markets()
    usdt_pairs = [symbol for symbol in markets if '/USDT' in symbol and markets[symbol]['active']]
    return sorted(usdt_pairs, key=lambda x: -markets[x]['info'].get('volume', 0))[:8]

def smart_trade():
    usdt = get_balance()
    if usdt < 3.6:
        print("資金不足，暫停...")
        return
    symbols = get_symbols()
    per_trade = usdt / len(symbols)
    for symbol in symbols:
        try:
            print(f"[{datetime.now()}] 嘗試買入 {symbol}")
            order = exchange.create_market_buy_order(symbol, per_trade)
            print(f"已買入：{order}")
            time.sleep(2)
        except Exception as e:
            print(f"{symbol} 買入失敗：{e}")
            continue

def cleanup_other_tokens():
    positions = get_positions()
    symbols = get_symbols()
    for pos in positions:
        symbol = f"{pos}/USDT"
        if symbol not in symbols:
            try:
                amount = exchange.fetch_balance()['total'][pos]
                print(f"清倉非策略幣：{symbol}")
                exchange.create_market_sell_order(symbol, amount)
                time.sleep(2)
            except Exception as e:
                print(f"{symbol} 清倉失敗：{e}")
                continue

while True:
    try:
        cleanup_other_tokens()
        smart_trade()
        time.sleep(60)
    except Exception as e:
        print("主邏輯錯誤：", e)
        time.sleep(10)
