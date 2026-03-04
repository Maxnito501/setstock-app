"""
SET Smart API Wrapper + Yahoo Finance Hybrid
- ข้อมูลพื้นฐานจาก SETSMART API
- ราคาจาก Yahoo Finance (เผื่อ API Error)
"""

import requests
import time
import yfinance as yf
from datetime import datetime

class SETSmartAPI:
    def __init__(self):
        self.api_key = "025e08a9-3f69-4ccf-8339-f8d37c03a4af"
        self.base_url = "https://www.setsmart.com/api/listed-company-api"
        self.last_call = 0
        self.min_interval = 3
        self.use_mock = False  # True = ใช้ข้อมูลตัวอย่าง, False = ใช้ API จริง
        
    def _call_api(self, endpoint, params):
        """เรียก API พร้อม rate limit"""
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
                print(f"API Error {response.status_code}")
                return None
        except Exception as e:
            print(f"Connection Error: {e}")
            return None
    
    def get_price_from_yahoo(self, symbol):
        """ดึงราคาปิดจาก Yahoo Finance (เผื่อ API ไม่ได้)"""
        try:
            ticker = yf.Ticker(f"{symbol}.BK")
            data = ticker.history(period="2d")
            if not data.empty and len(data) >= 2:
                price = data['Close'].iloc[-1]
                prev_close = data['Close'].iloc[-2]
                change = price - prev_close
                change_pct = (change / prev_close) * 100 if prev_close else 0
                
                return {
                    'success': True,
                    'price': round(price, 2),
                    'change': round(change, 2),
                    'change_pct': round(change_pct, 2),
                    'volume': int(data['Volume'].iloc[-1]) if not data['Volume'].isna().all() else 0,
                    'source': 'yahoo',
                    'timestamp': datetime.now().isoformat()
                }
            elif not data.empty:
                # มีแค่วันเดียว
                price = data['Close'].iloc[-1]
                return {
                    'success': True,
                    'price': round(price, 2),
                    'change': 0,
                    'change_pct': 0,
                    'volume': int(data['Volume'].iloc[-1]) if not data['Volume'].isna().all() else 0,
                    'source': 'yahoo',
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Yahoo Error for {symbol}: {e}")
        
        return {'success': False}
    
    def get_eod_price(self, symbol):
        """ดึงราคาปิดล่าสุด (ลอง SETSMART ก่อน ถ้าไม่ได้ใช้ Yahoo)"""
        
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
                'source': 'setsmart',
                'timestamp': datetime.now().isoformat()
            }
        
        # fallback เป็น Yahoo
        yahoo_data = self.get_price_from_yahoo(symbol)
        if yahoo_data['success']:
            return yahoo_data
        
        # fallback สุดท้ายเป็น mock data
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
                'source': 'setsmart',
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
            'ADVANC': {'price': 240.00, 'change': -5.00, 'change_pct': -2.04, 'volume': 3000000},
            'INTUCH': {'price': 70.00, 'change': -2.00, 'change_pct': -2.78, 'volume': 2000000},
            'TOP': {'price': 48.00, 'change': -2.00, 'change_pct': -4.00, 'volume': 3000000},
            'BANPU': {'price': 8.50, 'change': -0.50, 'change_pct': -5.56, 'volume': 10000000},
            'CHG': {'price': 3.50, 'change': -0.20, 'change_pct': -5.41, 'volume': 15000000},
            'COM7': {'price': 25.00, 'change': -1.00, 'change_pct': -3.85, 'volume': 5000000},
            'EA': {'price': 45.00, 'change': -2.00, 'change_pct': -4.26, 'volume': 4000000},
            'LH': {'price': 7.00, 'change': -0.30, 'change_pct': -4.11, 'volume': 8000000},
            'MINT': {'price': 28.00, 'change': -1.00, 'change_pct': -3.45, 'volume': 6000000},
            'RATCH': {'price': 32.00, 'change': -1.00, 'change_pct': -3.03, 'volume': 3000000},
            'SAWAD': {'price': 45.00, 'change': -2.00, 'change_pct': -4.26, 'volume': 2000000},
            'TRUE': {'price': 5.50, 'change': -0.30, 'change_pct': -5.17, 'volume': 20000000},
            'WHA': {'price': 4.50, 'change': -0.20, 'change_pct': -4.26, 'volume': 15000000},
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
            'source': 'mock',
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_mock_financial(self, symbol):
        """ข้อมูลงบการเงินตัวอย่าง"""
        mock_financial = {
            'PTT': {'pe': 10.2, 'pbv': 1.2, 'roe': 15.3, 'de': 0.6, 'dividend_yield': 5.0, 'eps': 3.2, 'eps_growth': 8.2, 'profit_margin': 10.5},
            'SCB': {'pe': 8.1, 'pbv': 0.8, 'roe': 10.2, 'de': 1.0, 'dividend_yield': 7.6, 'eps': 14.2, 'eps_growth': 5.8, 'profit_margin': 35.2},
            'TISCO': {'pe': 10.3, 'pbv': 1.5, 'roe': 16.1, 'de': 0.8, 'dividend_yield': 7.7, 'eps': 11.2, 'eps_growth': 8.1, 'profit_margin': 40.5},
            'AOT': {'pe': 30.5, 'pbv': 3.2, 'roe': 8.1, 'de': 0.2, 'dividend_yield': 0.0, 'eps': 1.8, 'eps_growth': 5.2, 'profit_margin': 30.1},
            'HMPRO': {'pe': 18.2, 'pbv': 3.1, 'roe': 22.7, 'de': 1.7, 'dividend_yield': 3.0, 'eps': 0.35, 'eps_growth': 10.2, 'profit_margin': 8.3},
            'SIRI': {'pe': 8.2, 'pbv': 1.0, 'roe': 9.1, 'de': 2.0, 'dividend_yield': 2.0, 'eps': 0.16, 'eps_growth': 5.1, 'profit_margin': 15.2},
            'PTG': {'pe': 9.5, 'pbv': 1.3, 'roe': 11.2, 'de': 1.1, 'dividend_yield': 3.5, 'eps': 0.92, 'eps_growth': 7.2, 'profit_margin': 12.3},
            'PTTEP': {'pe': 8.0, 'pbv': 1.1, 'roe': 14.0, 'de': 0.5, 'dividend_yield': 4.0, 'eps': 18.0, 'eps_growth': 10.0, 'profit_margin': 15.0},
            'KBANK': {'pe': 9.0, 'pbv': 0.9, 'roe': 9.0, 'de': 1.1, 'dividend_yield': 5.0, 'eps': 16.0, 'eps_growth': 5.0, 'profit_margin': 32.0},
            'CPALL': {'pe': 25.0, 'pbv': 4.0, 'roe': 18.0, 'de': 1.8, 'dividend_yield': 2.0, 'eps': 2.2, 'eps_growth': 15.0, 'profit_margin': 4.0},
            'BDMS': {'pe': 25.0, 'pbv': 3.0, 'roe': 15.0, 'de': 0.5, 'dividend_yield': 1.5, 'eps': 1.1, 'eps_growth': 9.0, 'profit_margin': 12.0},
            'ADVANC': {'pe': 20.0, 'pbv': 8.0, 'roe': 28.0, 'de': 0.8, 'dividend_yield': 4.0, 'eps': 12.0, 'eps_growth': 12.0, 'profit_margin': 18.0},
            'INTUCH': {'pe': 15.0, 'pbv': 2.5, 'roe': 18.0, 'de': 0.3, 'dividend_yield': 5.0, 'eps': 4.7, 'eps_growth': 10.0, 'profit_margin': 20.0},
            'TOP': {'pe': 9.0, 'pbv': 1.0, 'roe': 12.0, 'de': 0.7, 'dividend_yield': 5.0, 'eps': 5.3, 'eps_growth': 7.0, 'profit_margin': 8.0},
            'BANPU': {'pe': 8.0, 'pbv': 0.9, 'roe': 11.0, 'de': 0.8, 'dividend_yield': 6.0, 'eps': 1.1, 'eps_growth': 6.0, 'profit_margin': 7.0},
        }
        
        data = mock_financial.get(symbol, {
            'pe': 12.0,
            'pbv': 1.2,
            'roe': 12.0,
            'de': 1.0,
            'dividend_yield': 4.0,
            'eps': 2.0,
            'eps_growth': 7.0,
            'profit_margin': 15.0
        })
        
        data['success'] = True
        data['source'] = 'mock'
        return data
    
    def set_use_mock(self, use_mock):
        """เปลี่ยนโหมดการใช้ข้อมูล"""
        self.use_mock = use_mock
        print(f"เปลี่ยนโหมด: {'Mock' if use_mock else 'Live'}")
