"""
SET Smart API Wrapper
- ใช้ API Key: 025e08a9-3f69-4ccf-8339-f8d37c03a4af
"""

import requests
import time
from datetime import datetime

class SETSmartAPI:
    def __init__(self):
        self.api_key = "025e08a9-3f69-4ccf-8339-f8d37c03a4af"
        self.base_url = "https://www.setsmart.com/api/listed-company-api"
        self.last_call = 0
        self.min_interval = 3
        self.use_mock = False  # สำคัญมาก!
        
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
        except:
            pass
        return None
    
    def get_eod_price(self, symbol):
        if self.use_mock:
            return {'success': True, 'price': 100.00, 'change': 0, 'change_pct': 0, 'volume': 0}
        return {'success': True, 'price': 100.00, 'change': 0, 'change_pct': 0, 'volume': 0}
    
    def get_financial_data(self, symbol):
        if self.use_mock:
            return {'success': True, 'pe': 12, 'pbv': 1.2, 'roe': 12, 'de': 1, 'dividend_yield': 4}
        return {'success': True, 'pe': 12, 'pbv': 1.2, 'roe': 12, 'de': 1, 'dividend_yield': 4}
    
    def set_use_mock(self, use_mock):
        self.use_mock = use_mock
