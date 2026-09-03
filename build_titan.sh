#!/bin/bash
# build_titan.sh - Complete TITAN Platform Setup

echo "🚀 TITAN PLATFORM - ULTIMATE SETUP"
echo "==================================="
echo ""

# Step 1: Install System Dependencies
echo "📦 Step 1: Installing system dependencies..."
sudo apt update -y
sudo apt install -y docker.io docker-compose python3-pip git curl wget

# Step 2: Create Project
echo "📁 Step 2: Creating project structure..."
mkdir -p ~/titan
cd ~/titan

# Step 3: Create Docker Compose
echo "🐳 Step 3: Creating Docker Compose..."
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: titan
      POSTGRES_USER: titan
      POSTGRES_PASSWORD: titan123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  api:
    image: python:3.11-slim
    working_dir: /app
    ports:
      - "8000:8000"
    volumes:
      - ./api:/app
    command: bash -c "pip install fastapi uvicorn && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
  redis_data:
EOF

# Step 4: Create FastAPI App
echo "🐍 Step 4: Creating FastAPI application..."
mkdir -p api
cat > api/main.py << 'EOF'
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import redis
import psycopg2
import os
from datetime import datetime
import json
import random

app = FastAPI(title="TITAN Trading Platform", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db():
    try:
        conn = psycopg2.connect(
            host="postgres",
            database="titan",
            user="titan",
            password="titan123"
        )
        return conn
    except:
        return None

# Redis connection
def get_redis():
    try:
        r = redis.Redis(host='redis', port=6379, decode_responses=True)
        r.ping()
        return r
    except:
        return None

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

# Generate random stock price
def get_stock_price(symbol):
    base_price = {
        "RELIANCE": 2450, "TCS": 3800, "HDFC": 1650, "INFY": 1450,
        "HINDUNILVR": 2450, "ICICIBANK": 950, "ITC": 440, "SBIN": 620
    }
    price = base_price.get(symbol, 1000 + random.randint(1, 500))
    variation = random.uniform(-0.02, 0.02)
    return round(price * (1 + variation), 2)

# AI Signal Generator
def generate_signal(symbol, price):
    # Simple AI logic (in real app, this would be ML model)
    rsi = random.randint(20, 80)
    macd = random.uniform(-10, 10)
    volume = random.randint(100000, 5000000)
    
    score = 0.5
    
    # RSI logic
    if rsi < 30:
        score += 0.3
    elif rsi > 70:
        score -= 0.3
    
    # MACD logic
    if macd > 0:
        score += 0.2
    else:
        score -= 0.2
    
    # Volume logic
    if volume > 2000000:
        score += 0.1
    
    # Determine action
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

# API Endpoints

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
    db = get_db()
    redis = get_redis()
    return {
        "status": "healthy",
        "database": "connected" if db else "disconnected",
        "redis": "connected" if redis else "disconnected",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/screener/nifty50")
async def scan_nifty50():
    """Scan all NIFTY 50 stocks"""
    results = []
    for symbol in NIFTY_50:
        price = get_stock_price(symbol)
        signal = generate_signal(symbol, price)
        results.append(signal)
    
    # Sort by confidence
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
    """Scan specific stock"""
    if symbol not in NIFTY_50:
        raise HTTPException(status_code=404, detail="Stock not in NIFTY 50")
    
    price = get_stock_price(symbol)
    signal = generate_signal(symbol, price)
    
    # Calculate profit based on capital
    capital = 100000  # Default capital
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
    """Get all NIFTY 50 stocks with current prices"""
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
    """Get specific stock price"""
    if symbol not in NIFTY_50:
        raise HTTPException(status_code=404, detail="Stock not found")
    return {
        "symbol": symbol,
        "price": get_stock_price(symbol),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/market/status")
async def market_status():
    """Get market status"""
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
EOF

# Step 5: Start Everything
echo "🚀 Step 5: Starting services..."
sudo docker-compose up -d

echo ""
echo "✅ TITAN PLATFORM IS READY!"
echo "==================================="
echo "🌐 API Gateway: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "📊 Health Check: http://localhost:8000/health"
echo ""
echo "🔍 Try these endpoints:"
echo "  - Scan NIFTY 50: http://localhost:8000/api/screener/nifty50"
echo "  - Check stock: http://localhost:8000/api/screener/RELIANCE"
echo "  - All stocks: http://localhost:8000/api/stocks"
echo ""
echo "📝 To view logs: sudo docker-compose logs -f"
echo "🛑 To stop: sudo docker-compose down"
