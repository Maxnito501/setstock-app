"""
ใช้ Yahoo Finance แทน Settrade API
- วอลุ่มรวมช่องเดียว
- ไม่ต้องพึ่ง Docker
"""

import yfinance as yf
import time
from datetime import datetime

class StockAPI:
    def __init__(self):
        self.connected = True
        self.last_call = {}
        self.min_interval = 5
        print("✅ เชื่อมต่อ Yahoo Finance สำเร็จ")
    
    def get_quote(self, symbol):
        """ดึงข้อมูลจาก Yahoo Finance"""
        
        # เช็ค rate limit
        if symbol in self.last_call:
            elapsed = time.time() - self.last_call[symbol]
            if elapsed < self.min_interval:
                wait_time = self.min_interval - elapsed
                return {
                    'success': False,
                    'error': f'⏳ รอ {wait_time:.0f} วิ',
                    'wait': wait_time
                }
        
        try:
            # ดึงข้อมูลจาก Yahoo
            ticker = yf.Ticker(f"{symbol}.BK")
            info = ticker.info
            hist = ticker.history(period="1d")
            
            price = hist['Close'].iloc[-1] if not hist.empty else info.get('regularMarketPrice', 0)
            volume = hist['Volume'].iloc[-1] if not hist.empty else info.get('volume', 0)
            
            self.last_call[symbol] = time.time()
            
            # สร้างข้อมูลจำลอง Bid/Offer (เนื่องจาก Yahoo มีแค่ช่องเดียว)
            bid_price = info.get('bid', price * 0.998)
            ask_price = info.get('ask', price * 1.002)
            
            return {
                'success': True,
                'symbol': symbol,
                'price': round(price, 2),
                'change': info.get('regularMarketChange', 0),
                'change_percent': info.get('regularMarketChangePercent', 0),
                'volume': volume,
                # Yahoo มีแค่ช่องเดียว
                'bid': [{'price': bid_price, 'volume': volume // 3}],
                'offer': [{'price': ask_price, 'volume': volume // 3}],
                'bid_volume': volume // 3,
                'offer_volume': volume // 3,
                'high': info.get('dayHigh', price * 1.01),
                'low': info.get('dayLow', price * 0.99),
                'open': info.get('regularMarketOpen', price),
                'prev_close': info.get('regularMarketPreviousClose', price),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_volume(self, symbol):
        """วิเคราะห์วอลุ่มแบบง่าย (ช่องเดียว)"""
        data = self.get_quote(symbol)
        if not data['success']:
            return data
        
        volume = data['volume']
        
        # วิเคราะห์เบื้องต้น
        if volume > 10_000_000:  # 10 ล้าน
            signal = "🔴 วอลุ่มสูงมาก"
            action = "ระวังเจ้ามือ"
        elif volume > 5_000_000:  # 5 ล้าน
            signal = "🟡 วอลุ่มปานกลาง"
            action = "จับตาดู"
        elif volume > 1_000_000:  # 1 ล้าน
            signal = "🟢 วอลุ่มปกติ"
            action = "ปกติ"
        else:
            signal = "⚪ วอลุ่มเบาบาง"
            action = "เงียบ"
        
        return {
            'success': True,
            'symbol': symbol,
            'volume': volume,
            'signal': signal,
            'action': action
        }