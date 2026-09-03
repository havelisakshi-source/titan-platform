#!/usr/bin/env python3
"""
🚀 TITAN ULTIMATE - All-in-One Trading Platform
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import random
from datetime import datetime
import json

# ============================================
# NIFTY 50 STOCKS
# ============================================
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

# ============================================
# AI ENGINE
# ============================================
class AIEngine:
    def __init__(self):
        self.results = []
    
    def get_price(self, symbol):
        base = BASE_PRICES.get(symbol, 1000)
        variation = random.uniform(-0.02, 0.02)
        return round(base * (1 + variation), 2)
    
    def analyze(self, symbol, price):
        rsi = random.randint(20, 80)
        macd = random.uniform(-10, 10)
        volume = random.randint(100000, 5000000)
        
        score = 0.5
        if rsi < 30: score += 0.25
        elif rsi > 70: score -= 0.25
        if macd > 0: score += 0.15
        else: score -= 0.15
        if volume > 2000000: score += 0.05
        
        score = max(0, min(1, score))
        
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
    
    def scan(self):
        self.results = []
        for symbol in NIFTY_50:
            price = self.get_price(symbol)
            signal = self.analyze(symbol, price)
            self.results.append(signal)
        
        self.results.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            "total_scanned": len(self.results),
            "timestamp": datetime.now().isoformat(),
            "buy_signals": [r for r in self.results if r['action'] == 'BUY'],
            "sell_signals": [r for r in self.results if r['action'] == 'SELL'],
            "hold_signals": [r for r in self.results if r['action'] == 'HOLD'],
            "results": self.results
        }

# ============================================
# HTML WEB INTERFACE
# ============================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🚀 TITAN Trading Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }
        .header h1 {
            font-size: 2.5em;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .header .stats { display: flex; gap: 20px; flex-wrap: wrap; }
        .stat-box { text-align: center; padding: 10px; }
        .stat-box .number { font-size: 2em; font-weight: bold; }
        .stat-box .label { color: #666; font-size: 0.9em; }
        .buy-color { color: #00c853; }
        .sell-color { color: #ff1744; }
        .hold-color { color: #ffab00; }
        
        .controls {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
        }
        .controls button {
            padding: 12px 30px;
            border: none;
            border-radius: 10px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        .controls button:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(0,0,0,0.2); }
        .btn-refresh { background: #667eea; color: white; }
        .btn-buy { background: #00c853; color: white; }
        .btn-sell { background: #ff1744; color: white; }
        .btn-hold { background: #ffab00; color: white; }
        .btn-all { background: #333; color: white; }
        
        .signal-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        .signal-card {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: all 0.3s;
            border-left: 5px solid #ccc;
        }
        .signal-card:hover { transform: translateY(-5px); box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .signal-card.buy { border-left-color: #00c853; }
        .signal-card.sell { border-left-color: #ff1744; }
        .signal-card.hold { border-left-color: #ffab00; }
        
        .signal-card .symbol { font-size: 1.5em; font-weight: bold; margin-bottom: 10px; }
        .signal-card .action {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        .action-buy { background: #e8f5e9; color: #00c853; }
        .action-sell { background: #ffebee; color: #ff1744; }
        .action-hold { background: #fff8e1; color: #ffab00; }
        
        .signal-card .price { font-size: 1.8em; font-weight: bold; margin: 10px 0; }
        .signal-card .details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 10px;
        }
        .signal-card .details div {
            background: #f5f5f5;
            padding: 8px;
            border-radius: 8px;
            text-align: center;
        }
        .signal-card .details .label { font-size: 0.8em; color: #666; }
        .signal-card .details .value { font-weight: bold; }
        
        .confidence-bar {
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            margin-top: 10px;
            overflow: hidden;
        }
        .confidence-bar .fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s;
        }
        .confidence-bar .fill.high { background: #00c853; }
        .confidence-bar .fill.medium { background: #ffab00; }
        .confidence-bar .fill.low { background: #ff1744; }
        
        .loading { text-align: center; padding: 50px; color: white; font-size: 1.5em; }
        @media (max-width: 768px) {
            .header { flex-direction: column; text-align: center; }
            .signal-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 TITAN Trading Platform</h1>
            <div class="stats">
                <div class="stat-box"><div class="number buy-color" id="totalStocks">-</div><div class="label">Total</div></div>
                <div class="stat-box"><div class="number buy-color" id="buyCount">-</div><div class="label">BUY</div></div>
                <div class="stat-box"><div class="number sell-color" id="sellCount">-</div><div class="label">SELL</div></div>
                <div class="stat-box"><div class="number hold-color" id="holdCount">-</div><div class="label">HOLD</div></div>
                <div class="stat-box"><div class="number" id="lastUpdate">-</div><div class="label">Updated</div></div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn-refresh" onclick="refreshData()">🔄 Refresh</button>
            <button class="btn-all" onclick="filterData('all')">All</button>
            <button class="btn-buy" onclick="filterData('BUY')">BUY</button>
            <button class="btn-sell" onclick="filterData('SELL')">SELL</button>
            <button class="btn-hold" onclick="filterData('HOLD')">HOLD</button>
            <span style="margin-left: auto; color: #666;">Auto-refresh: 60s</span>
        </div>
        
        <div id="signals" class="signal-grid"><div class="loading">Loading signals...</div></div>
    </div>
    
    <script>
        let currentData = [];
        let currentFilter = 'all';
        
        function formatCurrency(v) { return '₹' + Number(v).toLocaleString('en-IN', {maximumFractionDigits: 2}); }
        
        function renderSignals(signals) {
            const container = document.getElementById('signals');
            if (!signals || signals.length === 0) {
                container.innerHTML = '<div class="loading">No signals found</div>';
                return;
            }
            
            let html = '';
            signals.forEach(s => {
                const actionClass = s.action.toLowerCase();
                const confClass = s.confidence >= 0.7 ? 'high' : s.confidence >= 0.4 ? 'medium' : 'low';
                const profit = s.expected_profit || 0;
                
                html += `
                    <div class="signal-card ${actionClass}">
                        <div class="symbol">${s.symbol}</div>
                        <div class="action action-${actionClass}">${s.action}</div>
                        <div class="price">${formatCurrency(s.current_price)}</div>
                        <div class="details">
                            <div><div class="label">Target</div><div class="value">${formatCurrency(s.target)}</div></div>
                            <div><div class="label">Stop Loss</div><div class="value">${formatCurrency(s.stop_loss)}</div></div>
                            <div><div class="label">Confidence</div><div class="value">${(s.confidence * 100).toFixed(0)}%</div></div>
                            <div><div class="label">Profit</div><div class="value" style="color:${profit>0?'#00c853':'#ff1744'}">${formatCurrency(profit)}</div></div>
                        </div>
                        <div class="confidence-bar"><div class="fill ${confClass}" style="width:${s.confidence*100}%"></div></div>
                        <div style="font-size:0.8em;color:#999;margin-top:8px;">${s.timestamp ? new Date(s.timestamp).toLocaleTimeString() : ''}</div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }
        
        function updateStats(data) {
            document.getElementById('totalStocks').textContent = data.total_scanned || 0;
            document.getElementById('buyCount').textContent = data.buy_signals ? data.buy_signals.length : 0;
            document.getElementById('sellCount').textContent = data.sell_signals ? data.sell_signals.length : 0;
            document.getElementById('holdCount').textContent = data.hold_signals ? data.hold_signals.length : 0;
            if (data.timestamp) document.getElementById('lastUpdate').textContent = new Date(data.timestamp).toLocaleTimeString();
        }
        
        function filterData(filter) {
            currentFilter = filter;
            const data = currentData;
            if (filter === 'all') { renderSignals(data.results || []); return; }
            renderSignals((data.results || []).filter(s => s.action === filter));
        }
        
        async function refreshData() {
            try {
                const response = await fetch('/api/screener/nifty50');
                const data = await response.json();
                currentData = data;
                updateStats(data);
                filterData(currentFilter);
            } catch (error) {
                document.getElementById('signals').innerHTML = '<div class="loading">⚠️ Error loading data</div>';
            }
        }
        
        refreshData();
        setInterval(refreshData, 60000);
    </script>
</body>
</html>
"""

# ============================================
# FASTAPI APPLICATION
# ============================================
app = FastAPI(title="TITAN Trading Platform", version="1.0.0")
ai = AIEngine()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return HTMLResponse(HTML_TEMPLATE)

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/screener/nifty50")
async def scan_nifty50():
    data = ai.scan()
    # Add expected profit
    for signal in data['results']:
        capital = 100000
        if signal['action'] == 'BUY':
            shares = int(capital / signal['current_price'])
            signal['expected_profit'] = round(shares * (signal['target'] - signal['current_price']), 2)
        elif signal['action'] == 'SELL':
            shares = int(capital / signal['current_price'])
            signal['expected_profit'] = round(shares * (signal['current_price'] - signal['target']), 2)
        else:
            signal['expected_profit'] = 0
        signal['capital_required'] = capital
    return data

@app.get("/api/screener/{symbol}")
async def scan_stock(symbol: str):
    if symbol not in NIFTY_50:
        raise HTTPException(status_code=404, detail="Stock not found")
    price = ai.get_price(symbol)
    signal = ai.analyze(symbol, price)
    capital = 100000
    if signal['action'] == 'BUY':
        shares = int(capital / price)
        signal['expected_profit'] = round(shares * (signal['target'] - price), 2)
    elif signal['action'] == 'SELL':
        shares = int(capital / price)
        signal['expected_profit'] = round(shares * (price - signal['target']), 2)
    else:
        signal['expected_profit'] = 0
    signal['capital_required'] = capital
    return signal

@app.get("/api/stocks")
async def get_stocks():
    stocks = []
    for symbol in NIFTY_50:
        stocks.append({"symbol": symbol, "price": ai.get_price(symbol)})
    return stocks

@app.get("/api/stocks/{symbol}")
async def get_stock(symbol: str):
    if symbol not in NIFTY_50:
        raise HTTPException(status_code=404, detail="Stock not found")
    return {"symbol": symbol, "price": ai.get_price(symbol)}

@app.get("/api/market/status")
async def market_status():
    now = datetime.now()
    is_open = now.weekday() < 5 and 9 <= now.hour < 15 and not (now.hour == 9 and now.minute < 15)
    return {"status": "open" if is_open else "closed", "timestamp": now.isoformat()}

# ============================================
# RUN THE APPLICATION
# ============================================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 TITAN ULTIMATE TRADING PLATFORM")
    print("=" * 60)
    print(f"📊 NIFTY 50 Stocks: {len(NIFTY_50)}")
    print(f"🌐 Web Interface: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print("=" * 60)
    print("\n✅ Platform is running! Open your browser to get started.")
    print("🔄 Auto-refresh every 60 seconds\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
