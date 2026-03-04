"""
Hybrid Fetcher - ใช้ tvdatafeed เท่านั้น (ไม่ใช้ tvkit)
"""

import asyncio
import aiohttp
import pandas as pd
from datetime import datetime
import json
import os
from tvDatafeed import TvDatafeed, Interval

class HybridFetcher:
    """ตัวดึงข้อมูลแบบ Hybrid"""
    
    def __init__(self, config_file='config/hybrid_config.json'):
        self.config = self.load_config(config_file)
        self.settrade_url = self.config.get('settrade_service_url', 'http://localhost:5001')
        self.timeout = aiohttp.ClientTimeout(total=10)
        self.tv = TvDatafeed()
        
    def load_config(self, config_file):
        """โหลดการตั้งค่า"""
        default_config = {
            'settrade_service_url': 'http://localhost:5001',
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
    
    def get_tradingview_data(self, symbol, interval='1D', bars=200):
        """ดึงข้อมูลจาก TradingView (tvdatafeed)"""
        try:
            # แปลง interval
            interval_map = {
                '1D': Interval.in_daily,
                '1W': Interval.in_weekly,
                '1M': Interval.in_monthly,
                '1h': Interval.in_1_hour,
                '4h': Interval.in_4_hour,
                '15m': Interval.in_15_minute
            }
            tv_interval = interval_map.get(interval, Interval.in_daily)
            
            # ดึงข้อมูล
            data = self.tv.get_hist(
                symbol=symbol,
                exchange='SET',
                interval=tv_interval,
                n_bars=bars
            )
            
            if data is None or data.empty:
                return {
                    'success': False,
                    'error': f'No data for {symbol}'
                }
            
            return {
                'success': True,
                'df': data,
                'symbol': symbol,
                'source': 'tradingview',
                'last_price': data['close'].iloc[-1],
                'last_volume': data['volume'].iloc[-1]
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
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source': 'settrade'
            }
    
    def get_sync_data(self, symbol, interval='1D', bars=200, get_bid_offer=True):
        """ดึงข้อมูลแบบ synchronous"""
        # ดึงข้อมูลหลักจาก TradingView
        tv_result = self.get_tradingview_data(symbol, interval, bars)
        
        result = {
            'symbol': symbol,
            'tradingview': tv_result,
            'bid_offer': None,
            'timestamp': datetime.now().isoformat()
        }
        
        # ถ้าได้ข้อมูลจาก TradingView และต้องการ Bid/Offer
        if get_bid_offer and tv_result['success']:
            # เรียก bid_offer แบบ synchronous
            try:
                import requests
                response = requests.get(f"{self.settrade_url}/bid_offer/{symbol}", timeout=5)
                if response.status_code == 200:
                    result['bid_offer'] = {
                        'success': True,
                        'bid': response.json().get('bid', []),
                        'offer': response.json().get('offer', [])
                    }
            except:
                pass
        
        return result
    
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
