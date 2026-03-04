"""
หน้า 2: วิเคราะห์หุ้นเล่นสั้น
ใช้ YahooFetcher และ TechnicalAnalyzer
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

# Import ตัวช่วยใหม่
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

# CSS
st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)

# ส่วนหัว
st.title("⚡ วิเคราะห์หุ้นเล่นสั้น")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.subheader("🔍 เลือกหุ้น")
    
    # รายชื่อหุ้น
    stock_list = list(fetcher.thai_stocks.keys())
    symbol = st.selectbox("เลือกหุ้น", stock_list, index=0)
    
    st.markdown("---")
    st.subheader("📊 ตั้งค่า")
    period = st.selectbox("ช่วงเวลา", ["1mo", "3mo", "6mo", "1y"], index=1)
    cutloss_pct = st.slider("Cut Loss %", 2, 10, 5)
    takeprofit_pct = st.slider("Take Profit %", 3, 20, 10)
    
    # ส่วนป้อน Bid/Offer ด้วยตนเอง (สำหรับกลยุทธ์นายพราน)
    st.markdown("---")
    st.subheader("🐋 ข้อมูล Bid/Offer")
    use_bid_offer = st.checkbox("ป้อนข้อมูล Bid/Offer")
    
    bid_text = ""
    offer_text = ""
    if use_bid_offer:
        bid_text = st.text_area("Bid 5 ช่อง (คั่นด้วย space)", 
                                placeholder="เช่น 1200 2500 3800 1500 900")
        offer_text = st.text_area("Offer 5 ช่อง (คั่นด้วย space)", 
                                 placeholder="เช่น 800 1900 3200 4500 2300")
    
    if st.button("🔄 โหลดข้อมูลใหม่", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ดึงข้อมูล
with st.spinner(f"กำลังโหลดข้อมูล {symbol}..."):
    data = fetcher.fetch_data(symbol, period=period)

if data is None:
    st.error(f"❌ ไม่สามารถดึงข้อมูล {symbol} ได้")
    st.stop()

df = data['df']

# คำนวณ indicators
df = analyzer.add_all_indicators(df)

# ข้อมูลล่าสุด
last = df.iloc[-1]
prev = df.iloc[-2]

# ========== แสดงข้อมูลเบื้องต้น ==========
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "ราคาปัจจุบัน",
        f"฿{last['Close']:.2f}",
        f"{last['Close'] - prev['Close']:+.2f} ({((last['Close']-prev['Close'])/prev['Close']*100):+.2f}%)"
    )

with col2:
    st.metric("RSI (14)", f"{last['RSI_14']:.1f}")

with col3:
    st.metric("MACD", f"{last['MACD']:.3f}")

with col4:
    st.metric("Volume Ratio", f"{last['Volume_Ratio']:.2f}x")

# ========== กลยุทธ์นายพราน ==========
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
        st.warning("⚠️ รูปแบบข้อมูลไม่ถูกต้อง")

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

# ========== Tabs ==========
tab1, tab2, tab3 = st.tabs(["📈 กราฟเทคนิคอล", "🎯 จุดซื้อขาย", "📊 ข้อมูลเพิ่มเติม"])

# ========== TAB 1: กราฟเทคนิคอล ==========
with tab1:
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
            name='ราคา'
        ),
        row=1, col=1
    )
    
    # Moving Averages
    fig.add_trace(
        go.Scatter(x=df.index, y=df['MA20'], name='MA20', line=dict(color='orange')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['MA50'], name='MA50', line=dict(color='blue')),
        row=1, col=1
    )
    
    # Bollinger Bands
    fig.add_trace(
        go.Scatter(x=df.index, y=df['BB_Upper'], name='BB Upper',
                  line=dict(color='gray', dash='dash')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['BB_Lower'], name='BB Lower',
                  line=dict(color='gray', dash='dash')),
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
        go.Scatter(x=df.index, y=df['RSI_14'], name='RSI', line=dict(color='purple')),
        row=3, col=1
    )
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    # MACD
    fig.add_trace(
        go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='blue')),
        row=4, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Signal'], name='Signal', line=dict(color='red')),
        row=4, col=1
    )
    
    fig.update_layout(height=800, showlegend=True, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

# ========== TAB 2: จุดซื้อขาย ==========
with tab2:
    col1, col2 = st.columns(2)
    
    points = analyzer.get_buy_sell_points(df, cutloss_pct, takeprofit_pct)
    
    with col1:
        st.markdown("### 📊 สถานะปัจจุบัน")
        st.markdown(f"**แนวโน้ม:** {hunter['primary'] if hunter['primary'] else 'sideways'}")
        st.markdown(f"**RSI:** {last['RSI_14']:.1f}")
        st.markdown(f"**MACD:** {'Bullish' if last['MACD'] > last['Signal'] else 'Bearish'}")
        st.markdown(f"**Stochastic:** {last['Stoch_K']:.1f}")
        st.markdown(f"**ATR:** {last['ATR_Pct']:.2f}%")
        st.markdown(f"**แนวรับ 20:** ฿{last['Support_20']:.2f}")
        st.markdown(f"**แนวต้าน 20:** ฿{last['Resistance_20']:.2f}")
    
    with col2:
        st.markdown("### 💰 จุดซื้อขายแนะนำ")
        if points['buy_points']:
            st.markdown("#### 🟢 จุดซื้อ")
            for p in points['buy_points'][:3]:
                st.markdown(f"- ฿{p:.2f}")
        
        if points['sell_points']:
            st.markdown("#### 🔴 จุดขาย")
            for p in points['sell_points'][:3]:
                st.markdown(f"- ฿{p:.2f}")
        
        st.markdown("#### ⛔ Cut Loss")
        st.markdown(f"- ฿{points['cut_loss']:.2f} (-{cutloss_pct}%)")
        
        st.markdown("#### 🎯 Take Profit")
        st.markdown(f"- 1: ฿{points['take_profit_1']:.2f} (+{takeprofit_pct}%)")
        st.markdown(f"- 2: ฿{points['take_profit_2']:.2f} (+{takeprofit_pct*2}%)")

# ========== TAB 3: ข้อมูลเพิ่มเติม ==========
with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 สถิติรายวัน")
        st.markdown(f"**เปิด:** ฿{last['Open']:.2f}")
        st.markdown(f"**สูงสุด:** ฿{last['High']:.2f}")
        st.markdown(f"**ต่ำสุด:** ฿{last['Low']:.2f}")
        st.markdown(f"**วอลุ่ม:** {last['Volume']:,.0f}")
        st.markdown(f"**วอลุ่มเฉลี่ย 20:** {last['Volume_MA20']:,.0f}")
    
    with col2:
        st.markdown("### 📊 ข้อมูลบริษัท")
        st.markdown(f"**ชื่อ:** {data['company_name']}")
        st.markdown(f"**หมวด:** {data['sector']}")
        st.markdown(f"**52-week สูง:** ฿{data['high_52w']:.2f}")
        st.markdown(f"**52-week ต่ำ:** ฿{data['low_52w']:.2f}")

# Footer
st.markdown("---")
st.caption(f"อัปเดตล่าสุด: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
