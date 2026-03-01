"""
หน้า 2: วิเคราะห์หุ้นเล่นสั้น ฉบับสมบูรณ์ (ไม่ใช้ scipy)
- กราฟเทคนิคอลครบ (RSI, MACD, Stochastic, Elliot Wave)
- จุดซื้อ ขาย ถัว Cut Loss
- วางข้อมูลวอลุ่ม 5 ช่องจากโปรแกรมเทรด วิเคราะห์ตามนายพราน
- รองรับ Python 3.13
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime, timedelta
import yfinance as yf
import re
import time

# เพิ่ม path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# ตั้งค่าเพจ
st.set_page_config(
    page_title="หุ้นเล่นสั้น V3.1",
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
        margin: 1rem 0;
    }
    .wait-signal {
        background: #f59e0b;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
    .neutral-signal {
        background: #6b7280;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
    .volume-bid {
        background: #dcfce7;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    .volume-offer {
        background: #fee2e2;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    .guru-quote {
        background: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-style: italic;
    }
    .metric-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        border-left: 3px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# ชื่อหน้า
st.markdown("""
<div style="display: flex; align-items: center; margin-bottom: 1rem;">
    <h1>⚡ วิเคราะห์หุ้นเล่นสั้น</h1>
    <span class="version-badge">V3.1 รองรับ Python 3.13</span>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ================== ฟังก์ชันคำนวณ indicators ==================

def calculate_rsi(prices, period=14):
    """คำนวณ RSI"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """คำนวณ MACD"""
    exp1 = prices.ewm(span=fast, adjust=False).mean()
    exp2 = prices.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram

def calculate_stochastic(df, k=14, d=3):
    """คำนวณ Stochastic"""
    low_min = df['Low'].rolling(window=k).min()
    high_max = df['High'].rolling(window=k).max()
    stoch_k = 100 * ((df['Close'] - low_min) / (high_max - low_min))
    stoch_d = stoch_k.rolling(window=d).mean()
    return stoch_k, stoch_d

def analyze_elliot_wave(prices):
    """วิเคราะห์ Elliot Wave แบบง่าย (ไม่ใช้ scipy)"""
    if len(prices) < 50:
        return "📊 ข้อมูลไม่พอ", 50
    
    # ใช้ pandas แทน scipy
    prices_array = prices.values
    
    # หาจุดสูงสุดต่ำสุดใน 20 วันล่าสุด
    last_20 = prices_array[-20:]
    last_high = last_20.max()
    last_low = last_20.min()
    last_price = prices_array[-1]
    
    price_range = last_high - last_low
    if price_range > 0:
        position = (last_price - last_low) / price_range
    else:
        position = 0.5
    
    # วิเคราะห์ตำแหน่ง
    if position > 0.8:
        return "📈 แนวโน้มขาขึ้น (Wave 3)", 80
    elif position < 0.2:
        return "📉 แนวโน้มขาลง (Wave 2)", 20
    else:
        return "📊 Sideways (Wave 4)", 50

def parse_volume(text, max_values=5):
    """แปลงข้อความเป็นตัวเลข รองรับ comma, space, ตัวหนังสือ"""
    if not text or not text.strip():
        return []
    
    # ค้นหาตัวเลขทั้งหมด
    numbers = re.findall(r'[\d,]+', text)
    
    volumes = []
    for num in numbers:
        clean = num.replace(',', '')
        try:
            volumes.append(int(clean))
        except:
            continue
    
    return volumes[:max_values]

# ================== Sidebar ==================

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
            buy_price = st.number_input("ราคาที่ซื้อ", min_value=0.0, step=0.5, format="%.2f")
        with col2:
            quantity = st.number_input("จำนวน", min_value=0, step=100)
    
    st.markdown("---")
    st.subheader("⚙️ ตั้งค่า Cut Loss")
    cutloss_pct = st.slider("% Cut Loss", 3, 10, 5)
    takeprofit_pct = st.slider("% Take Profit", 5, 20, 10)
    
    st.markdown("---")
    if st.button("🔄 รีเฟรชข้อมูล", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ================== ดึงข้อมูลจาก Yahoo ==================

@st.cache_data(ttl=60)
def load_data(symbol, period):
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period=period)
        info = ticker.info
        return df, info, True
    except Exception as e:
        return None, None, False

df, info, success = load_data(symbol, period)

if not success or df is None or df.empty:
    st.error(f"❌ ไม่สามารถดึงข้อมูล {symbol} ได้")
    st.info("ตรวจสอบรหัสหุ้น เช่น ADVANC, PTT, CPALL")
    st.stop()

# ================== คำนวณค่าต่างๆ ==================

current_price = df['Close'].iloc[-1]
prev_price = df['Close'].iloc[-2]
change = current_price - prev_price
change_pct = (change / prev_price) * 100

# RSI
rsi = calculate_rsi(df['Close'])
current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50

# MACD
macd, signal_line, histogram = calculate_macd(df['Close'])
current_macd = macd.iloc[-1] if not pd.isna(macd.iloc[-1]) else 0
current_signal = signal_line.iloc[-1] if not pd.isna(signal_line.iloc[-1]) else 0

# Stochastic
stoch_k, stoch_d = calculate_stochastic(df)
current_k = stoch_k.iloc[-1] if not pd.isna(stoch_k.iloc[-1]) else 50

# Elliot Wave
wave_status, wave_score = analyze_elliot_wave(df['Close'])

# Moving Averages
ma20 = df['Close'].rolling(20).mean().iloc[-1]
ma50 = df['Close'].rolling(50).mean().iloc[-1]

# แนวรับ/แนวต้าน
support = df['Low'].tail(20).min()
resistance = df['High'].tail(20).max()

# ================== Tabs ==================

tab1, tab2, tab3 = st.tabs(["📈 กราฟเทคนิคอล", "🎯 จุดซื้อขาย", "🐋 วิเคราะห์วอลุ่ม 5 ช่อง"])

# ================== TAB 1: กราฟเทคนิคอล ==================

with tab1:
    st.subheader(f"📈 กราฟเทคนิคอล {symbol}")
    
    # สร้างกราฟ 5 แถว
    fig = make_subplots(
        rows=5, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.3, 0.15, 0.15, 0.2, 0.2],
        subplot_titles=('ราคา', 'Volume', 'RSI', 'MACD', 'Stochastic')
    )
    
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
        row=1, col=1
    )
    
    # Moving Averages
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Close'].rolling(20).mean(),
                  name='MA20', line=dict(color='orange', width=1.5)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Close'].rolling(50).mean(),
                  name='MA50', line=dict(color='blue', width=1.5)),
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
        go.Scatter(x=df.index, y=rsi, name='RSI', line=dict(color='purple', width=2)),
        row=3, col=1
    )
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    # MACD
    fig.add_trace(
        go.Scatter(x=df.index, y=macd, name='MACD', line=dict(color='blue', width=2)),
        row=4, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=signal_line, name='Signal', line=dict(color='red', width=2)),
        row=4, col=1
    )
    
    # Stochastic
    fig.add_trace(
        go.Scatter(x=df.index, y=stoch_k, name='%K', line=dict(color='blue', width=2)),
        row=5, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=stoch_d, name='%D', line=dict(color='red', width=2)),
        row=5, col=1
    )
    fig.add_hline(y=80, line_dash="dash", line_color="red", row=5, col=1)
    fig.add_hline(y=20, line_dash="dash", line_color="green", row=5, col=1)
    
    fig.update_layout(
        height=1000,
        showlegend=True,
        hovermode='x unified',
        title=f"{symbol} - Technical Analysis"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # ข้อมูลพื้นฐาน
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("เปิด", f"฿{df['Open'].iloc[-1]:.2f}")
    with col2:
        st.metric("สูงสุด", f"฿{df['High'].iloc[-1]:.2f}")
    with col3:
        st.metric("ต่ำสุด", f"฿{df['Low'].iloc[-1]:.2f}")
    with col4:
        st.metric("วอลุ่ม", f"{df['Volume'].iloc[-1]:,.0f}")

# ================== TAB 2: จุดซื้อขาย ==================

with tab2:
    st.subheader("🎯 จุดซื้อขาย และวิเคราะห์")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 สถานะปัจจุบัน")
        
        st.metric("ราคาปัจจุบัน", f"฿{current_price:.2f}", 
                 f"{change:+.2f} ({change_pct:+.2f}%)")
        
        # แนวโน้ม
        if current_price > ma20 and ma20 > ma50:
            trend = "🟢 ขาขึ้น"
            trend_color = "green"
        elif current_price < ma20 and ma20 < ma50:
            trend = "🔴 ขาลง"
            trend_color = "red"
        else:
            trend = "🟡 Sideways"
            trend_color = "orange"
        
        st.markdown(f"**แนวโน้ม:** :{trend_color}[{trend}]")
        
        # RSI
        if current_rsi > 70:
            rsi_status = "🔴 Overbought"
            rsi_color = "red"
        elif current_rsi < 30:
            rsi_status = "🟢 Oversold"
            rsi_color = "green"
        else:
            rsi_status = "⚪ ปกติ"
            rsi_color = "gray"
        
        st.markdown(f"**RSI (14):** :{rsi_color}[{current_rsi:.1f}] ({rsi_status})")
        
        # MACD
        if current_macd > current_signal:
            macd_status = "🟢 Bullish"
            macd_color = "green"
        else:
            macd_status = "🔴 Bearish"
            macd_color = "red"
        
        st.markdown(f"**MACD:** :{macd_color}[{macd_status}]")
        
        # Stochastic
        if current_k > 80:
            stoch_status = "🔴 Overbought"
            stoch_color = "red"
        elif current_k < 20:
            stoch_status = "🟢 Oversold"
            stoch_color = "green"
        else:
            stoch_status = "⚪ ปกติ"
            stoch_color = "gray"
        
        st.markdown(f"**Stochastic:** :{stoch_color}[{current_k:.1f}] ({stoch_status})")
        
        # Elliot Wave
        st.markdown(f"**Elliot Wave:** {wave_status}")
        
        # แนวรับ/ต้าน
        st.markdown("---")
        st.markdown(f"**แนวรับ:** ฿{support:.2f}")
        st.markdown(f"**แนวต้าน:** ฿{resistance:.2f}")
    
    with col2:
        st.markdown("### 💰 จุดแนะนำ")
        
        # คำนวณจุดซื้อขาย
        buy_point = round(min(current_price * 0.98, support * 1.02), 2)
        sell_point = round(max(current_price * (1 + takeprofit_pct/100), resistance * 0.98), 2)
        cutloss_point = round(current_price * (1 - cutloss_pct/100), 2)
        
        st.markdown(f"**🟢 ซื้อที่:** ฿{buy_point:.2f}")
        st.markdown(f"**🔴 ขายที่:** ฿{sell_point:.2f}")
        st.markdown(f"**⛔ Cut Loss:** ฿{cutloss_point:.2f} ({cutloss_pct}%)")
        
        # Reward/Risk
        reward = sell_point - buy_point
        risk = buy_point - cutloss_point
        rr_ratio = reward / risk if risk > 0 else 0
        
        st.markdown(f"**📊 Reward/Risk:** {rr_ratio:.2f} : 1")
        if rr_ratio >= 2:
            st.success("✅ คุ้มค่าแก่การเสี่ยง")
        elif rr_ratio >= 1:
            st.warning("⚠️ พอรับได้")
        else:
            st.error("❌ ไม่คุ้ม")
        
        # ถ้ามีหุ้นในพอร์ต
        if has_stock and buy_price > 0:
            st.markdown("---")
            st.markdown("### 📊 สถานะพอร์ต")
            
            profit_loss = (current_price - buy_price) * quantity
            profit_pct = ((current_price - buy_price) / buy_price) * 100
            
            st.metric("กำไร/ขาดทุน", f"฿{profit_loss:,.2f}", 
                     f"{profit_pct:+.2f}%")
            
            # แนะนำถัว
            if profit_pct < -cutloss_pct:
                st.error(f"⚠️ ขาดทุนเกิน {cutloss_pct}% ควร cut loss")
            elif profit_pct < -3:
                st.warning(f"📉 ขาดทุน {profit_pct:.1f}% ถัวที่ ฿{current_price*0.97:.2f}")
            elif profit_pct > takeprofit_pct:
                st.success(f"✅ กำไรเกิน {takeprofit_pct}% ควรขายบางส่วน")
            elif profit_pct > 5:
                st.info(f"📈 กำไร {profit_pct:.1f}% ตั้ง cut loss ที่จุดคุ้มทุน")
    
    # สรุปสัญญาณ
    st.markdown("---")
    st.subheader("🔍 สรุปสัญญาณ")
    
    buy_signals = []
    sell_signals = []
    
    if current_rsi < 30:
        buy_signals.append("RSI Oversold")
    if current_rsi > 70:
        sell_signals.append("RSI Overbought")
    
    if current_macd > current_signal:
        buy_signals.append("MACD Bullish")
    else:
        sell_signals.append("MACD Bearish")
    
    if current_k < 20:
        buy_signals.append("Stochastic Oversold")
    if current_k > 80:
        sell_signals.append("Stochastic Overbought")
    
    if current_price < support * 1.02:
        buy_signals.append("ใกล้แนวรับ")
    if current_price > resistance * 0.98:
        sell_signals.append("ใกล้แนวต้าน")
    
    col1, col2 = st.columns(2)
    with col1:
        if buy_signals:
            st.markdown("### 🟢 สัญญาณซื้อ")
            for s in buy_signals:
                st.markdown(f"- {s}")
    
    with col2:
        if sell_signals:
            st.markdown("### 🔴 สัญญาณขาย")
            for s in sell_signals:
                st.markdown(f"- {s}")
    
    # คำแนะนำสุดท้าย
    st.markdown("---")
    signal_count = len(buy_signals) - len(sell_signals)
    
    if signal_count >= 2:
        st.markdown(
            '<div class="buy-signal">'
            '<h2>🟢 แนะนำ: ซื้อ</h2>'
            '<p>สัญญาณซื้อแรง รอจังหวะที่แนวรับ</p>'
            '</div>',
            unsafe_allow_html=True
        )
    elif signal_count <= -2:
        st.markdown(
            '<div class="sell-signal">'
            '<h2>🔴 แนะนำ: ขาย</h2>'
            '<p>สัญญาณขายแรง รอจังหวะขายทำกำไร</p>'
            '</div>',
            unsafe_allow_html=True
        )
    elif signal_count > 0:
        st.markdown(
            '<div class="wait-signal">'
            '<h2>🟡 แนะนำ: รอ</h2>'
            '<p>มีสัญญาณซื้อบางส่วน รอให้ชัดเจน</p>'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="neutral-signal">'
            '<h2>⚪ แนะนำ: เฝ้าดู</h2>'
            '<p>ไม่มีสัญญาณชัดเจน</p>'
            '</div>',
            unsafe_allow_html=True
        )

# ================== TAB 3: วิเคราะห์วอลุ่ม 5 ช่อง ==================

with tab3:
    st.subheader("🐋 วิเคราะห์วอลุ่ม 5 ช่อง (วางข้อมูลจากโปรแกรมเทรด)")
    
    st.markdown("### วิธีใช้")
    st.markdown("""
    1. เปิดโปรแกรมเทรด (InnovestX, Dime, Streaming)
    2. **เลือกและคัดลอก** ข้อมูล Bid/Offer 5 ช่อง
    3. **วาง (Ctrl+V)** ในช่องด้านล่าง
    4. ระบบจะวิเคราะห์กลยุทธ์ตามนายพรานให้
    """)
    
    with st.expander("📋 ดูตัวอย่าง"):
        st.markdown("""
        **วางแบบนี้ก็ได้ (ระบบจัดการให้):**
