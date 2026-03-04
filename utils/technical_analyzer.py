"""
ตัวคำนวณ technical indicators
ปรับปรุงมาจาก stock_analyzer.py
"""

import pandas as pd
import numpy as np

class TechnicalAnalyzer:
    """คำนวณตัวชี้วัดทางเทคนิค"""
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(prices):
        """MACD"""
        exp1 = prices.ewm(span=12).mean()
        exp2 = prices.ewm(span=26).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9).mean()
        histogram = macd - signal
        return macd, signal, histogram
    
    @staticmethod
    def calculate_stochastic(df, k=14, d=3):
        """Stochastic"""
        low_min = df['Low'].rolling(window=k).min()
        high_max = df['High'].rolling(window=k).max()
        stoch_k = 100 * ((df['Close'] - low_min) / (high_max - low_min))
        stoch_d = stoch_k.rolling(window=d).mean()
        return stoch_k, stoch_d
    
    @staticmethod
    def calculate_bollinger_bands(prices, period=20, std=2):
        """Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std_dev = prices.rolling(window=period).std()
        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)
        return upper, sma, lower
    
    @staticmethod
    def calculate_atr(df, period=14):
        """Average True Range"""
        high = df['High']
        low = df['Low']
        close = df['Close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
    
    def add_all_indicators(self, df):
        """เพิ่ม indicators ทั้งหมดลงใน DataFrame"""
        
        # RSI
        df['RSI_14'] = self.calculate_rsi(df['Close'])
        df['RSI_7'] = self.calculate_rsi(df['Close'], period=7)
        
        # MACD
        df['MACD'], df['Signal'], df['Histogram'] = self.calculate_macd(df['Close'])
        
        # Stochastic
        df['Stoch_K'], df['Stoch_D'] = self.calculate_stochastic(df)
        
        # Bollinger Bands
        df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = self.calculate_bollinger_bands(df['Close'])
        
        # Moving Averages
        df['MA5'] = df['Close'].rolling(5).mean()
        df['MA10'] = df['Close'].rolling(10).mean()
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA50'] = df['Close'].rolling(50).mean()
        df['MA200'] = df['Close'].rolling(200).mean() if len(df) > 200 else None
        
        # Volume
        df['Volume_MA20'] = df['Volume'].rolling(20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA20']
        
        # ATR
        df['ATR'] = self.calculate_atr(df)
        df['ATR_Pct'] = (df['ATR'] / df['Close']) * 100
        
        # Support/Resistance
        df['Resistance_20'] = df['High'].rolling(20).max()
        df['Support_20'] = df['Low'].rolling(20).min()
        df['Resistance_50'] = df['High'].rolling(50).max() if len(df) > 50 else None
        df['Support_50'] = df['Low'].rolling(50).min() if len(df) > 50 else None
        
        return df
    
    def analyze_hunter_strategy(self, df, bid_volumes=None, offer_volumes=None):
        """วิเคราะห์ตามกลยุทธ์นายพราน"""
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        result = {
            'strategies': [],
            'primary': None,
            'signals': []
        }
        
        # ===== 1. Whale Rider (ตามวอลุ่ม) =====
        if bid_volumes and offer_volumes and len(bid_volumes) >= 3:
            bid_3 = sum(bid_volumes[:3])
            offer_3 = sum(offer_volumes[:3])
            ratio = bid_3 / offer_3 if offer_3 > 0 else 0
            
            if ratio >= 2:
                result['strategies'].append({
                    'name': '🐋 Whale Rider',
                    'action': 'ตามช้อน',
                    'confidence': 'สูง',
                    'desc': f'วอลุ่มซื้อหนา {ratio:.2f} เท่า'
                })
                result['primary'] = 'whale_rider'
                result['signals'].append('🟢 วอลุ่มซื้อหนา')
        
        # ===== 2. จับจังหวะกลับตัว =====
        rsi_condition = last['RSI_14'] < 30 or last['RSI_7'] < 25
        price_near_support = last['Support_20'] and last['Close'] <= last['Support_20'] * 1.02
        
        if rsi_condition and price_near_support:
            result['strategies'].append({
                'name': '🎯 จับจังหวะกลับตัว',
                'action': 'รอซื้อ',
                'confidence': 'ปานกลาง',
                'desc': f'RSI {last["RSI_14"]:.1f} ใกล้แนวรับ'
            })
            if not result['primary']:
                result['primary'] = 'reversal'
            result['signals'].append('🟡 RSI Oversold + ใกล้แนวรับ')
        
        # ===== 3. หนีทันที =====
        if bid_volumes and offer_volumes and len(offer_volumes) >= 3:
            offer_3 = sum(offer_volumes[:3])
            bid_3 = sum(bid_volumes[:3])
            ratio = offer_3 / bid_3 if bid_3 > 0 else 0
            
            if ratio >= 2:
                result['strategies'].append({
                    'name': '💀 หนีทันที',
                    'action': 'ขาย/ชอร์ต',
                    'confidence': 'สูง',
                    'desc': f'วอลุ่มขายหนา {ratio:.2f} เท่า'
                })
                result['primary'] = 'panic'
                result['signals'].append('🔴 วอลุ่มขายหนา')
        
        rsi_overbought = last['RSI_14'] > 70
        price_near_resistance = last['Resistance_20'] and last['Close'] >= last['Resistance_20'] * 0.98
        
        if rsi_overbought and price_near_resistance:
            result['strategies'].append({
                'name': '💀 หนีทันที',
                'action': 'ขาย',
                'confidence': 'ปานกลาง',
                'desc': f'RSI {last["RSI_14"]:.1f} ใกล้แนวต้าน'
            })
            result['primary'] = 'panic'
            result['signals'].append('🔴 RSI Overbought + ใกล้แนวต้าน')
        
        # ===== 4. รอซ้ำยามเปลี้ย =====
        volume_low = last['Volume_Ratio'] < 0.7
        rsi_mid = 40 <= last['RSI_14'] <= 60
        price_sideways = abs(last['Close'] - last['MA20']) / last['MA20'] < 0.02 if last['MA20'] else False
        
        if volume_low and rsi_mid and price_sideways:
            result['strategies'].append({
                'name': '🎣 รอซ้ำยามเปลี้ย',
                'action': 'เฝ้าดู',
                'confidence': 'ต่ำ',
                'desc': 'ตลาดเงียบ รอจังหวะ'
            })
            if not result['primary']:
                result['primary'] = 'tired'
            result['signals'].append('⚪ ตลาดเงียบ')
        
        # ===== 5. ตามเทรน =====
        ma_bullish = last['MA5'] > last['MA10'] > last['MA20'] if last['MA20'] else False
        macd_bullish = last['MACD'] > last['Signal']
        volume_high = last['Volume_Ratio'] > 1.2
        
        if ma_bullish and macd_bullish and volume_high:
            result['strategies'].append({
                'name': '📈 ตามเทรน',
                'action': 'ถือ/ซื้อเพิ่ม',
                'confidence': 'สูง',
                'desc': 'เทรนขาขึ้นชัดเจน'
            })
            result['primary'] = 'trend'
            result['signals'].append('🟢 เทรนขาขึ้น')
        
        return result
    
    def get_buy_sell_points(self, df, cutloss_pct=5, takeprofit_pct=10):
        """คำนวณจุดซื้อขาย"""
        last = df.iloc[-1]
        price = last['Close']
        
        points = {
            'current_price': price,
            'buy_points': [],
            'sell_points': [],
            'cut_loss': price * (1 - cutloss_pct/100),
            'take_profit_1': price * (1 + takeprofit_pct/100),
            'take_profit_2': price * (1 + takeprofit_pct*2/100)
        }
        
        # จุดซื้อจาก indicators
        if last['Support_20']:
            points['buy_points'].append(round(last['Support_20'], 2))
        if last['MA50'] and not pd.isna(last['MA50']):
            points['buy_points'].append(round(last['MA50'], 2))
        if last['BB_Lower']:
            points['buy_points'].append(round(last['BB_Lower'], 2))
        
        # จุดขายจาก indicators
        if last['Resistance_20']:
            points['sell_points'].append(round(last['Resistance_20'], 2))
        if last['BB_Upper']:
            points['sell_points'].append(round(last['BB_Upper'], 2))
        
        # จุด Take Profit
        points['sell_points'].append(round(points['take_profit_1'], 2))
        points['sell_points'].append(round(points['take_profit_2'], 2))
        
        # Remove duplicates and sort
        points['buy_points'] = sorted(list(set(points['buy_points'])))
        points['sell_points'] = sorted(list(set(points['sell_points'])))
        
        return points
