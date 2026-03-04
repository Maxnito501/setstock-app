"""
Technical Analyzer - คำนวณตัวชี้วัดทางเทคนิค
"""

import pandas as pd
import numpy as np

class TechnicalAnalyzer:
    """คำนวณตัวชี้วัดทางเทคนิค"""
    
    def calculate_rsi(self, prices, period=14):
        """คำนวณ RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """คำนวณ MACD"""
        exp1 = prices.ewm(span=fast, adjust=False).mean()
        exp2 = prices.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram
    
    def calculate_atr(self, df, period=14):
        """คำนวณ ATR"""
        high = df['High'] if 'High' in df else df['high']
        low = df['Low'] if 'Low' in df else df['low']
        close = df['Close'] if 'Close' in df else df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
    
    def add_all_indicators(self, df):
        """เพิ่ม indicators ทั้งหมด"""
        
        # ทำสำเนาเพื่อไม่ให้กระทบต้นฉบับ
        df = df.copy()
        
        # แก้ไขชื่อคอลัมน์ (tvdatafeed ใช้ตัวเล็ก)
        if 'close' in df.columns and 'Close' not in df.columns:
            df['Close'] = df['close']
        if 'high' in df.columns and 'High' not in df.columns:
            df['High'] = df['high']
        if 'low' in df.columns and 'Low' not in df.columns:
            df['Low'] = df['low']
        if 'open' in df.columns and 'Open' not in df.columns:
            df['Open'] = df['open']
        if 'volume' in df.columns and 'Volume' not in df.columns:
            df['Volume'] = df['volume']
        
        # RSI
        df['RSI_14'] = self.calculate_rsi(df['Close'])
        df['RSI_7'] = self.calculate_rsi(df['Close'], period=7)
        
        # MACD
        macd, signal, hist = self.calculate_macd(df['Close'])
        df['MACD'] = macd
        df['Signal'] = signal
        df['Histogram'] = hist
        
        # Moving Averages
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA50'] = df['Close'].rolling(50).mean()
        df['MA200'] = df['Close'].rolling(200).mean() if len(df) > 200 else None
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(20).mean()
        df['BB_Upper'] = df['BB_Middle'] + 2 * df['Close'].rolling(20).std()
        df['BB_Lower'] = df['BB_Middle'] - 2 * df['Close'].rolling(20).std()
        
        # Volume
        df['Volume_MA20'] = df['Volume'].rolling(20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA20']
        
        # Support/Resistance
        df['Support_20'] = df['Low'].rolling(20).min()
        df['Resistance_20'] = df['High'].rolling(20).max()
        
        # ATR
        df['ATR'] = self.calculate_atr(df)
        df['ATR_Pct'] = (df['ATR'] / df['Close']) * 100
        
        return df
    
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
        if not pd.isna(last.get('Support_20', 0)):
            points['buy_points'].append(round(last['Support_20'], 2))
        if not pd.isna(last.get('MA50', 0)):
            points['buy_points'].append(round(last['MA50'], 2))
        if not pd.isna(last.get('BB_Lower', 0)):
            points['buy_points'].append(round(last['BB_Lower'], 2))
        
        # จุดขายจาก indicators
        if not pd.isna(last.get('Resistance_20', 0)):
            points['sell_points'].append(round(last['Resistance_20'], 2))
        if not pd.isna(last.get('BB_Upper', 0)):
            points['sell_points'].append(round(last['BB_Upper'], 2))
        
        # จุด Take Profit
        points['sell_points'].append(round(points['take_profit_1'], 2))
        points['sell_points'].append(round(points['take_profit_2'], 2))
        
        # Remove duplicates and sort
        points['buy_points'] = sorted(list(set(points['buy_points'])))
        points['sell_points'] = sorted(list(set(points['sell_points'])))
        
        return points
