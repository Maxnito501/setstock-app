"""
หน้า 2: วิเคราะห์หุ้นเล่นสั้น (ตัวเต็ม)
- รองรับการ Refresh และ Clear Cache
- กราฟเทคนิคอลครบ (RSI, MACD, Stochastic, Bollinger Bands)
- วิเคราะห์กลยุทธ์นายพราน
- จุดซื้อขาย Cut Loss
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import sys
import os

# เพิ่ม path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import ตัวช่วย
from utils.yahoo_fetcher import YahooFetcher
from utils.technical_analyzer import TechnicalAnalyzer

# ตั้งค่าเพจ
st.set_page_config(
    page_title="หุ้นเล่นสั้น",
    page_icon="⚡",
    layout="wide"
)

# สร้าง instances
fetcher = YahooFetcher()
analyzer = TechnicalAnalyzer()

# Initialize session state สำหรับ force refresh
if 'force_refresh' not in st.session_state:
    st.session_state.force_refresh = False
if 'last_symbol' not in st.session_state:
    st.session_state.last_symbol = 'ADVANC'

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
    .strategy-box {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .whale-rider { background: #d4edda; border-left: 5px solid #28a745; }
    .reversal { background: #fff3cd; border-left: 5px solid #ffc107; }
    .panic { background: #f8d7da; border-left: 5px solid #dc3545; }
    .tired { background: #e2e3e5; border-left: 5px solid #6c757d; }
    .trend { background: #cce5ff; border-left: 5px solid #007bff; }
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
    .refresh-button {
        background: #3b82f6;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# ส่วนหัว
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between;">
    <div style="display: flex; align-items: center;">
        <h1>⚡ วิเคราะห์หุ้นเล่นสั้น</h1>
        <span class="version-badge">V2.0 พร้อม Refresh</span>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ================== Sidebar ==================

with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/stocks--v1.png", width=60)
    st.subheader("🔍 เลือกหุ้น")
    
    # รายชื่อหุ้น
    stock_list = list(fetcher.thai_stocks.keys())
    selected_symbol = st.selectbox("เลือกหุ้น", stock_list, index=stock_list.index(st.session_state.last_symbol) if st.session_state.last_symbol in stock_list else 0)
    
    # อัปเดต session state
    if selected_symbol != st.session_state.last_symbol:
        st.session_state.last_symbol = selected_symbol
        st.session_state.force_refresh = False
    
    st.markdown("---")
    st.subheader("📊 ตั้งค่า")
    period = st.selectbox("ช่วงเวลา", ["1mo", "3mo", "6mo", "1y"], index=1)
    cutloss_pct = st.slider("Cut Loss %", 2, 10, 5)
    takeprofit_pct = st.slider("Take Profit %", 3, 20, 10)
    
    # ===== จัดการ Cache =====
    st.markdown("---")
    st.subheader("🔄 จัดการข้อมูล")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 ล้าง Cache", use_container_width=True):
            fetcher.clear_all_cache()
            st.success("✅ ล้าง cache เรียบร้อย")
            st.rerun()
    
    with col2:
        if st.button("⚡ รีเฟรช", use_container_width=True):
            st.session_state.force_refresh = True
            st.rerun()
    
    # แสดงสถานะ cache
    st.caption(f"หุ้นปัจจุบัน: {selected_symbol}")
    
    # ===== ข้อมูล Bid/Offer =====
    st.markdown("---")
    st.subheader("🐋 ข้อมูล Bid/Offer")
    use_bid_offer = st.checkbox("ป้อนข้อมูล Bid/Offer")
    
    bid_text = ""
    offer_text = ""
    if use_bid_offer:
        bid_text = st.text_area("Bid 5 ช่อง", placeholder="1200 2500 3800 1500 900", height=100)
        offer_text = st.text_area("Offer 5 ช่อง", placeholder="800 1900 3200 4500 2300", height=100)

# ================== ดึงข้อมูล ==================

# ทดสอบการเชื่อมต่อ
if not fetcher.test_connection(selected_symbol):
    st.warning("⚠️ กำลังทดสอบการเชื่อมต่อ Yahoo Finance...")

# ดึงข้อมูล
with st.spinner(f"📥 กำลังโหลดข้อมูล {selected_symbol}..."):
    if st.session_state.force_refresh:
        data = fetcher.force_refresh(selected_symbol, period)
        st.session_state.force_refresh = False
    else:
        data = fetcher.fetch_data(selected_symbol, period=period)

if data is None:
    st.error(f"❌ ไม่สามารถดึงข้อมูล {selected_symbol} ได้")
    st.info("""
    **สาเหตุที่เป็นไปได้:**
    - Yahoo Finance อาจมีปัญหา
    - การเชื่อมต่ออินเทอร์เน็ตไม่เสถียร
    - เซิร์ฟเวอร์ Yahoo ตอบสนองช้า
    
    **แนะนำ:**
    - กดปุ่ม "รีเฟรช" ด้านซ้าย
    - หรือกด "ล้าง Cache" แล้วลองใหม่
    """)
    
    # แสดงปุ่มให้ลองใหม่
    if st.button("🔄 ลองใหม่อีกครั้ง"):
        st.rerun()
    st.stop()

df = data['df']

# คำนวณ indicators
df = analyzer.add_all_indicators(df)

# ข้อมูลล่าสุด
last = df.iloc[-1]
prev = df.iloc[-2]

# ================== แสดงข้อมูลเบื้องต้น ==================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "ราคาปัจจุบัน",
        f"฿{last['Close']:.2f}",
        f"{last['Close'] - prev['Close']:+.2f} ({((last['Close']-prev['Close'])/prev['Close']*100):+.2f}%)"
    )

with col2:
    rsi_color = "🔴" if last['RSI_14'] > 70 else "🟢" if last['RSI_14'] < 30 else "⚪"
    st.metric("RSI (14)", f"{rsi_color} {last['RSI_14']:.1f}")

with col3:
    macd_status = "🟢 Bullish" if last['MACD'] > last['Signal'] else "🔴 Bearish"
    st.metric("MACD", macd_status)

with col4:
    vol_ratio = last['Volume_Ratio'] if not pd.isna(last['Volume_Ratio']) else 1
    vol_color = "🔴" if vol_ratio > 1.5 else "🟢" if vol_ratio < 0.7 else "⚪"
    st.metric("Volume Ratio", f"{vol_color} {vol_ratio:.2f}x")

# ================== กลยุทธ์นายพราน ==================

st.markdown("---")
st.subheader("🐋 วิเคราะห์ตามกลยุทธ์นายพราน")

# แปลง Bid/Offer ที่ป้อน
bid_volumes = None
offer_volumes = None

if use_bid_offer and bid_text and offer_text:
    try:
        bid_volumes = [int(x) for x in bid_text.split()]
        offer_volumes = [int(x) for x in offer_text.split()]
    except:
        st.warning("⚠️ รูปแบบข้อมูล Bid/Offer ไม่ถูกต้อง")

# วิเคราะห์กลยุทธ์
hunter = analyzer.analyze_hunter_strategy(df, bid_volumes, offer_volumes)

# แสดงกลยุทธ์ที่พบ
if hunter['strategies']:
    cols = st.columns(min(len(hunter['strategies']), 3))
    for i, strategy in enumerate(hunter['strategies']):
        with cols[i % 3]:
            box_class = {
                'whale_rider': 'whale-rider',
                'reversal': 'reversal',
                'panic': 'panic',
                'tired': 'tired',
                'trend': 'trend'
            }.get(strategy.get('name', '').split()[0], '')
            
            st.markdown(f"""
            <div class="strategy-box {box_class}">
                <h3>{strategy['name']}</h3>
                <p><b>{strategy['action']}</b></p>
                <p>{strategy['desc']}</p>
                <p>ความเชื่อมั่น: {strategy['confidence']}</p>
            </div>
            """, unsafe_allow_html=True)

if hunter['signals']:
    st.info("🔄 " + " | ".join(hunter['signals']))

# ================== Tabs ==================

tab1, tab2, tab3 = st.tabs(["📈 กราฟเทคนิคอล", "🎯 จุดซื้อขาย", "📊 ข้อมูลเพิ่มเติม"])

# ================== TAB 1: กราฟเทคนิคอล ==================

with tab1:
    # สร้างกราฟ 4 แถว
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.4, 0.2, 0.2, 0.2],
        subplot_titles=('ราคา', 'Volume', 'RSI', 'MACD')
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
        go.Scatter(x=df.index, y=df['MA20'], name='MA20', line=dict(color='orange', width=1.5)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['MA50'], name='MA50', line=dict(color='blue', width=1.5)),
        row=1, col=1
    )
    
    # Bollinger Bands
    fig.add_trace(
        go.Scatter(x=df.index, y=df['BB_Upper'], name='BB Upper',
                  line=dict(color='gray', width=1, dash='dash')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['BB_Lower'], name='BB Lower',
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
        go.Scatter(x=df.index, y=df['RSI_14'], name='RSI', line=dict(color='purple', width=2)),
        row=3, col=1
    )
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    # MACD
    fig.add_trace(
        go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='blue', width=2)),
        row=4, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Signal'], name='Signal', line=dict(color='red', width=2)),
        row=4, col=1
    )
    
    fig.update_layout(
        height=800,
        showlegend=True,
        hovermode='x unified',
        xaxis_rangeslider_visible=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ================== TAB 2: จุดซื้อขาย ==================

with tab2:
    col1, col2 = st.columns(2)
    
    points = analyzer.get_buy_sell_points(df, cutloss_pct, takeprofit_pct)
    
    with col1:
        st.markdown("### 📊 สถานะปัจจุบัน")
        st.markdown(f"**แนวโน้ม:** {hunter['primary'] if hunter['primary'] else 'sideways'}")
        st.markdown(f"**RSI (14):** {last['RSI_14']:.1f}")
        st.markdown(f"**RSI (7):** {last['RSI_7']:.1f}")
        st.markdown(f"**MACD:** {'Bullish' if last['MACD'] > last['Signal'] else 'Bearish'}")
        st.markdown(f"**Stochastic:** {last['Stoch_K']:.1f}")
        st.markdown(f"**ATR:** {last['ATR_Pct']:.2f}%")
        st.markdown(f"**แนวรับ 20:** ฿{last['Support_20']:.2f}")
        st.markdown(f"**แนวต้าน 20:** ฿{last['Resistance_20']:.2f}")
        if last['MA50'] and not pd.isna(last['MA50']):
            st.markdown(f"**MA50:** ฿{last['MA50']:.2f}")
    
    with col2:
        st.markdown("### 💰 จุดซื้อขายแนะนำ")
        
        if points['buy_points']:
            st.markdown("#### 🟢 จุดซื้อ")
            for i, p in enumerate(points['buy_points'][:3]):
                diff = ((p - points['current_price']) / points['current_price']) * 100
                st.markdown(f"- ฿{p:.2f} ({diff:+.1f}%)")
        
        if points['sell_points']:
            st.markdown("#### 🔴 จุดขาย")
            for i, p in enumerate(points['sell_points'][:3]):
                diff = ((p - points['current_price']) / points['current_price']) * 100
                st.markdown(f"- ฿{p:.2f} ({diff:+.1f}%)")
        
        st.markdown("#### ⛔ Cut Loss")
        cut_diff = ((points['cut_loss'] - points['current_price']) / points['current_price']) * 100
        st.markdown(f"- ฿{points['cut_loss']:.2f} ({cut_diff:+.1f}%)")
        
        st.markdown("#### 🎯 Take Profit")
        tp1_diff = ((points['take_profit_1'] - points['current_price']) / points['current_price']) * 100
        tp2_diff = ((points['take_profit_2'] - points['current_price']) / points['current_price']) * 100
        st.markdown(f"- 1: ฿{points['take_profit_1']:.2f} ({tp1_diff:+.1f}%)")
        st.markdown(f"- 2: ฿{points['take_profit_2']:.2f} ({tp2_diff:+.1f}%)")
        
        # Reward/Risk
        risk = points['current_price'] - points['cut_loss']
        reward = points['take_profit_1'] - points['current_price']
        rr_ratio = reward / risk if risk > 0 else 0
        
        st.markdown("---")
        st.markdown(f"**Reward/Risk:** {rr_ratio:.2f}")
        if rr_ratio >= 2:
            st.success("✅ คุ้มค่า")
        elif rr_ratio >= 1:
            st.warning("⚠️ พอรับได้")
        else:
            st.error("❌ ไม่คุ้ม")

# ================== TAB 3: ข้อมูลเพิ่มเติม ==================

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 สถิติรายวัน")
        st.markdown(f"**เปิด:** ฿{last['Open']:.2f}")
        st.markdown(f"**สูงสุด:** ฿{last['High']:.2f}")
        st.markdown(f"**ต่ำสุด:** ฿{last['Low']:.2f}")
        st.markdown(f"**ปิด:** ฿{last['Close']:.2f}")
        st.markdown(f"**วอลุ่ม:** {last['Volume']:,.0f}")
        st.markdown(f"**วอลุ่มเฉลี่ย 20:** {last['Volume_MA20']:,.0f}")
    
    with col2:
        st.markdown("### 📊 ข้อมูลบริษัท")
        st.markdown(f"**ชื่อ:** {data['company_name']}")
        st.markdown(f"**หมวด:** {data['sector']}")
        st.markdown(f"**52-week สูง:** ฿{data['high_52w']:.2f}")
        st.markdown(f"**52-week ต่ำ:** ฿{data['low_52w']:.2f}")
        st.markdown(f"**PE:** {data['info'].get('trailingPE', 'N/A')}")
        st.markdown(f"**PB:** {data['info'].get('priceToBook', 'N/A')}")
    
    # แสดงข้อมูลการโหลด
    st.markdown("---")
    st.markdown("### ℹ️ ข้อมูลการโหลด")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption(f"โหลดเมื่อ: {data['last_update'][:10]}")
    with col2:
        st.caption(f"เวลา: {data['last_update'][11:19]}")
    with col3:
        cache_status = "ใช้ Cache" if not st.session_state.force_refresh else "โหลดใหม่"
        st.caption(f"สถานะ: {cache_status}")

# ================== Footer ==================

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"หุ้น: {selected_symbol}")
with col2:
    st.caption(f"ข้อมูลล่าสุด: {df.index[-1].strftime('%Y-%m-%d')}")
with col3:
    st.caption("⚡ กดรีเฟรชที่เมนูด้านซ้ายเมื่อข้อมูลไม่มา")
