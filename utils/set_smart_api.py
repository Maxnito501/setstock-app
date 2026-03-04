"""
SET Smart API Wrapper
- ใช้ API Key: 025e08a9-3f69-4ccf-8339-f8d37c03a4af
- ดึงข้อมูลราคาและงบการเงินจาก SET
"""

import requests
import time
import streamlit as st
from datetime import datetime

class SETSmartAPI:
    def __init__(self):
        self.api_key = "025e08a9-3f69-4ccf-8339-f8d37c03a4af"
        self.base_url = "https://www.setsmart.com/api/listed-company-api"
        self.last_call = 0
        self.min_interval = 3  # เว้น 3 วินาทีตามที่ SET กำหนด
        self.use_mock = False  # False = ใช้ API จริง, True = ใช้ข้อมูลตัวอย่าง
        
    def _call_api(self, endpoint, params):
        """เรียก API พร้อม rate limit"""
        # รอให้ถึง interval
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        
        # เพิ่ม api_key ใน params (SET Smart รับผ่าน query parameter)
        params['api_key'] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, params=params, timeout=10)
            self.last_call = time.time()
            
            if response.status_code == 200:
                return response.json()
            else:
                st.warning(f"⚠️ API Error {response.status_code} - ใช้ข้อมูลตัวอย่างแทน")
                return None
        except Exception as e:
            st.warning(f"⚠️ Connection Error - ใช้ข้อมูลตัวอย่างแทน")
            return None
    
    def get_eod_price(self, symbol):
        """ดึงราคาปิดล่าสุด"""
        
        # ถ้าใช้ mock data
        if self.use_mock:
            return self._get_mock_price(symbol)
        
        # เรียก API จริง
        data = self._call_api("eod-price-by-symbol", {"symbol": symbol})
        
        if data and data.get('price'):
            return {
                'success': True,
                'price': data.get('price', 0),
                'change': data.get('change', 0),
                'change_pct': data.get('changePercent', 0),
                'volume': data.get('volume', 0),
                'high': data.get('high', 0),
                'low': data.get('low', 0),
                'open': data.get('open', 0),
                'prev_close': data.get('prevClose', 0),
                'timestamp': datetime.now().isoformat()
            }
        
        # fallback เป็น mock data
        return self._get_mock_price(symbol)
    
    def get_financial_data(self, symbol):
        """ดึงข้อมูลงบการเงิน"""
        
        # ถ้าใช้ mock data
        if self.use_mock:
            return self._get_mock_financial(symbol)
        
        # เรียก API จริง
        data = self._call_api("financial-data-and-ratio-by-symbol", {"symbol": symbol})
        
        if data:
            return {
                'success': True,
                'pe': data.get('pe', 0),
                'pbv': data.get('pbv', 0),
                'roe': data.get('roe', 0),
                'de': data.get('de', 0),
                'dividend_yield': data.get('dividendYield', 0),
                'eps': data.get('eps', 0),
                'eps_growth': data.get('epsGrowth', 0),
                'profit_margin': data.get('profitMargin', 0),
                'revenue': data.get('revenue', 0),
                'net_profit': data.get('netProfit', 0),
                'timestamp': datetime.now().isoformat()
            }
        
        # fallback เป็น mock data
        return self._get_mock_financial(symbol)
    
    def _get_mock_price(self, symbol):
        """ข้อมูลราคาตัวอย่าง"""
        mock_prices = {
            'PTT': {'price': 35.25, 'change': -1.50, 'change_pct': -4.08, 'volume': 15000000},
            'SCB': {'price': 142.50, 'change': -3.50, 'change_pct': -2.40, 'volume': 5000000},
            'TISCO': {'price': 112.00, 'change': -1.50, 'change_pct': -1.32, 'volume': 2000000},
            'AOT': {'price': 48.50, 'change': -3.00, 'change_pct': -5.83, 'volume': 8000000},
            'HMPRO': {'price': 6.60, 'change': -0.45, 'change_pct': -6.38, 'volume': 10000000},
            'SIRI': {'price': 1.33, 'change': -0.14, 'change_pct': -9.52, 'volume': 30000000},
            'PTG': {'price': 8.70, 'change': -0.55, 'change_pct': -5.95, 'volume': 5000000},
            'PTTEP': {'price': 146.00, 'change': -4.00, 'change_pct': -2.67, 'volume': 3000000},
            'KBANK': {'price': 156.00, 'change': -4.00, 'change_pct': -2.50, 'volume': 4000000},
            'CPALL': {'price': 55.50, 'change': -2.50, 'change_pct': -4.31, 'volume': 6000000},
            'BDMS': {'price': 28.50, 'change': -1.50, 'change_pct': -5.00, 'volume': 7000000},
        }
        
        data = mock_prices.get(symbol, {
            'price': 100.00,
            'change': -2.00,
            'change_pct': -1.96,
            'volume': 1000000
        })
        
        return {
            'success': True,
            'price': data['price'],
            'change': data['change'],
            'change_pct': data['change_pct'],
            'volume': data['volume'],
            'high': data['price'] * 1.02,
            'low': data['price'] * 0.98,
            'open': data['price'] * 0.99,
            'prev_close': data['price'] + abs(data['change']),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_mock_financial(self, symbol):
        """ข้อมูลงบการเงินตัวอย่าง"""
        mock_financial = {
            'PTT': {
                'pe': 10.2, 'pbv': 1.2, 'roe': 15.3, 'de': 0.6,
                'dividend_yield': 5.0, 'eps': 3.2, 'eps_growth': 8.2,
                'profit_margin': 10.5, 'revenue': 1000000, 'net_profit': 105000
            },
            'SCB': {
                'pe': 8.1, 'pbv': 0.8, 'roe': 10.2, 'de': 1.0,
                'dividend_yield': 7.6, 'eps': 14.2, 'eps_growth': 5.8,
                'profit_margin': 35.2, 'revenue': 500000, 'net_profit': 176000
            },
            'TISCO': {
                'pe': 10.3, 'pbv': 1.5, 'roe': 16.1, 'de': 0.8,
                'dividend_yield': 7.7, 'eps': 11.2, 'eps_growth': 8.1,
                'profit_margin': 40.5, 'revenue': 300000, 'net_profit': 121500
            },
            'AOT': {
                'pe': 30.5, 'pbv': 3.2, 'roe': 8.1, 'de': 0.2,
                'dividend_yield': 0.0, 'eps': 1.8, 'eps_growth': 5.2,
                'profit_margin': 30.1, 'revenue': 800000, 'net_profit': 240800
            },
            'HMPRO': {
                'pe': 18.2, 'pbv': 3.1, 'roe': 22.7, 'de': 1.7,
                'dividend_yield': 3.0, 'eps': 0.35, 'eps_growth': 10.2,
                'profit_margin': 8.3, 'revenue': 700000, 'net_profit': 58100
            },
            'SIRI': {
                'pe': 8.2, 'pbv': 1.0, 'roe': 9.1, 'de': 2.0,
                'dividend_yield': 2.0, 'eps': 0.16, 'eps_growth': 5.1,
                'profit_margin': 15.2, 'revenue': 400000, 'net_profit': 60800
            },
            'PTG': {
                'pe': 9.5, 'pbv': 1.3, 'roe': 11.2, 'de': 1.1,
                'dividend_yield': 3.5, 'eps': 0.92, 'eps_growth': 7.2,
                'profit_margin': 12.3, 'revenue': 600000, 'net_profit': 73800
            }
        }
        
        data = mock_financial.get(symbol, {
            'pe': 12.0, 'pbv': 1.2, 'roe': 12.0, 'de': 1.0,
            'dividend_yield': 4.0, 'eps': 2.0, 'eps_growth': 7.0,
            'profit_margin': 15.0, 'revenue': 500000, 'net_profit': 75000
        })
        
        return {
            'success': True,
            'pe': data['pe'],
            'pbv': data['pbv'],
            'roe': data['roe'],
            'de': data['de'],
            'dividend_yield': data['dividend_yield'],
            'eps': data['eps'],
            'eps_growth': data['eps_growth'],
            'profit_margin': data['profit_margin'],
            'revenue': data['revenue'],
            'net_profit': data['net_profit'],
            'timestamp': datetime.now().isoformat()
        }
    
    def set_use_mock(self, use_mock):
        """สลับโหมด mock data"""
        self.use_mock = use_mock
        if use_mock:
            st.info("🔧 ใช้ข้อมูลตัวอย่าง (Mock Mode)")
        else:
            st.success("✅ ใช้ API จริง (Live Mode)")
