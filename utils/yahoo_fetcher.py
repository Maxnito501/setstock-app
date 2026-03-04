"""
ตัวดึงข้อมูลจาก Yahoo Finance
ปรับปรุงมาจาก stock_analyzer.py
"""

import yfinance as yf
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from functools import wraps

# ================== Cache ==================

class YahooCache:
    def __init__(self, cache_file='yahoo_cache.json'):
        self.cache_file = cache_file
        self.cache = self.load_cache()
        self.min_interval = 60
    
    def load_cache(self):
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def save_cache(self):
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def get(self, symbol, data_type='price'):
        key = f"{symbol}_{data_type}"
        if key in self.cache:
            cached_time = datetime.fromisoformat(self.cache[key]['time'])
            if datetime.now() - cached_time < timedelta(seconds=self.min_interval):
                return self.cache[key]['data']
        return None
    
    def set(self, symbol, data, data_type='price'):
        key = f"{symbol}_{data_type}"
        self.cache[key] = {
            'time': datetime.now().isoformat(),
            'data': data
        }
        self.save_cache()

# ================== Retry ==================

def retry(max_attempts=3, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    result = func(*args, **kwargs)
                    if result is not None:
                        return result
                except:
                    pass
                if attempt < max_attempts - 1:
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

# ================== Main Fetcher ==================

class YahooFetcher:
    """ตัวดึงข้อมูลจาก Yahoo Finance สำหรับแอป"""
    
    def __init__(self):
        self.cache = YahooCache()
        
        # รายชื่อหุ้นไทยที่รองรับ
        self.thai_stocks = {
            'ADVANC': 'ADVANC.BK', 'AOT': 'AOT.BK', 'BDMS': 'BDMS.BK',
            'BH': 'BH.BK', 'BTS': 'BTS.BK', 'CPALL': 'CPALL.BK',
            'CPF': 'CPF.BK', 'CRC': 'CRC.BK', 'DTAC': 'DTAC.BK',
            'GULF': 'GULF.BK', 'INTUCH': 'INTUCH.BK', 'IVL': 'IVL.BK',
            'KBANK': 'KBANK.BK', 'KTB': 'KTB.BK', 'PTT': 'PTT.BK',
            'PTTEP': 'PTTEP.BK', 'SCB': 'SCB.BK', 'SCC': 'SCC.BK',
            'SIRI': 'SIRI.BK', 'TISCO': 'TISCO.BK', 'TRUE': 'TRUE.BK',
            'BANPU': 'BANPU.BK', 'CHG': 'CHG.BK', 'COM7': 'COM7.BK',
            'EA': 'EA.BK', 'JAS': 'JAS.BK', 'LH': 'LH.BK',
            'MINT': 'MINT.BK', 'PTG': 'PTG.BK', 'RATCH': 'RATCH.BK',
            'SAWAD': 'SAWAD.BK', 'TMB': 'TMB.BK', 'TOP': 'TOP.BK',
            'TU': 'TU.BK', 'WHA': 'WHA.BK'
        }
    
    def format_symbol(self, symbol):
        """แปลงรหัสหุ้นให้อยู่ในรูปแบบ Yahoo"""
        symbol = symbol.upper().strip()
        if symbol.endswith('.BK'):
            return symbol
        if symbol in self.thai_stocks:
            return self.thai_stocks[symbol]
        return f"{symbol}.BK"
    
    @retry(max_attempts=2, delay=1)
    def fetch_data(self, symbol, period='3mo'):
        """ดึงข้อมูลหุ้น (ใช้ในแอป)"""
        try:
            yahoo_symbol = self.format_symbol(symbol)
            ticker = yf.Ticker(yahoo_symbol)
            
            # ดึงข้อมูลย้อนหลัง
            df = ticker.history(period=period)
            if df.empty:
                return None
            
            # ดึงข้อมูลพื้นฐาน
            info = ticker.info
            
            # คำนวณค่าเฉลี่ย volume
            df['Volume_MA20'] = df['Volume'].rolling(20).mean()
            
            return {
                'df': df,
                'info': info,
                'symbol': symbol,
                'yahoo_symbol': yahoo_symbol,
                'company_name': info.get('longName', info.get('shortName', symbol)),
                'sector': info.get('sector', 'ไม่ระบุ'),
                'last_price': df['Close'].iloc[-1],
                'last_volume': df['Volume'].iloc[-1],
                'avg_volume_20': df['Volume'].tail(20).mean(),
                'high_52w': info.get('fiftyTwoWeekHigh', df['High'].max()),
                'low_52w': info.get('fiftyTwoWeekLow', df['Low'].min())
            }
        except Exception as e:
            return None
