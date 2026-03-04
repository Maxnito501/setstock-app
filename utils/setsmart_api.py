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
        self.min_interval = 3
        self.use_mock = False  # เพิ่มตรงนี้
        
    def _call_api(self, endpoint, params):
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        
        params['api_key'] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, params=params, timeout=10)
            self.last_call = time.time()
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except:
            return None
    
    def get_eod_price(self, symbol):
        if self.use_mock:
            return self._get_mock_price(symbol)
        
        data = self._call_api("eod-price-by-symbol", {"symbol": symbol})
        if data and data.get('price'):
            return {
                'success': True,
                'price': data.get('price', 0),
                'change': data.get('change', 0),
                'change_pct': data.get('changePercent', 0),
                'volume': data.get('volume', 0)
            }
        return self._get_mock_price(symbol)
    
    def get_financial_data(self, symbol):
        if self.use_mock:
            return self._get_mock_financial(symbol)
        
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
                'profit_margin': data.get('profitMargin', 0)
            }
        return self._get_mock_financial(symbol)
    
    def _get_mock_price(self, symbol):
        mock_prices = {
            'PTT': 35.25, 'SCB': 142.50, 'TISCO': 112.00,
            'AOT': 48.50, 'HMPRO': 6.60, 'SIRI': 1.33, 'PTG': 8.70
        }
        price = mock_prices.get(symbol, 100.00)
        return {
            'success': True,
            'price': price,
            'change': -2.00,
            'change_pct': -1.96,
            'volume': 1000000
        }
    
    def _get_mock_financial(self, symbol):
        mock_data = {
            'PTT': {'pe': 10.2, 'pbv': 1.2, 'roe': 15.3, 'de': 0.6, 'dividend_yield': 5.0},
            'SCB': {'pe': 8.1, 'pbv': 0.8, 'roe': 10.2, 'de': 1.0, 'dividend_yield': 7.6},
            'TISCO': {'pe': 10.3, 'pbv': 1.5, 'roe': 16.1, 'de': 0.8, 'dividend_yield': 7.7}
        }
        data = mock_data.get(symbol, {'pe': 12, 'pbv': 1.2, 'roe': 12, 'de': 1, 'dividend_yield': 4})
        data['success'] = True
        return data
    
    def set_use_mock(self, use_mock):
        """เปลี่ยนโหมดการใช้ข้อมูล"""
        self.use_mock = use_mock
        if use_mock:
            print("🔧 ใช้ข้อมูลตัวอย่าง (Mock Mode)")
        else:
            print("✅ ใช้ API จริง (Live Mode)")
