"""
โมดูลสำหรับดึงข้อมูลหุ้น
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

class DataFetcher:
    def __init__(self):
        """เริ่มต้นตัวดึงข้อมูล"""
        self.cache = {}
        self.last_update = {}
    
    def get_stock_data(self, symbol, period="3mo", interval="1d"):
        """
        ดึงข้อมูลหุ้นจาก Yahoo Finance
        
        Parameters:
        symbol: รหัสหุ้น (เช่น ADVANC, PTT)
        period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        
        Returns:
        DataFrame ของข้อมูลหุ้น
        """
        try:
            # เพิ่ม .BK สำหรับหุ้นไทย
            ticker = yf.Ticker(f"{symbol}.BK")
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                # ลองไม่มี .BK
                ticker = yf.Ticker(symbol)
                df = ticker.history(period=period, interval=interval)
            
            return df
            
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def get_current_price(self, symbol):
        """
        ดึงราคาปัจจุบัน
        """
        data = self.get_stock_data(symbol, period="1d", interval="1m")
        if data is not None and not data.empty:
            return data['Close'].iloc[-1]
        return None
    
    def get_historical_data(self, symbol, start_date, end_date):
        """
        ดึงข้อมูลตามช่วงวันที่ระบุ
        """
        try:
            ticker = yf.Ticker(f"{symbol}.BK")
            df = ticker.history(start=start_date, end=end_date)
            return df
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_multiple_stocks(self, symbols, period="3mo"):
        """
        ดึงข้อมูลหลายหุ้นพร้อมกัน
        """
        results = {}
        for symbol in symbols:
            df = self.get_stock_data(symbol, period)
            if df is not None:
                results[symbol] = df
            time.sleep(0.5)  # พักครึ่งวินาทีเพื่อไม่ให้ถูกบล็อก
        return results
    
    def get_market_overview(self):
        """
        ข้อมูลภาพรวมตลาด (mock data สำหรับตอนนี้)
        """
        return {
            'set_index': 1523.45,
            'set_change': 12.34,
            'set_change_pct': 0.82,
            'volume': 45.2e9,
            'foreign_net': 2.1e9,
            'market_cap': 19.8e12,
            'advance': 245,
            'decline': 178,
            'unchanged': 45
        }
    
    def get_stock_info(self, symbol):
        """
        ข้อมูลพื้นฐานของหุ้น
        """
        try:
            ticker = yf.Ticker(f"{symbol}.BK")
            info = ticker.info
            return {
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'high_52w': info.get('fiftyTwoWeekHigh', 0),
                'low_52w': info.get('fiftyTwoWeekLow', 0)
            }
        except:
            return {
                'name': symbol,
                'sector': 'N/A',
                'industry': 'N/A',
                'market_cap': 0,
                'pe_ratio': 0,
                'dividend_yield': 0,
                'high_52w': 0,
                'low_52w': 0
            }