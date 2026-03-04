"""
ตัวดึงข้อมูลจาก Yahoo Finance
- มีระบบ Cache และ Refresh
- รองรับการ Clear Cache
- รองรับหุ้นไทย
"""

import yfinance as yf
import pandas as pd
import json
import time
import os
from datetime import datetime, timedelta
from functools import wraps

# ================== Cache Manager ==================

class CacheManager:
    """จัดการ Cache สำหรับ Yahoo Finance"""
    
    def __init__(self, cache_file='yahoo_cache.json'):
        self.cache_file = cache_file
        self.cache = self.load_cache()
        self.min_interval = 60  # 60 วินาที
    
    def load_cache(self):
        """โหลด cache จากไฟล์"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except:
            return {}
    
    def save_cache(self):
        """บันทึก cache ลงไฟล์"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def clear_cache(self):
        """ล้าง cache ทั้งหมด"""
        self.cache = {}
        self.save_cache()
        print("✅ ล้าง cache เรียบร้อย")
    
    def get(self, symbol, data_type='price'):
        """ดึงข้อมูลจาก cache ถ้ายังไม่หมดอายุ"""
        key = f"{symbol}_{data_type}"
        
        if key in self.cache:
            cached_time = datetime.fromisoformat(self.cache[key]['time'])
            if datetime.now() - cached_time < timedelta(seconds=self.min_interval):
                return self.cache[key]['data']
        
        return None
    
    def set(self, symbol, data, data_type='price'):
        """บันทึกข้อมูลลง cache"""
        key = f"{symbol}_{data_type}"
        self.cache[key] = {
            'time': datetime.now().isoformat(),
            'data': data
        }
        self.save_cache()
    
    def remove(self, symbol, data_type='price'):
        """ลบ cache ของหุ้นตัวเดียว"""
        key = f"{symbol}_{data_type}"
        if key in self.cache:
            del self.cache[key]
            self.save_cache()
            return True
        return False

# ================== Retry Decorator ==================

def retry(max_attempts=3, delay=2):
    """Decorator สำหรับ retry เมื่อเรียกข้อมูลล้มเหลว"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    result = func(*args, **kwargs)
                    if result is not None:
                        return result
                except Exception as e:
                    print(f"⚠️ Attempt {attempt + 1} failed: {e}")
                
                if attempt < max_attempts - 1:
                    print(f"⏳ รอ {delay} วินาที แล้วลองใหม่...")
                    time.sleep(delay)
            
            return None
        return wrapper
    return decorator

# ================== Main Fetcher ==================

class YahooFetcher:
    """ตัวดึงข้อมูลจาก Yahoo Finance สำหรับแอป"""
    
    def __init__(self):
        self.cache = CacheManager()
        
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
            'TU': 'TU.BK', 'WHA': 'WHA.BK', 'HMPRO': 'HMPRO.BK'
        }
    
    def format_symbol(self, symbol):
        """แปลงรหัสหุ้นให้อยู่ในรูปแบบ Yahoo"""
        symbol = symbol.upper().strip()
        if symbol.endswith('.BK'):
            return symbol
        if symbol in self.thai_stocks:
            return self.thai_stocks[symbol]
        return f"{symbol}.BK"
    
    def test_connection(self, symbol):
        """ทดสอบการเชื่อมต่อ Yahoo Finance"""
        try:
            yahoo_symbol = self.format_symbol(symbol)
            ticker = yf.Ticker(yahoo_symbol)
            df = ticker.history(period='1d')
            return not df.empty
        except:
            return False
    
    def force_refresh(self, symbol, period='3mo'):
        """บังคับโหลดใหม่ ไม่ใช้ cache"""
        # ลบ cache เดิม
        self.cache.remove(symbol, 'full')
        self.cache.remove(symbol, 'price')
        
        # โหลดใหม่
        return self.fetch_data(symbol, period, force=True)
    
    def clear_all_cache(self):
        """ล้าง cache ทั้งหมด"""
        self.cache.clear_cache()
    
    @retry(max_attempts=2, delay=1)
    def fetch_data(self, symbol, period='3mo', force=False):
        """ดึงข้อมูลหุ้น (ใช้ cache ถ้ามี)"""
        
        # ถ้าไม่ force ให้ลองจาก cache ก่อน
        if not force:
            cached = self.cache.get(symbol, 'full')
            if cached:
                return cached
        
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
            
            result = {
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
                'low_52w': info.get('fiftyTwoWeekLow', df['Low'].min()),
                'last_update': datetime.now().isoformat()
            }
            
            # เก็บเข้า cache
            self.cache.set(symbol, result, 'full')
            
            return result
            
        except Exception as e:
            return None
    
    def get_current_price(self, symbol):
        """ดึงเฉพาะราคาปัจจุบัน (เร็ว)"""
        
        # ลองจาก cache ก่อน
        cached = self.cache.get(symbol, 'price')
        if cached:
            return cached
        
        try:
            yahoo_symbol = self.format_symbol(symbol)
            ticker = yf.Ticker(yahoo_symbol)
            df = ticker.history(period='1d')
            
            if df.empty:
                return None
            
            result = {
                'price': df['Close'].iloc[-1],
                'volume': df['Volume'].iloc[-1],
                'time': datetime.now().isoformat()
            }
            
            # เก็บเข้า cache (เวลาสั้นกว่า)
            self.cache.min_interval = 30  # 30 วิ สำหรับราคา
            self.cache.set(symbol, result, 'price')
            self.cache.min_interval = 60  # reset
            
            return result
            
        except:
            return None
