"""
โมดูลสำหรับวิเคราะห์ทางเทคนิค
"""

import pandas as pd
import numpy as np

class TechnicalAnalyzer:
    def __init__(self):
        """เริ่มต้นตัววิเคราะห์ทางเทคนิค"""
        pass
    
    def calculate_rsi(self, prices, period=14):
        """
        คำนวณ RSI (Relative Strength Index)
        
        Parameters:
        prices: ราคา (Series)
        period: ระยะเวลา (default 14)
        
        Returns:
        RSI values
        """
        # คำนวณการเปลี่ยนแปลงของราคา
        delta = prices.diff()
        
        # แยกกำไรและขาดทุน
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # คำนวณ RS และ RSI
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """
        คำนวณ MACD (Moving Average Convergence Divergence)
        
        Returns:
        MACD line, Signal line, Histogram
        """
        # คำนวณ EMA
        exp1 = prices.ewm(span=fast, adjust=False).mean()
        exp2 = prices.ewm(span=slow, adjust=False).mean()
        
        # MACD line
        macd = exp1 - exp2
        
        # Signal line
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        
        # Histogram
        histogram = macd - signal_line
        
        return macd, signal_line, histogram
    
    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """
        คำนวณ Bollinger Bands
        
        Returns:
        Upper band, Middle band, Lower band
        """
        # คำนวณ moving average
        middle = prices.rolling(window=period).mean()
        
        # คำนวณ standard deviation
        std = prices.rolling(window=period).std()
        
        # คำนวณ upper และ lower bands
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return upper, middle, lower
    
    def calculate_moving_averages(self, prices, periods=[20, 50, 200]):
        """
        คำนวณ Moving Averages หลายช่วง
        """
        mas = {}
        for period in periods:
            mas[f'MA{period}'] = prices.rolling(window=period).mean()
        return mas
    
    def calculate_volume_oscillator(self, volume, fast=5, slow=10):
        """
        คำนวณ Volume Oscillator
        """
        fast_ma = volume.rolling(window=fast).mean()
        slow_ma = volume.rolling(window=slow).mean()
        vo = ((fast_ma - slow_ma) / slow_ma) * 100
        return vo
    
    def find_support_resistance(self, prices, window=20):
        """
        หาแนวรับและแนวต้าน
        """
        # หาจุดสูงสุดและต่ำสุดในแต่ละช่วง
        highs = prices.rolling(window=window).max()
        lows = prices.rolling(window=window).min()
        
        # หาแนวต้านล่าสุด
        recent_highs = highs.tail(10).unique()
        resistance = sorted(recent_highs, reverse=True)[:3] if len(recent_highs) > 0 else []
        
        # หาแนวรับล่าสุด
        recent_lows = lows.tail(10).unique()
        support = sorted(recent_lows)[:3] if len(recent_lows) > 0 else []
        
        return {
            'support_levels': [round(x, 2) for x in support if x > 0],
            'resistance_levels': [round(x, 2) for x in resistance if x > 0],
            'current_support': round(lows.iloc[-1], 2) if not pd.isna(lows.iloc[-1]) else 0,
            'current_resistance': round(highs.iloc[-1], 2) if not pd.isna(highs.iloc[-1]) else 0
        }
    
    def identify_trend(self, prices, ma_short=20, ma_long=50):
        """
        ระบุแนวโน้ม (ขาขึ้น/ขาลง/ sideways)
        """
        if len(prices) < ma_long:
            return "ข้อมูลไม่พอ"
        
        ma_short_val = prices.rolling(window=ma_short).mean().iloc[-1]
        ma_long_val = prices.rolling(window=ma_long).mean().iloc[-1]
        current_price = prices.iloc[-1]
        price_ma50 = prices.rolling(window=50).mean().iloc[-1]
        
        # ตรวจสอบแนวโน้ม
        if ma_short_val > ma_long_val and current_price > price_ma50:
            return "ขาขึ้น"
        elif ma_short_val < ma_long_val and current_price < price_ma50:
            return "ขาลง"
        else:
            return "Sideways"
    
    def elliot_wave_simple(self, prices, window=20):
        """
        วิเคราะห์ Elliot Wave แบบง่าย
        """
        if len(prices) < window * 5:
            return "ข้อมูลไม่พอสำหรับวิเคราะห์ Elliot Wave"
        
        # หาจุดสูงสุดและต่ำสุด
        from scipy.signal import argrelextrema
        
        # หา local maxima
        local_max = argrelextrema(prices.values, np.greater, order=5)[0]
        local_min = argrelextrema(prices.values, np.less, order=5)[0]
        
        # รวมจุดสำคัญทั้งหมด
        important_points = sorted(local_max.tolist() + local_min.tolist())
        
        # วิเคราะห์รูปแบบ
        if len(important_points) >= 5:
            # ตรวจสอบว่าราคาล่าสุดอยู่ตรงไหน
            last_price = prices.iloc[-1]
            last_high = prices.iloc[local_max[-1]] if len(local_max) > 0 else last_price
            last_low = prices.iloc[local_min[-1]] if len(local_min) > 0 else last_price
            
            # คำนวณว่าราคาอยู่ในช่วงไหน
            price_range = last_high - last_low
            if price_range > 0:
                position = (last_price - last_low) / price_range
            else:
                position = 0.5
            
            if position > 0.8:
                wave = "Wave 3 (กำลังขึ้นแรง) หรือ Wave C (ใกล้จบ)"
            elif position < 0.2:
                wave = "Wave 2 (กำลังลง) หรือใกล้จบ correction"
            else:
                wave = "Wave 4 (sideways) หรือระหว่างทาง"
            
            return {
                'wave_count': f"พบ {len(important_points)} จุดสำคัญ",
                'wave_position': wave,
                'last_high': round(last_high, 2),
                'last_low': round(last_low, 2)
            }
        
        return {
            'wave_count': "ไม่พบรูปแบบที่ชัดเจน",
            'wave_position': "ไม่สามารถระบุได้",
            'last_high': 0,
            'last_low': 0
        }
    
    def get_signal_summary(self, prices, volume):
        """
        สรุปสัญญาณทางเทคนิค
        """
        signals = []
        
        # ตรวจสอบ RSI
        rsi = self.calculate_rsi(prices)
        if len(rsi) > 0:
            latest_rsi = rsi.iloc[-1]
            if latest_rsi > 70:
                signals.append({"indicator": "RSI", "signal": "ขาย", "value": f"{latest_rsi:.1f}"})
            elif latest_rsi < 30:
                signals.append({"indicator": "RSI", "signal": "ซื้อ", "value": f"{latest_rsi:.1f}"})
            else:
                signals.append({"indicator": "RSI", "signal": "กลาง", "value": f"{latest_rsi:.1f}"})
        
        # ตรวจสอบ MACD
        macd, signal, hist = self.calculate_macd(prices)
        if len(hist) > 0:
            latest_hist = hist.iloc[-1]
            prev_hist = hist.iloc[-2] if len(hist) > 1 else 0
            
            if latest_hist > 0 and prev_hist <= 0:
                signals.append({"indicator": "MACD", "signal": "ซื้อ", "value": f"{latest_hist:.3f}"})
            elif latest_hist < 0 and prev_hist >= 0:
                signals.append({"indicator": "MACD", "signal": "ขาย", "value": f"{latest_hist:.3f}"})
            else:
                signals.append({"indicator": "MACD", "signal": "ถือ", "value": f"{latest_hist:.3f}"})
        
        # ตรวจสอบ Moving Average
        ma20 = prices.rolling(window=20).mean().iloc[-1]
        ma50 = prices.rolling(window=50).mean().iloc[-1]
        current = prices.iloc[-1]
        
        if current > ma20 and ma20 > ma50:
            signals.append({"indicator": "MA", "signal": "ซื้อ", "value": f"{current:.2f}"})
        elif current < ma20 and ma20 < ma50:
            signals.append({"indicator": "MA", "signal": "ขาย", "value": f"{current:.2f}"})
        else:
            signals.append({"indicator": "MA", "signal": "กลาง", "value": f"{current:.2f}"})
        
        # ตรวจสอบ Volume
        avg_vol = volume.tail(20).mean()
        curr_vol = volume.iloc[-1]
        vol_ratio = curr_vol / avg_vol if avg_vol > 0 else 1
        
        if vol_ratio > 1.5:
            signals.append({"indicator": "Volume", "signal": "สูง", "value": f"{vol_ratio:.2f}x"})
        elif vol_ratio < 0.5:
            signals.append({"indicator": "Volume", "signal": "ต่ำ", "value": f"{vol_ratio:.2f}x"})
        else:
            signals.append({"indicator": "Volume", "signal": "ปกติ", "value": f"{vol_ratio:.2f}x"})
        
        return signals