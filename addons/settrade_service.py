"""
Settrade API Service - สำหรับรันใน Docker
ใช้ Python 3.10 ภายใน container
"""

import sys
import json
from flask import Flask, jsonify
import yfinance as yf

app = Flask(__name__)

# ข้อมูลจำลองสำหรับทดสอบ (จะถูกแทนที่ด้วย Settrade API จริง)
MOCK_BID_OFFER = {
    "ADVANC": {
        "bid": [
            {"price": 248.00, "volume": 15200},
            {"price": 247.50, "volume": 23400},
            {"price": 247.00, "volume": 18100},
            {"price": 246.50, "volume": 12500},
            {"price": 246.00, "volume": 9800}
        ],
        "offer": [
            {"price": 248.50, "volume": 14300},
            {"price": 249.00, "volume": 22100},
            {"price": 249.50, "volume": 16700},
            {"price": 250.00, "volume": 13200},
            {"price": 250.50, "volume": 8900}
        ]
    }
}

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/bid_offer/<symbol>')
def get_bid_offer(symbol):
    """ดึง Bid/Offer 5 ช่อง"""
    symbol = symbol.upper()
    
    # ใช้ mock data ก่อน
    if symbol in MOCK_BID_OFFER:
        return jsonify(MOCK_BID_OFFER[symbol])
    
    # TODO: เรียก Settrade API จริง
    return jsonify({
        "bid": [
            {"price": 100.00, "volume": 10000},
            {"price": 99.50, "volume": 15000},
            {"price": 99.00, "volume": 20000},
            {"price": 98.50, "volume": 12000},
            {"price": 98.00, "volume": 8000}
        ],
        "offer": [
            {"price": 100.50, "volume": 9000},
            {"price": 101.00, "volume": 14000},
            {"price": 101.50, "volume": 18000},
            {"price": 102.00, "volume": 11000},
            {"price": 102.50, "volume": 7000}
        ]
    })

@app.route('/quote/<symbol>')
def get_quote(symbol):
    """ดึงราคา (ใช้ Yahoo เป็น fallback)"""
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        data = ticker.history(period="1d")
        if not data.empty:
            return jsonify({
                "price": data['Close'].iloc[-1],
                "volume": data['Volume'].iloc[-1],
                "high": data['High'].iloc[-1],
                "low": data['Low'].iloc[-1]
            })
    except:
        pass
    
    return jsonify({"error": "No data"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
