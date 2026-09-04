#!/usr/bin/env python3
"""
🚀 TITAN PRO – Intraday Edition
- Real-time prices from NSE (fallback to simulated)
- Intraday price history (last 60 points)
- Sparkline charts on every card
- Advanced indicators (RSI, MACD, Bollinger Bands)
- Paper trading, Telegram alerts
- Full animated dashboard
"""

import asyncio
import json
import random
import os
import math
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# --- Web Framework ---
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
import uvicorn

# --- NSE (only real data source) ---
try:
    from nsetools import Nse
    nse = Nse()
    HAS_NSE = True
except:
    HAS_NSE = False
    print("⚠️ nsetools not installed. Install: pip install nsetools")

# --- Telegram ---
try:
    import requests
    HAS_REQUESTS = True
except:
    HAS_REQUESTS = False
    print("⚠️ requests not installed. Telegram alerts won't work.")

# --- Indicators (TA-Lib optional, fallback included) ---
try:
    import talib
    HAS_TALIB = True
except:
    HAS_TALIB = False
    print("⚠️ TA-Lib not installed. Using fallback indicators.")

# ============================================
# CONFIGURATION
# ============================================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID")

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
# INTRADAY PRICE SIMULATION
# ============================================
def generate_intraday_prices(base_price, num_points=60):
    """Generate simulated intraday price movement."""
    prices = []
    current = base_price
    for _ in range(num_points):
        change = random.uniform(-0.005, 0.005)  # 0.5% max change per step
        current = max(1, current * (1 + change))
        prices.append(round(current, 2))
    return prices

# ============================================
# REAL DATA FETCHER (NSE Only)
# ============================================
def get_real_price(symbol):
    """Get real price from NSE, returns None if fails"""
    if HAS_NSE:
        try:
            quote = nse.get_quote(symbol)
            if quote and 'lastPrice' in quote:
                return round(quote['lastPrice'], 2)
        except:
            pass
    return None

def get_historical_data_simulated(symbol):
    """Generate simulated historical prices for indicators"""
    base = BASE_PRICES.get(symbol, 1000)
    prices = []
    current = base
    for _ in range(30):
        change = random.uniform(-0.03, 0.03)
        current = max(1, current * (1 + change))
        prices.append(round(current, 2))
    return prices

# ============================================
# FALLBACK INDICATORS (if TA-Lib not available)
# ============================================
def fallback_rsi(prices, period=14):
    if len(prices) < period:
        return 50.0
    delta = np.diff(prices)
    gains = delta[delta > 0].sum() / period
    losses = -delta[delta < 0].sum() / period
    if losses == 0:
        return 100.0
    rs = gains / losses
    return 100 - (100 / (1 + rs))

def fallback_sma(prices, period):
    if len(prices) < period:
        return float(prices[-1])
    return float(np.mean(prices[-period:]))

# ============================================
# INDICATOR ENGINE (with NaN cleaning)
# ============================================
class IndicatorEngine:
    @staticmethod
    def calculate_indicators(prices):
        def clean(val):
            if math.isnan(val):
                return 0.0
            return round(val, 2)

        if HAS_TALIB and len(prices) >= 30:
            close_array = np.array(prices, dtype=float)
            rsi = talib.RSI(close_array, timeperiod=14)[-1] if len(close_array) >= 14 else 50.0
            macd, macd_signal, macd_hist = talib.MACD(close_array)
            macd_val = macd[-1] if len(macd) else 0.0
            macd_signal_val = macd_signal[-1] if len(macd_signal) else 0.0
            macd_hist_val = macd_hist[-1] if len(macd_hist) else 0.0
            upper, middle, lower = talib.BBANDS(close_array, timeperiod=20, nbdevup=2, nbdevdn=2)
            bb_upper = upper[-1] if len(upper) else 0.0
            bb_middle = middle[-1] if len(middle) else 0.0
            bb_lower = lower[-1] if len(lower) else 0.0
            atr = talib.ATR(close_array, close_array, close_array, timeperiod=14)[-1] if len(close_array) >= 14 else 0.0
            sma_20 = talib.SMA(close_array, timeperiod=20)[-1] if len(close_array) >= 20 else prices[-1]
            sma_50 = talib.SMA(close_array, timeperiod=50)[-1] if len(close_array) >= 50 else prices[-1]
        else:
            rsi = fallback_rsi(prices) if len(prices) >= 14 else 50.0
            macd_val = 0.0
            macd_signal_val = 0.0
            macd_hist_val = 0.0
            bb_upper = 0.0
            bb_middle = 0.0
            bb_lower = 0.0
            atr = 0.0
            sma_20 = fallback_sma(prices, 20) if len(prices) >= 20 else prices[-1]
            sma_50 = fallback_sma(prices, 50) if len(prices) >= 50 else prices[-1]

        return {
            "rsi": clean(rsi),
            "macd": clean(macd_val),
            "macd_signal": clean(macd_signal_val),
            "macd_hist": clean(macd_hist_val),
            "bb_upper": clean(bb_upper),
            "bb_middle": clean(bb_middle),
            "bb_lower": clean(bb_lower),
            "atr": clean(atr),
            "sma_20": clean(sma_20),
            "sma_50": clean(sma_50)
        }

# ============================================
# PAPER TRADER
# ============================================
class PaperTrader:
    def __init__(self):
        self.cash = 100000.0
        self.positions = {}
        self.trades = []
        self.initial_cash = 100000.0

    def buy(self, symbol, price, shares):
        cost = price * shares
        if cost > self.cash:
            return {"error": "Insufficient cash"}
        self.cash -= cost
        self.positions[symbol] = self.positions.get(symbol, 0) + shares
        self.trades.append({"action": "BUY", "symbol": symbol, "shares": shares, "price": price, "time": datetime.now().isoformat()})
        return {"success": True, "cash": self.cash, "position": self.positions[symbol]}

    def sell(self, symbol, price, shares):
        if symbol not in self.positions or self.positions[symbol] < shares:
            return {"error": "Insufficient shares"}
        self.positions[symbol] -= shares
        self.cash += price * shares
        if self.positions[symbol] == 0:
            del self.positions[symbol]
        self.trades.append({"action": "SELL", "symbol": symbol, "shares": shares, "price": price, "time": datetime.now().isoformat()})
        return {"success": True, "cash": self.cash, "position": self.positions.get(symbol, 0)}

    def get_portfolio(self, current_prices):
        total_value = self.cash
        holdings = []
        for sym, shares in self.positions.items():
            price = current_prices.get(sym, 0)
            value = shares * price
            total_value += value
            holdings.append({"symbol": sym, "shares": shares, "price": price, "value": value})
        return {
            "cash": round(self.cash, 2),
            "holdings": holdings,
            "total_value": round(total_value, 2),
            "pnl": round(total_value - self.initial_cash, 2),
            "pnl_percent": round(((total_value / self.initial_cash) - 1) * 100, 2)
        }

# ============================================
# TELEGRAM ALERTS
# ============================================
def send_telegram_alert(message):
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "YOUR_BOT_TOKEN":
        return
    if not HAS_REQUESTS:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, json=data, timeout=5)
    except:
        pass

# ============================================
# AI ENGINE (with Intraday Data)
# ============================================
class AIEngine:
    def __init__(self):
        self.results = []
        self.use_real_data = True
        self.last_prices = {}
        self.intraday = {}  # symbol -> list of (timestamp, price)
        self.paper_trader = PaperTrader()
        self.intraday_limit = 60  # keep last 60 points

    def update_intraday(self, symbol, price):
        """Add new price point to intraday history"""
        now = datetime.now().isoformat()
        if symbol not in self.intraday:
            self.intraday[symbol] = []
        self.intraday[symbol].append((now, price))
        # Keep only the last N points
        if len(self.intraday[symbol]) > self.intraday_limit:
            self.intraday[symbol] = self.intraday[symbol][-self.intraday_limit:]

    def get_price(self, symbol):
        if self.use_real_data:
            price = get_real_price(symbol)
            if price:
                self.last_prices[symbol] = price
                self.update_intraday(symbol, price)
                return price
        # fallback to simulation
        base = BASE_PRICES.get(symbol, 1000)
        old = self.last_prices.get(symbol, base)
        change = random.uniform(-1.5, 1.5)
        new_price = max(1, old + change)
        self.last_prices[symbol] = new_price
        self.update_intraday(symbol, new_price)
        return round(new_price, 2)

    def get_intraday_prices(self, symbol):
        """Return list of prices (last N points) for a symbol"""
        if symbol in self.intraday:
            return [p[1] for p in self.intraday[symbol]]
        # generate simulated intraday if missing
        base = BASE_PRICES.get(symbol, 1000)
        return generate_intraday_prices(base, 30)

    def get_historical_prices(self, symbol):
        # Always use simulated for indicators (no real historical needed)
        return get_historical_data_simulated(symbol)

    def analyze(self, symbol, price):
        hist = self.get_historical_prices(symbol)
        if len(hist) < 14:
            hist = [price] * 30
        indicators = IndicatorEngine.calculate_indicators(hist)

        score = 0.5
        rsi = indicators['rsi']
        macd = indicators['macd']
        macd_signal = indicators['macd_signal']
        bb_lower = indicators['bb_lower']
        bb_upper = indicators['bb_upper']
        atr = indicators['atr']

        if rsi < 30: score += 0.25
        elif rsi > 70: score -= 0.25
        if macd > macd_signal: score += 0.15
        else: score -= 0.15
        if price < bb_lower: score += 0.10
        elif price > bb_upper: score -= 0.10

        score = max(0, min(1, score))

        if score >= 0.7:
            action = "BUY"
            confidence = score
            target = round(price + atr * 2, 2) if atr else round(price * 1.05, 2)
            stop_loss = round(price - atr * 1.5, 2) if atr else round(price * 0.98, 2)
        elif score <= 0.3:
            action = "SELL"
            confidence = 1 - score
            target = round(price - atr * 2, 2) if atr else round(price * 0.95, 2)
            stop_loss = round(price + atr * 1.5, 2) if atr else round(price * 1.02, 2)
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
            "indicators": indicators,
            "intraday": self.get_intraday_prices(symbol),  # include last 30 prices for sparkline
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
# FASTAPI APP
# ============================================
app = FastAPI(title="TITAN Pro - Intraday", version="3.1.0")
ai = AIEngine()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# HTML TEMPLATE (Animated Dashboard with Sparklines)
# ============================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 TITAN Pro - Intraday</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --bg: #0a0e17;
            --card: rgba(255,255,255,0.05);
            --text: #e0e0e0;
            --border: rgba(255,255,255,0.1);
            --glow: rgba(102, 126, 234, 0.3);
        }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            padding: 20px;
            transition: background 0.5s, color 0.5s;
        }
        body.light {
            --bg: #f0f4ff;
            --card: rgba(0,0,0,0.04);
            --text: #1a1a2e;
            --border: rgba(0,0,0,0.1);
            --glow: rgba(102, 126, 234, 0.2);
        }
        .container { max-width: 1600px; margin: 0 auto; }
        .header {
            background: var(--card);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            padding: 25px 30px;
            margin-bottom: 25px;
            border: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
            animation: fadeInDown 0.8s ease;
        }
        .header h1 {
            font-size: 2.2rem;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .header-actions {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        .theme-toggle {
            background: var(--card);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 10px 18px;
            border-radius: 30px;
            cursor: pointer;
            font-size: 1rem;
            transition: 0.3s;
        }
        .theme-toggle:hover { transform: scale(1.05); box-shadow: 0 0 20px var(--glow); }
        .stats-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }
        .stat-card {
            background: var(--card);
            border-radius: 16px;
            padding: 18px 15px;
            text-align: center;
            border: 1px solid var(--border);
            transition: all 0.3s;
            animation: fadeInUp 0.6s ease backwards;
        }
        .stat-card:hover { transform: translateY(-4px); box-shadow: 0 8px 30px var(--glow); }
        .stat-card .number { font-size: 2.2rem; font-weight: 700; }
        .stat-card .label { font-size: 0.85rem; opacity: 0.7; margin-top: 4px; }
        .buy-color { color: #00c853; }
        .sell-color { color: #ff1744; }
        .hold-color { color: #ffab00; }
        .ticker-wrap {
            background: var(--card);
            border-radius: 16px;
            padding: 12px 20px;
            margin-bottom: 25px;
            border: 1px solid var(--border);
            overflow: hidden;
            white-space: nowrap;
        }
        .ticker {
            display: inline-block;
            animation: tickerScroll 30s linear infinite;
        }
        .ticker-item { display: inline-block; margin: 0 25px; font-weight: 500; }
        .ticker-item .up { color: #00c853; }
        .ticker-item .down { color: #ff1744; }
        @keyframes tickerScroll {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }
        .controls {
            background: var(--card);
            border-radius: 16px;
            padding: 18px 22px;
            margin-bottom: 25px;
            border: 1px solid var(--border);
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            align-items: center;
            animation: fadeInUp 0.6s ease backwards;
            animation-delay: 0.1s;
        }
        .controls button {
            padding: 10px 24px;
            border: none;
            border-radius: 30px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            background: var(--card);
            color: var(--text);
            border: 1px solid var(--border);
        }
        .controls button:hover { transform: scale(1.05); box-shadow: 0 0 20px var(--glow); }
        .controls button.active { background: #667eea; color: white; border-color: #667eea; }
        .btn-refresh { background: #667eea !important; color: white !important; border-color: #667eea !important; }
        .btn-buy.active { background: #00c853 !important; color: white !important; }
        .btn-sell.active { background: #ff1744 !important; color: white !important; }
        .btn-hold.active { background: #ffab00 !important; color: white !important; }
        .signal-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 20px;
            animation: fadeIn 0.8s ease;
        }
        .signal-card {
            background: var(--card);
            backdrop-filter: blur(8px);
            border-radius: 20px;
            padding: 22px;
            border: 1px solid var(--border);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
            cursor: default;
        }
        .signal-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 60px var(--glow);
            border-color: rgba(102,126,234,0.5);
        }
        .signal-card .glow {
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(102,126,234,0.1) 0%, transparent 70%);
            opacity: 0;
            transition: opacity 0.6s;
            pointer-events: none;
        }
        .signal-card:hover .glow { opacity: 1; }
        .signal-card.buy { border-left: 6px solid #00c853; }
        .signal-card.sell { border-left: 6px solid #ff1744; }
        .signal-card.hold { border-left: 6px solid #ffab00; }
        .signal-card .top-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        .signal-card .symbol { font-size: 1.6rem; font-weight: 700; }
        .signal-card .action-badge {
            padding: 4px 16px;
            border-radius: 30px;
            font-weight: 600;
            font-size: 0.9rem;
        }
        .action-badge.buy { background: #00c85322; color: #00c853; }
        .action-badge.sell { background: #ff174422; color: #ff1744; }
        .action-badge.hold { background: #ffab0022; color: #ffab00; }
        .signal-card .price { font-size: 2rem; font-weight: 700; margin: 6px 0 8px; }
        .signal-card .indicators {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            margin: 12px 0;
            font-size: 0.85rem;
        }
        .signal-card .indicators span {
            background: rgba(255,255,255,0.05);
            padding: 4px 8px;
            border-radius: 8px;
            text-align: center;
        }
        .signal-card .chart-container {
            margin: 12px 0 8px;
            height: 40px;
            width: 100%;
        }
        .signal-card .chart-container svg {
            width: 100%;
            height: 100%;
        }
        .signal-card .details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 10px;
        }
        .signal-card .details div {
            background: rgba(255,255,255,0.04);
            padding: 8px 10px;
            border-radius: 12px;
            text-align: center;
        }
        .signal-card .details .label { font-size: 0.7rem; opacity: 0.6; }
        .signal-card .details .value { font-weight: 600; }
        .confidence-bar {
            width: 100%;
            height: 6px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            margin-top: 12px;
            overflow: hidden;
        }
        .confidence-bar .fill {
            height: 100%;
            border-radius: 4px;
            transition: width 1s ease;
            background: linear-gradient(90deg, #00c853, #ffab00, #ff1744);
        }
        .signal-card .timestamp { font-size: 0.7rem; opacity: 0.5; margin-top: 10px; text-align: right; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes fadeInDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .pulse { animation: pulse 2s infinite; }
        @media (max-width: 640px) {
            .header h1 { font-size: 1.6rem; }
            .signal-grid { grid-template-columns: 1fr; }
            .stats-row { grid-template-columns: 1fr 1fr; }
        }
    </style>
</head>
<body>
<div class="container">
    <header class="header">
        <h1>🚀 TITAN <span style="font-weight:300;font-size:1rem;background:none;-webkit-text-fill-color:currentColor;opacity:0.7;">Pro</span></h1>
        <div class="header-actions">
            <button class="theme-toggle" onclick="toggleTheme()">🌓 Theme</button>
            <span id="liveIndicator" style="display:flex;align-items:center;gap:6px;font-size:0.9rem;">
                <span class="pulse" style="color:#00c853;">●</span> Live
            </span>
        </div>
    </header>

    <div class="stats-row" id="statsRow">
        <div class="stat-card"><div class="number buy-color" id="totalStocks">-</div><div class="label">Total Stocks</div></div>
        <div class="stat-card"><div class="number buy-color" id="buyCount">-</div><div class="label">BUY Signals</div></div>
        <div class="stat-card"><div class="number sell-color" id="sellCount">-</div><div class="label">SELL Signals</div></div>
        <div class="stat-card"><div class="number hold-color" id="holdCount">-</div><div class="label">HOLD Signals</div></div>
        <div class="stat-card"><div class="number" id="lastUpdate">-</div><div class="label">Last Update</div></div>
    </div>

    <div class="ticker-wrap" id="tickerWrap">
        <div class="ticker" id="ticker"></div>
    </div>

    <div class="controls">
        <button class="btn-refresh" onclick="refreshData()">🔄 Refresh</button>
        <button class="btn-all active" data-filter="all" onclick="setFilter('all')">All</button>
        <button class="btn-buy" data-filter="BUY" onclick="setFilter('BUY')">BUY</button>
        <button class="btn-sell" data-filter="SELL" onclick="setFilter('SELL')">SELL</button>
        <button class="btn-hold" data-filter="HOLD" onclick="setFilter('HOLD')">HOLD</button>
        <span style="margin-left:auto;opacity:0.6;font-size:0.9rem;">Auto-update every 5s</span>
    </div>

    <div id="signalGrid" class="signal-grid">
        <div style="text-align:center;padding:60px;opacity:0.6;">Loading signals...</div>
    </div>
</div>

<script>
    let currentData = null;
    let currentFilter = 'all';
    let eventSource = null;

    function toggleTheme() { document.body.classList.toggle('light'); }

    function renderSparkline(canvasId, prices) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        ctx.clearRect(0, 0, width, height);

        if (!prices || prices.length < 2) {
            ctx.fillStyle = '#666';
            ctx.font = '12px sans-serif';
            ctx.fillText('No data', 10, height/2 + 4);
            return;
        }

        const min = Math.min(...prices);
        const max = Math.max(...prices);
        const range = max - min || 1;
        const padding = 4;

        ctx.beginPath();
        ctx.strokeStyle = '#667eea';
        ctx.lineWidth = 2;
        for (let i = 0; i < prices.length; i++) {
            const x = padding + (i / (prices.length - 1)) * (width - 2 * padding);
            const y = height - padding - ((prices[i] - min) / range) * (height - 2 * padding);
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.stroke();

        // fill under curve
        ctx.lineTo(width - padding, height - padding);
        ctx.lineTo(padding, height - padding);
        ctx.closePath();
        ctx.fillStyle = 'rgba(102,126,234,0.1)';
        ctx.fill();
    }

    function renderSignals(signals) {
        const grid = document.getElementById('signalGrid');
        if (!signals || signals.length === 0) {
            grid.innerHTML = '<div style="text-align:center;padding:60px;opacity:0.6;">No signals match filter</div>';
            return;
        }
        let html = '';
        signals.forEach((s, idx) => {
            const actionClass = s.action.toLowerCase();
            const profit = s.expected_profit || 0;
            const rsi = s.indicators?.rsi || '--';
            const macd = s.indicators?.macd || '--';
            const volume = s.indicators?.volume ? (s.indicators.volume/1e6).toFixed(1)+'M' : '--';
            const intraday = s.intraday || [];
            const canvasId = 'sparkline-' + s.symbol + '-' + idx;

            html += `
                <div class="signal-card ${actionClass}" style="animation: fadeInUp 0.4s ease backwards; animation-delay: ${idx*0.05}s;">
                    <div class="glow"></div>
                    <div class="top-row">
                        <span class="symbol">${s.symbol}</span>
                        <span class="action-badge ${actionClass}">${s.action}</span>
                    </div>
                    <div class="price">₹${s.current_price.toFixed(2)}</div>
                    <div class="indicators">
                        <span>RSI ${rsi}</span>
                        <span>MACD ${macd}</span>
                        <span>Vol ${volume}</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="${canvasId}" width="300" height="40"></canvas>
                    </div>
                    <div class="details">
                        <div><div class="label">Target</div><div class="value">₹${s.target.toFixed(2)}</div></div>
                        <div><div class="label">Stop Loss</div><div class="value">₹${s.stop_loss.toFixed(2)}</div></div>
                        <div><div class="label">Confidence</div><div class="value">${(s.confidence*100).toFixed(0)}%</div></div>
                        <div><div class="label">Profit (₹1L)</div><div class="value" style="color:${profit>=0?'#00c853':'#ff1744'}">₹${profit.toFixed(2)}</div></div>
                    </div>
                    <div class="confidence-bar"><div class="fill" style="width:${s.confidence*100}%;background:linear-gradient(90deg, ${s.confidence>=0.7?'#00c853':s.confidence>=0.4?'#ffab00':'#ff1744'}, ${s.confidence>=0.7?'#00c853':s.confidence>=0.4?'#ffab00':'#ff1744'});"></div></div>
                    <div class="timestamp">${s.timestamp ? new Date(s.timestamp).toLocaleTimeString() : ''}</div>
                </div>
            `;
        });
        grid.innerHTML = html;

        // Render sparklines after DOM update
        signals.forEach((s, idx) => {
            const canvasId = 'sparkline-' + s.symbol + '-' + idx;
            renderSparkline(canvasId, s.intraday || []);
        });
    }

    function updateStats(data) {
        document.getElementById('totalStocks').textContent = data.total_scanned || 0;
        document.getElementById('buyCount').textContent = data.buy_signals ? data.buy_signals.length : 0;
        document.getElementById('sellCount').textContent = data.sell_signals ? data.sell_signals.length : 0;
        document.getElementById('holdCount').textContent = data.hold_signals ? data.hold_signals.length : 0;
        if (data.timestamp) {
            document.getElementById('lastUpdate').textContent = new Date(data.timestamp).toLocaleTimeString();
        }
    }

    function setFilter(filter) {
        currentFilter = filter;
        document.querySelectorAll('.controls button[data-filter]').forEach(b => {
            b.classList.toggle('active', b.dataset.filter === filter);
        });
        applyFilter();
    }

    function applyFilter() {
        if (!currentData) return;
        const all = currentData.results || [];
        let filtered = all;
        if (currentFilter !== 'all') {
            filtered = all.filter(s => s.action === currentFilter);
        }
        renderSignals(filtered);
    }

    async function refreshData() {
        try {
            const resp = await fetch('/api/screener/nifty50?use_real=true');
            const data = await resp.json();
            currentData = data;
            updateStats(data);
            updateTicker(data);
            applyFilter();
        } catch (e) { console.error('Refresh error:', e); }
    }

    function updateTicker(data) {
        if (!data || !data.results) return;
        const buys = data.results.filter(r => r.action === 'BUY').slice(0,5);
        const sells = data.results.filter(r => r.action === 'SELL').slice(0,5);
        const items = [...buys, ...sells];
        if (items.length === 0) return;
        let html = '';
        items.forEach(s => {
            const cls = s.action === 'BUY' ? 'up' : 'down';
            const arrow = s.action === 'BUY' ? '▲' : '▼';
            html += `<span class="ticker-item">${s.symbol} <span class="${cls}">${arrow} ${s.current_price}</span></span>`;
        });
        document.getElementById('ticker').innerHTML = html + html;
    }

    function connectSSE() {
        if (eventSource) eventSource.close();
        eventSource = new EventSource('/api/stream');
        eventSource.onmessage = function(e) {
            try {
                const data = JSON.parse(e.data);
                currentData = data;
                updateStats(data);
                updateTicker(data);
                applyFilter();
            } catch (err) { console.error('SSE parse error', err); }
        };
        eventSource.onerror = function(e) {
            console.warn('SSE connection lost, reconnecting...');
            setTimeout(connectSSE, 3000);
        };
    }

    refreshData();
    connectSSE();
    setInterval(refreshData, 10000);
    document.addEventListener('keydown', (e) => { if (e.key === 'r' || e.key === 'R') refreshData(); });
</script>
</body>
</html>
"""

# ============================================
# API ENDPOINTS (including Intraday)
# ============================================
@app.get("/")
async def root():
    return HTMLResponse(HTML_TEMPLATE)

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/screener/nifty50")
async def scan_nifty50(use_real: bool = True):
    ai.use_real_data = use_real
    data = ai.scan()
    for s in data['results']:
        capital = 100000
        if s['action'] == 'BUY':
            shares = int(capital / s['current_price'])
            s['expected_profit'] = round(shares * (s['target'] - s['current_price']), 2)
        elif s['action'] == 'SELL':
            shares = int(capital / s['current_price'])
            s['expected_profit'] = round(shares * (s['current_price'] - s['target']), 2)
        else:
            s['expected_profit'] = 0
        s['capital_required'] = capital
        # Ensure intraday is included (already in signal)
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

@app.get("/api/intraday/{symbol}")
async def get_intraday(symbol: str, points: int = 30):
    """Return intraday price points for a symbol."""
    if symbol not in NIFTY_50:
        raise HTTPException(status_code=404, detail="Stock not found")
    prices = ai.get_intraday_prices(symbol)
    # Return last 'points' entries
    if len(prices) > points:
        prices = prices[-points:]
    return {
        "symbol": symbol,
        "prices": prices,
        "timestamp": datetime.now().isoformat()
    }

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

@app.post("/api/paper/buy")
async def paper_buy(symbol: str, shares: int):
    if symbol not in NIFTY_50:
        raise HTTPException(404, "Symbol not found")
    price = ai.get_price(symbol)
    result = ai.paper_trader.buy(symbol, price, shares)
    return result

@app.post("/api/paper/sell")
async def paper_sell(symbol: str, shares: int):
    if symbol not in NIFTY_50:
        raise HTTPException(404, "Symbol not found")
    price = ai.get_price(symbol)
    result = ai.paper_trader.sell(symbol, price, shares)
    return result

@app.get("/api/paper/portfolio")
async def paper_portfolio():
    current_prices = {sym: ai.get_price(sym) for sym in NIFTY_50}
    return ai.paper_trader.get_portfolio(current_prices)

@app.post("/api/telegram/alert")
async def send_alert(message: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_telegram_alert, message)
    return {"status": "alert sent"}

@app.get("/api/stream")
async def stream_events():
    async def event_generator():
        while True:
            data = ai.scan()
            for s in data['results']:
                capital = 100000
                if s['action'] == 'BUY':
                    shares = int(capital / s['current_price'])
                    s['expected_profit'] = round(shares * (s['target'] - s['current_price']), 2)
                elif s['action'] == 'SELL':
                    shares = int(capital / s['current_price'])
                    s['expected_profit'] = round(shares * (s['current_price'] - s['target']), 2)
                else:
                    s['expected_profit'] = 0
                s['capital_required'] = capital
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(5)
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# ============================================
# RUN
# ============================================
if __name__ == "__main__":
    print("🚀 TITAN PRO (Intraday Edition) starting...")
    uvicorn.run(app, host="0.0.0.0", port=8000)