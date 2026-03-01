"""
ใช้ Yahoo Finance แทน Settrade API
- วอลุ่มรวมช่องเดียว
- ใช้งานง่าย ไม่ต้องติดตั้ง Settrade
"""

import yfinance as yf
import time
from datetime import datetime

class StockAPI:
    def __init__(self):
        """เริ่มต้นเชื่อมต่อ Yahoo Finance"""
        self.connected = True
        self.last_call = {}
        self.min_interval = 5
        print("✅ เชื่อมต่อ Yahoo Finance สำเร็จ")
    
    def get_quote(self, symbol):
        """ดึงข้อมูลราคาและวอลุ่มจาก Yahoo Finance"""
        
        # เช็คอัตราการเรียก
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
            
            # ราคาล่าสุด
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                volume = hist['Volume'].iloc[-1]
            else:
                price = info.get('regularMarketPrice', 0)
                volume = info.get('volume', 0)
            
            # ราคาเปลี่ยนแปลง
            change = info.get('regularMarketChange', 0)
            change_percent = info.get('regularMarketChangePercent', 0)
            
            self.last_call[symbol] = time.time()
            
            return {
                'success': True,
                'symbol': symbol,
                'price': round(price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'volume': volume,
                'high': info.get('dayHigh', price),
                'low': info.get('dayLow', price),
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
        """วิเคราะห์วอลุ่มแบบง่าย"""
        data = self.get_quote(symbol)
        if not data['success']:
            return data
        
        volume = data['volume']
        
        # วิเคราะห์ตามขนาดวอลุ่ม
        if volume > 10_000_000:  # 10 ล้าน
            signal = "🔴 วอลุ่มสูงมาก"
            action = "ระวังเจ้ามือ"
            level = "สูง"
        elif volume > 5_000_000:  # 5 ล้าน
            signal = "🟡 วอลุ่มปานกลาง"
            action = "จับตาดู"
            level = "กลาง"
        elif volume > 1_000_000:  # 1 ล้าน
            signal = "🟢 วอลุ่มปกติ"
            action = "ปกติ"
            level = "ปกติ"
        else:
            signal = "⚪ วอลุ่มเบาบาง"
            action = "เงียบ"
            level = "ต่ำ"
        
        return {
            'success': True,
            'symbol': symbol,
            'volume': volume,
            'signal': signal,
            'action': action,
            'level': level
        }
