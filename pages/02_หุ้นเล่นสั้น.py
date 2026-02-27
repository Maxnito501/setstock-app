"""
หน้า 2: วิเคราะห์หุ้นเล่นสั้น
แสดงกราฟเทคนิคอล RSI, MACD, Elliot Wave
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime, timedelta

# เพิ่ม path เพื่อให้ import จาก utils ได้
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# ลอง import utils (ถ้ามี)
try:
    from utils.data_fetcher import DataFetcher
    from utils.technical_analysis import TechnicalAnalyzer
    fetcher = DataFetcher()
    analyzer = TechnicalAnalyzer()
    utils_ready = True
except:
    utils_ready = False
    st.warning("⚠️ กำลังใช้โหมดข้อมูลตัวอย่าง (ไม่ได้เชื่อมต่อ utils)")

# กำหนดค่าเพจ
st.set_page_config(
    page_title="หุ้นเล่นสั้น",
    page_icon="⚡",
    layout="wide"
)

# ชื่อหน้า
st.title("⚡ วิเคราะห์หุ้นเล่นสั้น")
st.markdown("---")

# Sidebar สำหรับเลือกหุ้น
with st.sidebar:
    st.subheader("ตั้งค่าการวิเคราะห์")
    
    # เลือกหุ้น
    symbol = st.text_input("รหัสหุ้น", "ADVANC").upper()
    
    # เลือกช่วงเวลา
    period = st.selectbox(
        "ช่วงเวลา",
        ["1mo", "3mo", "6mo", "1y"],
        index=1
    )
    
    st.markdown("---")
    st.markdown("### ตัวชี้วัด")
    show_rsi = st.checkbox("แสดง RSI", value=True)
    show_macd = st.checkbox("แสดง MACD", value=True)
    show_volume = st.checkbox("แสดง Volume", value=True)
    show_elliott = st.checkbox("แสดง Elliot Wave", value=True)

# ฟังก์ชันสร้างข้อมูลตัวอย่าง
def get_sample_data(symbol, period="3mo"):
    """สร้างข้อมูลตัวอย่างสำหรับทดสอบ"""
    np.random.seed(hash(symbol) % 100)
    
    # สร้างวันที่
    if period == "1mo":
        days = 22
    elif period == "3mo":
        days = 66
    elif period == "6mo":
        days = 132
    else:  # 1y
        days = 252
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='B')
    
    # สร้างราคา
    price = 100
    prices = []
    for i in range(days):
        change = np.random.randn() * 2
        price = price * (1 + change/100)
        prices.append(price)
    
    # สร้าง DataFrame
    df = pd.DataFrame({
        'Open': prices * np.random.uniform(0.98, 1.02, days),
        'High': prices * np.random.uniform(1.01, 1.05, days),
        'Low': prices * np.random.uniform(0.95, 0.99, days),
        'Close': prices,
        'Volume': np.random.randint(1000000, 10000000, days)
    }, index=dates)
    
    return df

# ดึงข้อมูล
if utils_ready:
    df = fetcher.get_stock_data(symbol, period=period)
    if df is None or df.empty:
        st.warning(f"ไม่สามารถดึงข้อมูล {symbol} ได้ ใช้ข้อมูลตัวอย่างแทน")
        df = get_sample_data(symbol, period)
else:
    df = get_sample_data(symbol, period)

# แสดงข้อมูลปัจจุบัน
col1, col2, col3, col4 = st.columns(4)

current_price = df['Close'].iloc[-1]
prev_price = df['Close'].iloc[-2]
change = current_price - prev_price
change_pct = (change / prev_price) * 100

with col1:
    st.metric("ราคาปัจจุบัน", f"฿{current_price:.2f}", f"{change:+.2f} ({change_pct:+.2f}%)")
with col2:
    st.metric("สูงสุดวัน", f"฿{df['High'].iloc[-1]:.2f}", "")
with col3:
    st.metric("ต่ำสุดวัน", f"฿{df['Low'].iloc[-1]:.2f}", "")
with col4:
    st.metric("วอลุ่ม", f"{df['Volume'].iloc[-1]:,.0f}", "")

# สร้างกราฟ
st.subheader(f"กราฟราคา {symbol}")

# กำหนดจำนวนแถวในกราฟ
rows = 1
if show_volume:
    rows += 1
if show_rsi:
    rows += 1
if show_macd:
    rows += 1

# สร้าง subplots
fig = make_subplots(
    rows=rows, 
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.05,
    row_heights=[0.4] + [0.2] * (rows - 1)
)

row = 1

# กราฟแท่งเทียน
fig.add_trace(
    go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='ราคา'
    ),
    row=row, col=1
)

# เพิ่ม Moving Averages
fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df['Close'].rolling(window=20).mean(),
        name='MA20',
        line=dict(color='orange', width=1)
    ),
    row=row, col=1
)

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df['Close'].rolling(window=50).mean(),
        name='MA50',
        line=dict(color='blue', width=1)
    ),
    row=row, col=1
)

row += 1

# กราฟ Volume
if show_volume:
    colors = ['red' if df['Open'].iloc[i] > df['Close'].iloc[i] else 'green' 
              for i in range(len(df))]
    
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color=colors
        ),
        row=row, col=1
    )
    row += 1

# กราฟ RSI
if show_rsi:
    # คำนวณ RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=rsi,
            name='RSI',
            line=dict(color='purple', width=2)
        ),
        row=row, col=1
    )
    
    # เส้น RSI 70 และ 30
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=row, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=row, col=1)
    fig.add_hline(y=50, line_dash="dot", line_color="gray", row=row, col=1)
    
    row += 1

# กราฟ MACD
if show_macd:
    # คำนวณ MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal
    
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=macd,
            name='MACD',
            line=dict(color='blue', width=2)
        ),
        row=row, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=signal,
            name='Signal',
            line=dict(color='red', width=2)
        ),
        row=row, col=1
    )
    
    # Histogram
    colors = ['red' if val < 0 else 'green' for val in histogram]
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=histogram,
            name='Histogram',
            marker_color=colors,
            opacity=0.5
        ),
        row=row, col=1
    )

# ปรับแต่ง layout
fig.update_layout(
    title=f"{symbol} - Technical Analysis",
    xaxis_title="วันที่",
    height=200 + rows * 200,
    showlegend=True,
    hovermode='x unified'
)

fig.update_xaxes(rangeslider_visible=False)
fig.update_layout(xaxis_rangeslider_visible=False)

st.plotly_chart(fig, use_container_width=True)

# วิเคราะห์ทางเทคนิค
st.markdown("---")
st.subheader("📊 วิเคราะห์ทางเทคนิค")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### ตัวชี้วัดหลัก")
    
    # RSI ปัจจุบัน
    if 'rsi' in locals() and len(rsi) > 0:
        current_rsi = rsi.iloc[-1]
        rsi_status = "Overbought" if current_rsi > 70 else "Oversold" if current_rsi < 30 else "ปกติ"
        rsi_color = "red" if current_rsi > 70 else "green" if current_rsi < 30 else "blue"
        st.markdown(f"**RSI (14):** :{rsi_color}[{current_rsi:.2f}] ({rsi_status})")
    
    # MACD ปัจจุบัน
    if 'macd' in locals() and len(macd) > 0:
        current_macd = macd.iloc[-1]
        current_signal = signal.iloc[-1]
        current_hist = histogram.iloc[-1]
        
        macd_signal = "Bullish" if current_macd > current_signal else "Bearish"
        macd_color = "green" if current_macd > current_signal else "red"
        st.markdown(f"**MACD:** :{macd_color}[{current_macd:.3f}] ({macd_signal})")
        st.markdown(f"**Signal:** {current_signal:.3f}")
        st.markdown(f"**Histogram:** {current_hist:.3f}")
    
    # Moving Averages
    ma20 = df['Close'].rolling(20).mean().iloc[-1]
    ma50 = df['Close'].rolling(50).mean().iloc[-1]
    ma200 = df['Close'].rolling(200).mean().iloc[-1] if len(df) > 200 else None
    
    st.markdown(f"**MA20:** ฿{ma20:.2f}")
    st.markdown(f"**MA50:** ฿{ma50:.2f}")
    if ma200:
        st.markdown(f"**MA200:** ฿{ma200:.2f}")
    
    # Golden Cross / Death Cross
    if ma20 > ma50:
        st.success("✅ MA20 ตัดขึ้นเหนือ MA50 (สัญญาณซื้อ)")
    else:
        st.error("❌ MA20 ตัดลงใต้ MA50 (สัญญาณขาย)")

with col2:
    st.markdown("### Elliot Wave Analysis")
    
    # Elliot Wave แบบง่าย
    if len(df) > 50:
        # หาจุดสูงสุดต่ำสุด
        from scipy.signal import argrelextrema
        
        prices = df['Close'].values
        local_max = argrelextrema(prices, np.greater, order=5)[0]
        local_min = argrelextrema(prices, np.less, order=5)[0]
        
        # นับจำนวนคลื่น
        total_waves = len(local_max) + len(local_min)
        
        st.markdown(f"**จำนวนคลื่นที่พบ:** {total_waves} จุด")
        
        # วิเคราะห์ตำแหน่งปัจจุบัน
        last_price = prices[-1]
        if len(local_max) > 0 and len(local_min) > 0:
            last_high = prices[local_max[-1]] if len(local_max) > 0 else last_price
            last_low = prices[local_min[-1]] if len(local_min) > 0 else last_price
            
            # คำนวณตำแหน่ง
            price_range = last_high - last_low
            if price_range > 0:
                position = (last_price - last_low) / price_range
            else:
                position = 0.5
            
            if position > 0.8:
                wave_status = "น่าจะอยู่ใน Wave 3 (กำลังขึ้นแรง)"
                st.info(wave_status)
            elif position < 0.2:
                wave_status = "น่าจะอยู่ใน Wave 2 หรือใกล้จบการปรับฐาน"
                st.info(wave_status)
            else:
                wave_status = "น่าจะอยู่ใน Wave 4 ( sideways)"
                st.info(wave_status)
        else:
            st.warning("ไม่พบรูปแบบ Elliot Wave ที่ชัดเจน")
    else:
        st.warning("ข้อมูลไม่พอสำหรับวิเคราะห์ Elliot Wave")

# วิเคราะห์วอลุ่มรายใหญ่
st.markdown("---")
st.subheader("💰 วิเคราะห์วอลุ่มรายใหญ่")

col1, col2 = st.columns(2)

with col1:
    # คำนวณวอลุ่มเฉลี่ย
    avg_volume = df['Volume'].tail(20).mean()
    current_volume = df['Volume'].iloc[-1]
    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
    
    st.metric("วอลุ่มวันนี้ / ค่าเฉลี่ย", f"{volume_ratio:.2f}x", 
              "สูงกว่าปกติ" if volume_ratio > 1.5 else "ปกติ")
    
    # ตรวจสอบวอลุ่มผิดปกติ
    if volume_ratio > 2:
        st.error("⚠️ วอลุ่มสูงผิดปกติ (อาจมีรายใหญ่ทำรายการ)")
    elif volume_ratio > 1.5:
        st.warning("⚠️ วอลุ่มสูงกว่าปกติ")
    else:
        st.success("✅ วอลุ่มปกติ")

with col2:
    # วิเคราะห์ทิศทางวอลุ่ม
    volume_ma5 = df['Volume'].tail(5).mean()
    volume_ma10 = df['Volume'].tail(10).mean()
    
    if volume_ma5 > volume_ma10 and current_price > ma20:
        st.success("📈 วอลุ่มเพิ่มขึ้น ราคาขึ้น (น่าจะมีแรงซื้อ)")
    elif volume_ma5 > volume_ma10 and current_price < ma20:
        st.error("📉 วอลุ่มเพิ่มขึ้น ราคาลง (น่าจะมีแรงขาย)")
    else:
        st.info("📊 วอลุ่มทรงตัว")

# จุดซื้อขาย
st.markdown("---")
st.subheader("🎯 จุดซื้อขายแนะนำ")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### จุดซื้อ")
    
    # หาแนวรับ
    support = df['Low'].tail(20).min()
    rsi_oversold = current_rsi < 30 if 'current_rsi' in locals() else False
    
    st.markdown(f"- **แนวรับ:** ฿{support:.2f}")
    if rsi_oversold:
        st.markdown("- ✅ RSI Oversold (น่าซื้อ)")
    else:
        st.markdown("- ❌ RSI ยังไม่ Oversold")
    
    if current_price < ma20:
        st.markdown("- ✅ ราคาต่ำกว่า MA20")
    else:
        st.markdown("- ❌ ราคาสูงกว่า MA20")
    
    if volume_ratio > 1.5 and current_price < ma20:
        st.markdown("- ⚠️ มีวอลุ่มสูง ราคาลง (รอสัญญาณกลับตัว)")

with col2:
    st.markdown("### จุดขาย")
    
    # หาแนวต้าน
    resistance = df['High'].tail(20).max()
    rsi_overbought = current_rsi > 70 if 'current_rsi' in locals() else False
    
    st.markdown(f"- **แนวต้าน:** ฿{resistance:.2f}")
    if rsi_overbought:
        st.markdown("- ⚠️ RSI Overbought (ควรขาย)")
    else:
        st.markdown("- ✅ RSI ยังไม่ Overbought")
    
    if current_price > ma20 * 1.1:
        st.markdown("- ⚠️ ราคาสูงเกินไป (อาจขายทำกำไร)")
    else:
        st.markdown("- ✅ ราคายังไม่แพงเกิน")

# ท้ายหน้า
st.markdown("---")
st.caption(f"อัปเดตล่าสุด: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")