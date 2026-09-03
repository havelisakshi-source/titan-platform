from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import random
from datetime import datetime
import json

app = FastAPI(title="TITAN Trading Platform", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# NIFTY 50 stocks
NIFTY_50 = [
    "RELIANCE", "TCS", "HDFC", "INFY", "HINDUNILVR", 
    "ICICIBANK", "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK",
    "LT", "WIPRO", "HCLTECH", "ASIANPAINT", "AXISBANK",
    "TITAN", "SUNPHARMA", "ULTRACEMCO", "BAJFINANCE", "NTPC",
    "ONGC", "POWERGRID", "TATAMOTORS", "TATASTEEL", "JSWSTEEL",
    "MARUTI", "M&M", "BRITANNIA", "NESTLEIND", "HDFCLIFE",
    "SBILIFE", "BAJAJFINSV", "SHREECEM", "EICHERMOT", "COALINDIA",
    "HINDALCO", "UPL", "GRASIM", "DIVISLAB", "DRREDDY",
    "TECHM", "ADANIPORTS", "BPCL", "HEROMOTOCO", "INDUSINDBK",
    "IOCL", "BAJAJ-AUTO", "TATACONSUM", "CIPLA"
]

BASE_PRICES = {
    "RELIANCE": 2450, "TCS": 3800, "HDFC": 1650, "INFY": 1450,
    "HINDUNILVR": 2450, "ICICIBANK": 950, "ITC": 440, "SBIN": 620,
    "BHARTIARTL": 980, "KOTAKBANK": 1750, "LT": 3200, "WIPRO": 430,
    "HCLTECH": 1200, "ASIANPAINT": 3200, "AXISBANK": 1050,
    "TITAN": 3500, "SUNPHARMA": 1250, "ULTRACEMCO": 8200,
    "BAJFINANCE": 7500, "NTPC": 280, "ONGC": 175, "POWERGRID": 230,
    "TATAMOTORS": 850, "TATASTEEL": 120, "JSWSTEEL": 780,
    "MARUTI": 10500, "M&M": 1450, "BRITANNIA": 4900, "NESTLEIND": 25000,
    "HDFCLIFE": 650, "SBILIFE": 1350, "BAJAJFINSV": 1600,
    "SHREECEM": 26000, "EICHERMOT": 3800, "COALINDIA": 290,
    "HINDALCO": 490, "UPL": 720, "GRASIM": 1900, "DIVISLAB": 3800,
    "DRREDDY": 5500, "TECHM": 1200, "ADANIPORTS": 980,
    "BPCL": 360, "HEROMOTOCO": 3200, "INDUSINDBK": 1400,
    "IOCL": 120, "BAJAJ-AUTO": 4800, "TATACONSUM": 1050, "CIPLA": 1200
}

def get_stock_price(symbol):
    base = BASE_PRICES.get(symbol, 1000)
    variation = random.uniform(-0.02, 0.02)
    return round(base * (1 + variation), 2)

def generate_signal(symbol, price):
    rsi = random.randint(20, 80)
    macd = random.uniform(-10, 10)
    volume = random.randint(100000, 5000000)
    
    score = 0.5
    
    if rsi < 30:
        score += 0.3
    elif rsi > 70:
        score -= 0.3
    
    if macd > 0:
        score += 0.2
    else:
        score -= 0.2
    
    if volume > 2000000:
        score += 0.1
    
    if score >= 0.7:
        action = "BUY"
        confidence = score
        target = round(price * 1.05, 2)
        stop_loss = round(price * 0.98, 2)
    elif score <= 0.3:
        action = "SELL"
        confidence = 1 - score
        target = round(price * 0.95, 2)
        stop_loss = round(price * 1.02, 2)
    else:
        action = "HOLD"
        confidence = 0.5
        target = price
        stop_loss = price
    
    return {
        "symbol": symbol,
        "action": action,
        "confidence": round(confidence, 2),
        "current_price": price,
        "target": target,
        "stop_loss": stop_loss,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    return {
        "platform": "TITAN Trading Platform",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/screener/nifty50")
async def scan_nifty50():
    results = []
    for symbol in NIFTY_50:
        price = get_stock_price(symbol)
        signal = generate_signal(symbol, price)
        results.append(signal)
    
    results.sort(key=lambda x: x['confidence'], reverse=True)
    
    return {
        "total_scanned": len(results),
        "buy_signals": [r for r in results if r['action'] == 'BUY'],
        "sell_signals": [r for r in results if r['action'] == 'SELL'],
        "hold_signals": [r for r in results if r['action'] == 'HOLD'],
        "results": results,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/screener/{symbol}")
async def scan_stock(symbol: str):
    if symbol not in NIFTY_50:
        raise HTTPException(status_code=404, detail="Stock not in NIFTY 50")
    
    price = get_stock_price(symbol)
    signal = generate_signal(symbol, price)
    
    capital = 100000
    expected_profit = 0
    
    if signal['action'] == 'BUY':
        shares = int(capital / price)
        expected_profit = round(shares * (signal['target'] - price), 2)
    elif signal['action'] == 'SELL':
        shares = int(capital / price)
        expected_profit = round(shares * (price - signal['target']), 2)
    
    signal['expected_profit'] = expected_profit
    signal['capital_required'] = capital
    
    return signal

@app.get("/api/stocks")
async def get_stocks():
    stocks = []
    for symbol in NIFTY_50:
        stocks.append({
            "symbol": symbol,
            "price": get_stock_price(symbol),
            "timestamp": datetime.now().isoformat()
        })
    return stocks

@app.get("/api/stocks/{symbol}")
async def get_stock(symbol: str):
    if symbol not in NIFTY_50:
        raise HTTPException(status_code=404, detail="Stock not found")
    return {
        "symbol": symbol,
        "price": get_stock_price(symbol),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/market/status")
async def market_status():
    now = datetime.now()
    is_open = (
        now.weekday() < 5 and
        9 <= now.hour < 15 and
        not (now.hour == 9 and now.minute < 15)
    )
    return {
        "status": "open" if is_open else "closed",
        "timestamp": now.isoformat(),
        "next_open": "09:15 AM",
        "next_close": "03:30 PM"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
