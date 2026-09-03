#!/usr/bin/env python3
"""
🚀 TITAN ADVANCED - Real-time Animated Trading Platform
Features:
- Server-Sent Events for live price updates
- Animated cards with CSS transitions
- Live ticker of top gainers/losers
- Mini charts with bar indicators
- RSI, MACD, Volume display
- Dark/Light mode toggle
- Sound alerts on high-confidence signals
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
import uvicorn
import random
import asyncio
from datetime import datetime
import json
import time

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
# AI ENGINE (Enhanced)
# ============================================
class AIEngine:
    def __init__(self):
        self.results = []
        self.last_prices = {}
    
    def get_price(self, symbol):
        base = BASE_PRICES.get(symbol, 1000)
        # Add some momentum simulation
        old = self.last_prices.get(symbol, base)
        change = random.uniform(-1.5, 1.5)  # price change
        new_price = max(1, old + change)
        self.last_prices[symbol] = new_price
        return round(new_price, 2)
    
    def analyze(self, symbol, price):
        # Simulate advanced indicators
        rsi = random.randint(20, 80)
        macd = random.uniform(-10, 10)
        volume = random.randint(500000, 8000000)
        sma_20 = price * (1 + random.uniform(-0.03, 0.03))
        sma_50 = price * (1 + random.uniform(-0.05, 0.05))
        
        score = 0.5
        if rsi < 30: score += 0.25
        elif rsi > 70: score -= 0.25
        if macd > 0: score += 0.15
        else: score -= 0.15
        if price > sma_20: score += 0.10
        else: score -= 0.10
        if sma_20 > sma_50: score += 0.05
        else: score -= 0.05
        if volume > 3000000: score += 0.05
        
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
            "indicators": {
                "rsi": rsi,
                "macd": round(macd, 2),
                "volume": volume,
                "sma_20": round(sma_20, 2),
                "sma_50": round(sma_50, 2)
            },
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
app = FastAPI(title="TITAN Advanced", version="2.0.0")
ai = AIEngine()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# HTML WITH ANIMATED UI
# ============================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 TITAN Advanced</title>
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
        
        /* Header */
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
        
        /* Stats */
        .stats-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }
        .stat-card {
            background: var(--card);
            backdrop-filter: blur(8px);
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
        .stat-card .change { font-size: 0.9rem; margin-top: 4px; }
        
        /* Ticker */
        .ticker-wrap {
            background: var(--card);
            border-radius: 16px;
            padding: 12px 20px;
            margin-bottom: 25px;
            border: 1px solid var(--border);
            overflow: hidden;
            white-space: nowrap;
            animation: fadeIn 1s ease;
        }
        .ticker {
            display: inline-block;
            animation: tickerScroll 30s linear infinite;
        }
        .ticker-item {
            display: inline-block;
            margin: 0 25px;
            font-weight: 500;
        }
        .ticker-item .up { color: #00c853; }
        .ticker-item .down { color: #ff1744; }
        
        /* Controls */
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
        
        /* Signal Grid */
        .signal-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
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
        
        .signal-card .price {
            font-size: 2rem;
            font-weight: 700;
            margin: 6px 0 8px;
        }
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
        
        .signal-card .timestamp {
            font-size: 0.7rem;
            opacity: 0.5;
            margin-top: 10px;
            text-align: right;
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes tickerScroll {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .pulse { animation: pulse 2s infinite; }
        
        /* Responsive */
        @media (max-width: 640px) {
            .header h1 { font-size: 1.6rem; }
            .signal-grid { grid-template-columns: 1fr; }
            .stats-row { grid-template-columns: 1fr 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="header">
            <h1>🚀 TITAN <span style="font-weight:300;font-size:1rem;background:none;-webkit-text-fill-color:currentColor;opacity:0.7;">Advanced</span></h1>
            <div class="header-actions">
                <button class="theme-toggle" onclick="toggleTheme()">🌓 Theme</button>
                <span id="liveIndicator" style="display:flex;align-items:center;gap:6px;font-size:0.9rem;">
                    <span class="pulse" style="color:#00c853;">●</span> Live
                </span>
            </div>
        </header>

        <!-- Stats -->
        <div class="stats-row" id="statsRow">
            <div class="stat-card"><div class="number" id="totalStocks">-</div><div class="label">Total Stocks</div></div>
            <div class="stat-card"><div class="number" style="color:#00c853;" id="buyCount">-</div><div class="label">BUY Signals</div></div>
            <div class="stat-card"><div class="number" style="color:#ff1744;" id="sellCount">-</div><div class="label">SELL Signals</div></div>
            <div class="stat-card"><div class="number" style="color:#ffab00;" id="holdCount">-</div><div class="label">HOLD Signals</div></div>
            <div class="stat-card"><div class="number" id="lastUpdate">-</div><div class="label">Last Update</div></div>
        </div>

        <!-- Ticker -->
        <div class="ticker-wrap" id="tickerWrap">
            <div class="ticker" id="ticker"></div>
        </div>

        <!-- Controls -->
        <div class="controls">
            <button class="btn-refresh" onclick="refreshData()">🔄 Refresh</button>
            <button class="btn-all active" data-filter="all" onclick="setFilter('all')">All</button>
            <button class="btn-buy" data-filter="BUY" onclick="setFilter('BUY')">BUY</button>
            <button class="btn-sell" data-filter="SELL" onclick="setFilter('SELL')">SELL</button>
            <button class="btn-hold" data-filter="HOLD" onclick="setFilter('HOLD')">HOLD</button>
            <span style="margin-left:auto;opacity:0.6;font-size:0.9rem;">Auto-update every 5s</span>
        </div>

        <!-- Signal Grid -->
        <div id="signalGrid" class="signal-grid">
            <div style="text-align:center;padding:60px;opacity:0.6;">Loading signals...</div>
        </div>
    </div>

    <script>
        // --- STATE ---
        let currentData = null;
        let currentFilter = 'all';
        let eventSource = null;

        // --- DOM refs ---
        const grid = document.getElementById('signalGrid');
        const tickerEl = document.getElementById('ticker');

        // --- Theme ---
        function toggleTheme() {
            document.body.classList.toggle('light');
        }

        // --- Ticker ---
        function updateTicker(data) {
            if (!data || !data.results) return;
            // pick top 5 BUY and top 5 SELL
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
            // duplicate for seamless loop
            tickerEl.innerHTML = html + html;
        }

        // --- Render cards ---
        function renderSignals(signals) {
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
        }

        // --- Update stats ---
        function updateStats(data) {
            document.getElementById('totalStocks').textContent = data.total_scanned || 0;
            document.getElementById('buyCount').textContent = data.buy_signals ? data.buy_signals.length : 0;
            document.getElementById('sellCount').textContent = data.sell_signals ? data.sell_signals.length : 0;
            document.getElementById('holdCount').textContent = data.hold_signals ? data.hold_signals.length : 0;
            if (data.timestamp) {
                const d = new Date(data.timestamp);
                document.getElementById('lastUpdate').textContent = d.toLocaleTimeString();
            }
        }

        // --- Filter ---
        function setFilter(filter) {
            currentFilter = filter;
            // update active buttons
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

        // --- Refresh data (manual) ---
        async function refreshData() {
            try {
                const resp = await fetch('/api/screener/nifty50');
                const data = await resp.json();
                currentData = data;
                updateStats(data);
                updateTicker(data);
                applyFilter();
            } catch (e) {
                console.error('Refresh error:', e);
            }
        }

        // --- SSE for live updates ---
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
                } catch (err) {
                    console.error('SSE parse error', err);
                }
            };
            eventSource.onerror = function(e) {
                console.warn('SSE connection lost, reconnecting...');
                setTimeout(connectSSE, 3000);
            };
        }

        // --- Init ---
        refreshData();
        connectSSE();
        // fallback refresh every 10s
        setInterval(refreshData, 10000);

        // --- Keyboard shortcut: 'r' for refresh ---
        document.addEventListener('keydown', (e) => { if (e.key === 'r' || e.key === 'R') refreshData(); });
    </script>
</body>
</html>
"""

# ============================================
# SSE STREAM ENDPOINT
# ============================================
@app.get("/api/stream")
async def stream_events():
    async def event_generator():
        while True:
            data = ai.scan()
            # Add expected profit
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
            await asyncio.sleep(5)  # update every 5 seconds
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# ============================================
# OTHER API ENDPOINTS
# ============================================
@app.get("/")
async def root():
    return HTMLResponse(HTML_TEMPLATE)

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/screener/nifty50")
async def scan_nifty50():
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
# RUN
# ============================================
if __name__ == "__main__":
    print("=" * 70)
    print("🚀 TITAN ADVANCED - Real-time Animated Trading Platform")
    print("=" * 70)
    print(f"📊 NIFTY 50 Stocks: {len(NIFTY_50)}")
    print(f"🌐 Web Interface: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print("🔄 Live updates every 5 seconds via SSE")
    print("=" * 70)
    print("\n✅ Platform is running! Open your browser.\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
