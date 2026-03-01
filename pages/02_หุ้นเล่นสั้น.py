"""
หน้า 2: วิเคราะห์หุ้นเล่นสั้น ฉบับสมบูรณ์
- กราฟเทคนิคอลครบ (RSI, MACD, Stochastic, Elliot Wave)
- จุดซื้อ ขาย ถัว Cut Loss
- วางข้อมูลวอลุ่ม 5 ช่องจากโปรแกรมเทรด วิเคราะห์ตามนายพราน
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime
import yfinance as yf
import re

# ตั้งค่าเพจ
st.set_page_config(
    page_title="หุ้นเล่นสั้น",
    page_icon="⚡",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    .version-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 50px;
        display: inline-block;
        font-size: 0.9rem;
        margin-left: 1rem;
    }
    .buy-signal {
        background: #10b981;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
    .sell-signal {
        background: #ef4444;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .wait-signal {
        background: #f59e0b;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .neutral-signal {
        background: #6b7280;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .guru-quote {
        background: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# ชื่อหน้า
st.markdown("""
<div style="display: flex; align-items: center; margin-bottom: 1rem;">
    <h1>⚡ วิเคราะห์หุ้นเล่นสั้น</h1>
    <span class="version-badge">V3.0</span>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ฟังก์ชันคำนวณ RSI
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ฟังก์ชันคำนวณ MACD
def calculate_macd(prices, fast=12, slow=26, signal=9):
    exp1 = prices.ewm(span=fast, adjust=False).mean()
    exp2 = prices.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

# ฟังก์ชันคำนวณ Stochastic
def calculate_stochastic(df, k=14, d=3):
    low_min = df['Low'].rolling(window=k).min()
    high_max = df['High'].rolling(window=k).max()
    stoch_k = 100 * ((df['Close'] - low_min) / (high_max - low_min))
    stoch_d = stoch_k.rolling(window=d).mean()
    return stoch_k, stoch_d

# ฟังก์ชันแปลงข้อความเป็นตัวเลข
def parse_volume(text, max_values=5):
    if not text or not text.strip():
        return []
    numbers = re.findall(r'[\d,]+', text)
    volumes = []
    for num in numbers:
        clean = num.replace(',', '')
        try:
            volumes.append(int(clean))
        except:
            continue
    return volumes[:max_values]

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/stocks--v1.png", width=60)
    st.subheader("🔍 เลือกหุ้น")
    symbol = st.text_input("รหัสหุ้น", "ADVANC").upper()
    
    st.markdown("---")
    st.subheader("📊 ช่วงเวลา")
    period = st.selectbox("", ["1mo", "3mo", "6mo", "1y"], index=1)
    
    st.markdown("---")
    st.subheader("💰 ข้อมูลพอร์ต")
    has_stock = st.checkbox("มีหุ้นนี้ในพอร์ต")
    if has_stock:
        col1, col2 = st.columns(2)
        with col1:
            buy_price = st.number_input("ราคาที่ซื้อ", min_value=0.0, step=0.5)
        with col2:
            quantity = st.number_input("จำนวน", min_value=0, step=100)
    
    st.markdown("---")
    st.subheader("⚙️ ตั้งค่า")
    cutloss_pct = st.slider("% Cut Loss", 3, 10, 5)
    takeprofit_pct = st.slider("% Take Profit", 5, 20, 10)
    
    st.markdown("---")
    if st.button("🔄 รีเฟรช", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ดึงข้อมูล
@st.cache_data(ttl=60)
def load_data(symbol, period):
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period=period)
        return df, True
    except:
        return None, False

df, success = load_data(symbol, period)

if not success or df is None or df.empty:
    st.error(f"❌ ไม่สามารถดึงข้อมูล {symbol} ได้")
    st.stop()

# คำนวณค่าต่างๆ
current_price = df['Close'].iloc[-1]
prev_price = df['Close'].iloc[-2]
change = current_price - prev_price
change_pct = (change / prev_price) * 100

rsi = calculate_rsi(df['Close'])
current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50

macd, signal_line = calculate_macd(df['Close'])
current_macd = macd.iloc[-1] if not pd.isna(macd.iloc[-1]) else 0
current_signal = signal_line.iloc[-1] if not pd.isna(signal_line.iloc[-1]) else 0

stoch_k, stoch_d = calculate_stochastic(df)
current_k = stoch_k.iloc[-1] if not pd.isna(stoch_k.iloc[-1]) else 50

ma20 = df['Close'].rolling(20).mean().iloc[-1]
ma50 = df['Close'].rolling(50).mean().iloc[-1]
support = df['Low'].tail(20).min()
resistance = df['High'].tail(20).max()

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 กราฟเทคนิคอล", "🎯 จุดซื้อขาย", "🐋 วิเคราะห์วอลุ่ม"])

# ================== TAB 1 ==================
with tab1:
    st.subheader(f"📈 กราฟเทคนิคอล {symbol}")
    
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.4, 0.2, 0.2, 0.2],
        subplot_titles=('ราคา', 'Volume', 'RSI', 'Stochastic')
    )
    
    # กราฟแท่งเทียน
    fig.add_trace(
        go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'], name='ราคา'
        ), row=1, col=1
    )
    
    # Moving Averages
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Close'].rolling(20).mean(),
                  name='MA20', line=dict(color='orange')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Close'].rolling(50).mean(),
                  name='MA50', line=dict(color='blue')),
        row=1, col=1
    )
    
    # Volume
    colors = ['red' if df['Open'].iloc[i] > df['Close'].iloc[i] else 'green' 
              for i in range(len(df))]
    fig.add_trace(
        go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color=colors),
        row=2, col=1
    )
    
    # RSI
    fig.add_trace(
        go.Scatter(x=df.index, y=rsi, name='RSI', line=dict(color='purple')),
        row=3, col=1
    )
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    # Stochastic
    fig.add_trace(
        go.Scatter(x=df.index, y=stoch_k, name='%K', line=dict(color='blue')),
        row=4, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=stoch_d, name='%D', line=dict(color='red')),
        row=4, col=1
    )
    fig.add_hline(y=80, line_dash="dash", line_color="red", row=4, col=1)
    fig.add_hline(y=20, line_dash="dash", line_color="green", row=4, col=1)
    
    fig.update_layout(height=800, showlegend=True, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

# ================== TAB 2 ==================
with tab2:
    st.subheader("🎯 จุดซื้อขาย")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 สถานะปัจจุบัน")
        st.metric("ราคา", f"฿{current_price:.2f}", f"{change:+.2f} ({change_pct:+.2f}%)")
        
        if current_price > ma20 and ma20 > ma50:
            st.success("🟢 แนวโน้มขาขึ้น")
        elif current_price < ma20 and ma20 < ma50:
            st.error("🔴 แนวโน้มขาลง")
        else:
            st.warning("🟡 Sideways")
        
        st.markdown(f"**RSI:** {current_rsi:.1f}")
        st.markdown(f"**MACD:** {'Bullish' if current_macd > current_signal else 'Bearish'}")
        st.markdown(f"**Stochastic:** {current_k:.1f}")
        st.markdown(f"**แนวรับ:** ฿{support:.2f}")
        st.markdown(f"**แนวต้าน:** ฿{resistance:.2f}")
    
    with col2:
        st.markdown("### 💰 จุดแนะนำ")
        buy_point = round(min(current_price * 0.98, support * 1.02), 2)
        sell_point = round(max(current_price * (1 + takeprofit_pct/100), resistance * 0.98), 2)
        cutloss_point = round(current_price * (1 - cutloss_pct/100), 2)
        
        st.markdown(f"**🟢 ซื้อที่:** ฿{buy_point:.2f}")
        st.markdown(f"**🔴 ขายที่:** ฿{sell_point:.2f}")
        st.markdown(f"**⛔ Cut Loss:** ฿{cutloss_point:.2f}")
        
        if has_stock and buy_price > 0:
            st.markdown("---")
            profit_loss = (current_price - buy_price) * quantity
            profit_pct = ((current_price - buy_price) / buy_price) * 100
            st.metric("กำไร/ขาดทุน", f"฿{profit_loss:,.2f}", f"{profit_pct:+.2f}%")

# ================== TAB 3 ==================
with tab3:
    st.subheader("🐋 วิเคราะห์วอลุ่ม 5 ช่อง")
    
    st.markdown("### วิธีใช้")
    st.markdown("""
    1. เปิดโปรแกรมเทรด
    2. คัดลอกข้อมูล Bid/Offer 5 ช่อง
    3. วางในช่องด้านล่าง
    """)
    
    with st.expander("📋 ดูตัวอย่าง"):
        st.markdown("""
