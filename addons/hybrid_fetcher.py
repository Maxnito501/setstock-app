"""
Hybrid Fetcher - รวม TradingView + Settrade API
- ใช้ TradingView (tvkit) เป็นหลัก (Python 3.13)
- เรียก Settrade API จาก Docker สำหรับ Bid/Offer
"""

import asyncio
import aiohttp
import pandas as pd
from datetime import datetime
import json
import os

# ตรวจสอบว่ามี tvkit หรือไม่
try:
    from tvkit.api.chart.ohlcv import OHLCV
    TVKIT_AVAILABLE = True
except ImportError:
    TVKIT_AVAILABLE = False
    print("⚠️ ไม่พบ tvkit กรุณาติดตั้ง: pip install tvkit")

class HybridFetcher:
    """ตัวดึงข้อมูลแบบ Hybrid"""
    
    def __init__(self, config_file='config/hybrid_config.json'):
        self.config = self.load_config(config_file)
        self.settrade_url = self.config.get('settrade_service_url', 'http://localhost:5001')
        self.timeout = aiohttp.ClientTimeout(total=10)
        
    def load_config(self, config_file):
        """โหลดการตั้งค่า"""
        default_config = {
            'settrade_service_url': 'http://localhost:5001',
            'tv_symbol_format': 'SET:{}',
            'default_interval': '1D',
            'default_bars': 200
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return {**default_config, **json.load(f)}
        except:
            pass
            
        return default_config
    
    async def get_tradingview_data(self, symbol, interval='1D', bars=200):
        """ดึงข้อมูลจาก TradingView (tvkit)"""
        if not TVKIT_AVAILABLE:
            return {
                'success': False,
                'error': 'tvkit not installed',
                'solution': 'pip install tvkit'
            }
        
        try:
            tv_symbol = self.config['tv_symbol_format'].format(symbol)
            
            async with OHLCV() as client:
                bars_data = await client.get_historical_ohlcv(
                    tv_symbol,
                    interval=interval,
                    bars_count=bars
                )
                
                if not bars_data:
                    return {
                        'success': False,
                        'error': f'No data for {tv_symbol}'
                    }
                
                # แปลงเป็น DataFrame
                df_data = []
                for bar in bars_data:
                    df_data.append({
                        'datetime': bar.timestamp,
                        'open': bar.open,
                        'high': bar.high,
                        'low': bar.low,
                        'close': bar.close,
                        'volume': bar.volume
                    })
                
                df = pd.DataFrame(df_data)
                df.set_index('datetime', inplace=True)
                
                return {
                    'success': True,
                    'df': df,
                    'symbol': symbol,
                    'source': 'tradingview',
                    'last_price': df['close'].iloc[-1],
                    'last_volume': df['volume'].iloc[-1]
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source': 'tradingview'
            }
    
    async def get_settrade_bid_offer(self, symbol):
        """ดึง Bid/Offer 5 ช่องจาก Settrade API (ผ่าน Docker)"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(
                    f"{self.settrade_url}/bid_offer/{symbol}"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'success': True,
                            'bid': data.get('bid', []),
                            'offer': data.get('offer', []),
                            'source': 'settrade'
                        }
                    else:
                        return {
                            'success': False,
                            'error': f"HTTP {response.status}",
                            'source': 'settrade'
                        }
        except asyncio.TimeoutError:
            return {
                'success': False,
                'error': 'Connection timeout',
                'source': 'settrade'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source': 'settrade'
            }
    
    async def get_hybrid_data(self, symbol, interval='1D', bars=200, get_bid_offer=True):
        """ดึงข้อมูลแบบครบวงจร"""
        
        # 1. ดึงข้อมูลหลักจาก TradingView
        tv_result = await self.get_tradingview_data(symbol, interval, bars)
        
        result = {
            'symbol': symbol,
            'tradingview': tv_result,
            'bid_offer': None,
            'timestamp': datetime.now().isoformat()
        }
        
        # 2. ดึง Bid/Offer ถ้าต้องการ
        if get_bid_offer and tv_result['success']:
            bid_offer = await self.get_settrade_bid_offer(symbol)
            result['bid_offer'] = bid_offer
        
        return result
    
    def get_sync_data(self, symbol, interval='1D', bars=200, get_bid_offer=True):
        """เวอร์ชัน synchronous (เรียกใช้ใน Streamlit)"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.get_hybrid_data(symbol, interval, bars, get_bid_offer)
            )
        finally:
            loop.close()
    
    def analyze_volume_layers(self, bid_offer_data, top_n=3):
        """วิเคราะห์วอลุ่มตามกลยุทธ์นายพราน"""
        if not bid_offer_data or not bid_offer_data.get('success'):
            return None
        
        bid = bid_offer_data.get('bid', [])
        offer = bid_offer_data.get('offer', [])
        
        bid_vol = sum(b.get('volume', 0) for b in bid[:top_n])
        offer_vol = sum(o.get('volume', 0) for o in offer[:top_n])
        
        ratio = bid_vol / offer_vol if offer_vol > 0 else 0
        
        if ratio >= 2:
            strategy = '🐋 Whale Rider'
            action = 'ตามช้อน'
            desc = f'วอลุ่มซื้อหนา {ratio:.2f} เท่า'
        elif ratio >= 1.5:
            strategy = '🎯 จับจังหวะกลับตัว'
            action = 'รอดู'
            desc = f'วอลุ่มซื้อเริ่มเข้า {ratio:.2f} เท่า'
        elif ratio <= 0.5:
            strategy = '💀 หนีทันที'
            action = 'ขาย/ชอร์ต'
            desc = f'วอลุ่มขายหนา {1/ratio:.2f} เท่า'
        else:
            strategy = '🎣 รอซ้ำยามเปลี้ย'
            action = 'เฝ้าดู'
            desc = f'วอลุ่มสมดุล {ratio:.2f} เท่า'
        
        return {
            'strategy': strategy,
            'action': action,
            'desc': desc,
            'bid_3': bid_vol,
            'offer_3': offer_vol,
            'ratio': ratio
        }
