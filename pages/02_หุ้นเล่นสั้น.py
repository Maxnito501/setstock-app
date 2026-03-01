"""
หน้า 2: วิเคราะห์หุ้นเล่นสั้น (ใช้ Yahoo Finance)
- รายชื่อหุ้นไทยที่มีข้อมูลครบ
- กราฟเทคนิคอล: RSI, MACD, Stochastic, Bollinger Bands, Elliot Wave
- จุดซื้อ ขาย Cut Loss
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

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
    .buy-box {
        background: #10b981;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .sell-box {
        background: #ef4444;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .wait-box {
        background: #f59e0b;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .info-box {
        background: #3b82f6;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ชื่อหน้า
st.markdown("""
<div style="display: flex; align-items: center;">
    <h1>⚡ วิเคราะห์หุ้นเล่นสั้น</h1>
    <span class="version-badge">Yahoo Finance</span>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ================== รายชื่อหุ้นไทยที่มีข้อมูลใน Yahoo Finance ==================

thai_stocks = {
    # SET50
    "ADVANC": "ADVANC.BK",
    "AOT": "AOT.BK",
    "BANPU": "BANPU.BK",
    "BBL": "BBL.BK",
    "BDMS": "BDMS.BK",
    "BEM": "BEM.BK",
    "BH": "BH.BK",
    "BJC": "BJC.BK",
    "CBG": "CBG.BK",
    "CENTEL": "CENTEL.BK",
    "CK": "CK.BK",
    "CPALL": "CPALL.BK",
    "CPF": "CPF.BK",
    "CPN": "CPN.BK",
    "DELTA": "DELTA.BK",
    "DTAC": "DTAC.BK",
    "EGCO": "EGCO.BK",
    "GLOBAL": "GLOBAL.BK",
    "GPSC": "GPSC.BK",
    "GULF": "GULF.BK",
    "HMPRO": "HMPRO.BK",
    "INTUCH": "INTUCH.BK",
    "IRPC": "IRPC.BK",
    "IVL": "IVL.BK",
    "KBANK": "KBANK.BK",
    "KCE": "KCE.BK",
    "KTB": "KTB.BK",
    "KTC": "KTC.BK",
    "LH": "LH.BK",
    "MINT": "MINT.BK",
    "MTC": "MTC.BK",
    "OSP": "OSP.BK",
    "PLANB": "PLANB.BK",
    "PTT": "PTT.BK",
    "PTTEP": "PTTEP.BK",
    "PTTGC": "PTTGC.BK",
    "RATCH": "RATCH.BK",
    "SAWAD": "SAWAD.BK",
    "SCB": "SCB.BK",
    "SCC": "SCC.BK",
    "SIRI": "SIRI.BK",
    "SPALI": "SPALI.BK",
    "TASCO": "TASCO.BK",
    "TCAP": "TCAP.BK",
    "THAI": "THAI.BK",
    "TISCO": "TISCO.BK",
    "TOP": "TOP.BK",
    "TRUE": "TRUE.BK",
    "TU": "TU.BK",
    "VGI": "VGI.BK",
    "WHA": "WHA.BK",
    
    # เพิ่มเติม
    "BGRIM": "BGRIM.BK",
    "BCH": "BCH.BK",
    "CHG": "CHG.BK",
    "COM7": "COM7.BK",
    "EA": "EA.BK",
    "JMT": "JMT.BK",
    "OR": "OR.BK",
    "SCGP": "SCGP.BK",
    "STEC": "STEC.BK",
    "SUPER": "SUPER.BK"
}

# ================== ฟังก์ชันคำนวณ Technical Indicators ==================

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

def calculate_bollinger_bands(prices, period=20, std=2):
    """คำนวณ Bollinger Bands"""
    sma = prices.rolling(window=period).mean()
    std_dev = prices.rolling(window=period).std()
    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)
    return upper, sma, lower

def analyze_elliot_wave(prices):
    """วิเคราะห์ Elliot Wave แบบง่าย"""
    if len(prices) < 50:
        return "ข้อมูลไม่พอ", 0
    
    last_20 = prices.values[-20:]
    last_high = last_20.max()
    last_low = last_20.min()
    last_price = prices.values[-1]
    
    price_range = last_high - last_low
    if price_range > 0:
        position = (last_price - last_low) / price_range
    else:
        position = 0.5
    
    if position > 0.8:
        return "📈 Wave 3 (ขาขึ้น)", 80
    elif position < 0.2:
        return "📉 Wave 2 (ขาลง)", 20
    else:
        return "📊 Wave 4 (Sideways)", 50

# ================== Sidebar ==================

with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/stocks--v1.png", width=60)
    st.subheader("🔍 เลือกหุ้น")
    
    # เลือกจากรายชื่อ
    symbol_display = st.selectbox("เลือกหุ้น", list(thai_stocks.keys()), index=0)
    symbol = thai_stocks[symbol_display]
    
    st.markdown("---")
    st.subheader("📊 ช่วงเวลา")
    period = st.selectbox("", ["1mo", "3mo", "6mo", "1y", "2y"], index=1)
    
    st.markdown("---")
    st.subheader("💰 ข้อมูลพอร์ต")
    has_stock = st.checkbox("มีหุ้นนี้ในพอร์ต")
    if has_stock:
        col1, col2 = st.columns(2)
        with col1:
            buy_price = st.number_input("ราคาที่ซื้อ", min_value=0.0, step=0.5, format="%.2f")
        with col2:
            quantity = st.number_input("จำนวนหุ้น", min_value=0, step=100)
    
    st.markdown("---")
    st.subheader("⚙️ ตั้งค่า")
    cutloss_pct = st.slider("Cut Loss %", 2, 10, 5)
    takeprofit_pct = st.slider("Take Profit %", 3, 20, 10)
    
    st.markdown("---")
    if st.button("🔄 โหลดข้อมูลใหม่", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ================== ดึงข้อมูลจาก Yahoo Finance ==================

@st.cache_data(ttl=60)
def load_stock_data(symbol, period):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        
        if df.empty:
            return None, None, False
        
        info = ticker.info
        name = info.get('longName', symbol)
        
        return df, name, True
    except Exception as e:
        return None, None, False

df, company_name, success = load_stock_data(symbol, period)

if not success or df is None or df.empty:
    st.error(f"❌ ไม่สามารถดึงข้อมูล {symbol_display} ได้")
    st.info("หุ้นที่มีข้อมูล: " + ", ".join(list(thai_stocks.keys())[:10]) + "...")
    st.stop()

# ================== คำนวณ Indicators ==================

current_price = df['Close'].iloc[-1]
prev_price = df['Close'].iloc[-2]
change = current_price - prev_price
change_pct = (change / prev_price) * 100

# RSI
rsi = calculate_rsi(df['Close'])
current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50

# MACD
macd, signal, histogram = calculate_macd(df['Close'])
current_macd = macd.iloc[-1] if not pd.isna(macd.iloc[-1]) else 0
current_signal = signal.iloc[-1] if not pd.isna(signal.iloc[-1]) else 0

# Stochastic
stoch_k, stoch_d = calculate_stochastic(df)
current_k = stoch_k.iloc[-1] if not pd.isna(stoch_k.iloc[-1]) else 50
current_d = stoch_d.iloc[-1] if not pd.isna(stoch_d.iloc[-1]) else 50

# Bollinger Bands
upper_bb, middle_bb, lower_bb = calculate_bollinger_bands(df['Close'])

# Elliot Wave
wave_status, wave_score = analyze_elliot_wave(df['Close'])

# Moving Averages
ma20 = df['Close'].rolling(20).mean().iloc[-1]
ma50 = df['Close'].rolling(50).mean().iloc[-1]
ma200 = df['Close'].rolling(200).mean().iloc[-1] if len(df) > 200 else None

# แนวรับ/แนวต้าน
support = df['Low'].tail(20).min()
resistance = df['High'].tail(20).max()

# Volume
volume_ma = df['Volume'].tail(20).mean()
current_volume = df['Volume'].iloc[-1]
volume_ratio = current_volume / volume_ma if volume_ma > 0 else 1

# ================== แสดงข้อมูลเบื้องต้น ==================

st.markdown(f"""
<div class="info-box">
    {symbol_display} - {company_name[:80] if company_name else ''}
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("ราคาปัจจุบัน", f"฿{current_price:.2f}", f"{change:+.2f} ({change_pct:+.2f}%)")
with col2:
    rsi_color = "🔴" if current_rsi > 70 else "🟢" if current_rsi < 30 else "⚪"
    st.metric("RSI (14)", f"{rsi_color} {current_rsi:.1f}")
with col3:
    macd_status = "🟢 Bullish" if current_macd > current_signal else "🔴 Bearish"
    st.metric("MACD", macd_status)
with col4:
    st.metric("Volume Ratio", f"{volume_ratio:.2f}x")

st.markdown("---")

# ================== Tabs ==================

tab1, tab2, tab3 = st.tabs(["📈 กราฟเทคนิคอล", "🎯 จุดซื้อขาย", "📊 ข้อมูลเพิ่มเติม"])

# ================== TAB 1: กราฟเทคนิคอล ==================

with tab1:
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
            name='ราคา',
            showlegend=False
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
    
    # Bollinger Bands
    fig.add_trace(
        go.Scatter(x=df.index, y=upper_bb, name='Upper BB',
                  line=dict(color='gray', width=1, dash='dash')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=lower_bb, name='Lower BB',
                  line=dict(color='gray', width=1, dash='dash')),
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
        go.Scatter(x=df.index, y=signal, name='Signal', line=dict(color='red', width=2)),
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
        xaxis_rangeslider_visible=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ================== TAB 2: จุดซื้อขาย ==================

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 สถานะปัจจุบัน")
        
        # แนวโน้ม
        if current_price > ma20 and ma20 > ma50:
            st.success("🟢 แนวโน้มขาขึ้น")
        elif current_price < ma20 and ma20 < ma50:
            st.error("🔴 แนวโน้มขาลง")
        else:
            st.warning("🟡 Sideways")
        
        st.markdown(f"**RSI:** {current_rsi:.1f}")
        st.markdown(f"**MACD:** {'Bullish' if current_macd > current_signal else 'Bearish'}")
        st.markdown(f"**Stochastic:** {current_k:.1f}")
        st.markdown(f"**Elliot Wave:** {wave_status}")
        st.markdown(f"**แนวรับ:** ฿{support:.2f}")
        st.markdown(f"**แนวต้าน:** ฿{resistance:.2f}")
        st.markdown(f"**MA20:** ฿{ma20:.2f}")
        st.markdown(f"**MA50:** ฿{ma50:.2f}")
    
    with col2:
        st.markdown("### 💰 จุดแนะนำ")
        
        # คำนวณจุดซื้อ
        buy_point = round(support, 2)
        buy_point2 = round(lower_bb.iloc[-1], 2) if not pd.isna(lower_bb.iloc[-1]) else buy_point
        buy_point3 = round(ma50, 2)
        
        # คำนวณจุดขาย
        sell_point = round(resistance, 2)
        sell_point2 = round(upper_bb.iloc[-1], 2) if not pd.isna(upper_bb.iloc[-1]) else sell_point
        sell_point3 = round(current_price * (1 + takeprofit_pct/100), 2)
        
        # Cut Loss
        cutloss_point = round(current_price * (1 - cutloss_pct/100), 2)
        
        st.markdown("#### 🟢 จุดซื้อ")
        st.markdown(f"- แนวรับ: ฿{buy_point:.2f}")
        st.markdown(f"- Lower BB: ฿{buy_point2:.2f}")
        st.markdown(f"- MA50: ฿{buy_point3:.2f}")
        
        st.markdown("#### 🔴 จุดขาย")
        st.markdown(f"- แนวต้าน: ฿{sell_point:.2f}")
        st.markdown(f"- Upper BB: ฿{sell_point2:.2f}")
        st.markdown(f"- Take Profit: ฿{sell_point3:.2f}")
        
        st.markdown("#### ⛔ Cut Loss")
        st.markdown(f"- ตั้งที่: ฿{cutloss_point:.2f} ({cutloss_pct}%)")
        
        # Reward/Risk
        risk = current_price - cutloss_point
        reward = sell_point - current_price
        rr_ratio = reward / risk if risk > 0 else 0
        
        st.markdown(f"#### 📊 Reward/Risk: {rr_ratio:.2f}")
        if rr_ratio >= 2:
            st.success("✅ คุ้มค่า")
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
            
            st.metric("กำไร/ขาดทุน", f"฿{profit_loss:,.2f}", f"{profit_pct:+.2f}%")
            
            if profit_pct < -cutloss_pct:
                st.error(f"⚠️ ขาดทุนเกิน {cutloss_pct}% ควร Cut Loss")
            elif profit_pct > takeprofit_pct:
                st.success(f"✅ กำไรเกิน {takeprofit_pct}% ควรขาย")
    
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
    
    if current_price < lower_bb.iloc[-1]:
        buy_signals.append("ใต้ Lower BB")
    if current_price > upper_bb.iloc[-1]:
        sell_signals.append("เหนือ Upper BB")
    
    col1, col2 = st.columns(2)
    with col1:
        if buy_signals:
            st.markdown("##### 🟢 สัญญาณซื้อ")
            for s in buy_signals:
                st.markdown(f"- {s}")
    
    with col2:
        if sell_signals:
            st.markdown("##### 🔴 สัญญาณขาย")
            for s in sell_signals:
                st.markdown(f"- {s}")
    
    # คำแนะนำ
    st.markdown("---")
    signal_score = len(buy_signals) - len(sell_signals)
    
    if signal_score >= 3:
        st.markdown('<div class="buy-box"><h2>🟢 แนะนำ: ซื้อ</h2></div>', unsafe_allow_html=True)
    elif signal_score <= -3:
        st.markdown('<div class="sell-box"><h2>🔴 แนะนำ: ขาย</h2></div>', unsafe_allow_html=True)
    elif signal_score > 0:
        st.markdown('<div class="wait-box"><h2>🟡 แนะนำ: รอ</h2></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="wait-box"><h2>⚪ แนะนำ: เฝ้าดู</h2></div>', unsafe_allow_html=True)

# ================== TAB 3: ข้อมูลเพิ่มเติม ==================

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 สถิติรายวัน")
        st.markdown(f"**เปิด:** ฿{df['Open'].iloc[-1]:.2f}")
        st.markdown(f"**สูงสุด:** ฿{df['High'].iloc[-1]:.2f}")
        st.markdown(f"**ต่ำสุด:** ฿{df['Low'].iloc[-1]:.2f}")
        st.markdown(f"**ปิด:** ฿{df['Close'].iloc[-1]:.2f}")
        st.markdown(f"**วอลุ่ม:** {df['Volume'].iloc[-1]:,.0f}")
    
    with col2:
        st.markdown("### 📊 สถิติย้อนหลัง")
        st.markdown(f"**สูงสุด 52 สัปดาห์:** ฿{df['High'].tail(252).max():.2f}")
        st.markdown(f"**ต่ำสุด 52 สัปดาห์:** ฿{df['Low'].tail(252).min():.2f}")
        st.markdown(f"**วอลุ่มเฉลี่ย 20 วัน:** {df['Volume'].tail(20).mean():,.0f}")
        st.markdown(f"**Volume Ratio:** {volume_ratio:.2f}x")
    
    # วิเคราะห์วอลุ่ม
    st.markdown("---")
    st.markdown("### 📊 วิเคราะห์วอลุ่ม")
    
    if volume_ratio > 1.5:
        st.warning(f"⚠️ วอลุ่มสูงกว่าปกติ {volume_ratio:.2f} เท่า")
        if change_pct > 0:
            st.info("🔍 แรงซื้อเข้า")
        else:
            st.info("🔍 แรงขายออก")
    elif volume_ratio < 0.5:
        st.info(f"📊 วอลุ่มเบาบาง {volume_ratio:.2f} เท่า")
    else:
        st.success(f"✅ วอลุ่มปกติ {volume_ratio:.2f} เท่า")

# ================== Footer ==================

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"หุ้น: {symbol_display}")
with col2:
    st.caption(f"ข้อมูลล่าสุด: {df.index[-1].strftime('%Y-%m-%d')}")
with col3:
    st.caption(f"จำนวนหุ้นในระบบ: {len(thai_stocks)} ตัว")
