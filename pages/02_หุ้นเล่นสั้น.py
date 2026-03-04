"""
หน้า 2: วิเคราะห์หุ้นเล่นสั้น (Hybrid Version)
- เลือกได้: กรอก Bid/Offer เอง หรือ Auto จาก Docker
- กราฟเทคนิคอลครบ (RSI, MACD, Bollinger Bands)
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
from addons.hybrid_fetcher import HybridFetcher
from addons.docker_manager import DockerManager
from utils.technical_analyzer import TechnicalAnalyzer

# ตั้งค่าเพจ
st.set_page_config(
    page_title="หุ้นเล่นสั้น",
    page_icon="⚡",
    layout="wide"
)

# สร้าง instances
fetcher = HybridFetcher()
analyzer = TechnicalAnalyzer()
docker = DockerManager()

# Initialize session state
if 'force_refresh' not in st.session_state:
    st.session_state.force_refresh = False
if 'last_symbol' not in st.session_state:
    st.session_state.last_symbol = 'ADVANC'
if 'docker_status' not in st.session_state:
    st.session_state.docker_status = docker.get_container_status()

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
    .docker-status {
        background: #f0f2f6;
        padding: 0.5rem;
        border-radius: 5px;
        font-size: 0.9rem;
    }
    .bid-box {
        background: #dcfce7;
        padding: 0.3rem;
        border-radius: 5px;
        text-align: center;
    }
    .offer-box {
        background: #fee2e2;
        padding: 0.3rem;
        border-radius: 5px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ส่วนหัว
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between;">
    <div style="display: flex; align-items: center;">
        <h1>⚡ วิเคราะห์หุ้นเล่นสั้น</h1>
        <span class="version-badge">Hybrid v2.0</span>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ================== Sidebar ==================

with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/stocks--v1.png", width=60)
    st.subheader("🔍 เลือกหุ้น")
    
    # รายชื่อหุ้น
    stock_list = [
        'ADVANC', 'AOT', 'BDMS', 'BH', 'BTS', 'CPALL', 'CPF', 'CRC',
        'DTAC', 'GULF', 'INTUCH', 'IVL', 'KBANK', 'KTB', 'PTT', 'PTTEP',
        'SCB', 'SCC', 'SIRI', 'TISCO', 'TRUE', 'BANPU', 'CHG', 'COM7',
        'EA', 'JAS', 'LH', 'MINT', 'PTG', 'RATCH', 'SAWAD', 'TOP', 'TU', 'WHA', 'HMPRO'
    ]
    
    selected_symbol = st.selectbox(
        "เลือกหุ้น", 
        stock_list, 
        index=stock_list.index(st.session_state.last_symbol) 
        if st.session_state.last_symbol in stock_list else 0
    )
    
    # อัปเดต session state
    if selected_symbol != st.session_state.last_symbol:
        st.session_state.last_symbol = selected_symbol
        st.session_state.force_refresh = False
    
    st.markdown("---")
    st.subheader("📊 ตั้งค่า")
    period = st.selectbox("ช่วงเวลา", ["1D", "5D", "1M", "3M", "6M", "1Y"], index=3)
    cutloss_pct = st.slider("Cut Loss %", 2, 10, 5)
    takeprofit_pct = st.slider("Take Profit %", 3, 20, 10)
    
    # ===== จัดการข้อมูล =====
    st.markdown("---")
    st.subheader("🔄 จัดการข้อมูล")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 รีเฟรช", use_container_width=True):
            st.session_state.force_refresh = True
            st.rerun()
    with col2:
        if st.button("🧹 ล้าง Cache", use_container_width=True):
            st.cache_data.clear()
            st.success("✅ Cache cleared")
            st.rerun()
    
    # ===== ข้อมูล Bid/Offer =====
    st.markdown("---")
    st.subheader("🐋 ข้อมูล Bid/Offer")
    
    bid_source = st.radio(
        "เลือกแหล่งข้อมูล",
        ["✍️ กรอกเอง", "🤖 Auto (Docker)"],
        horizontal=True,
        key="bid_source"
    )
    
    bid_volumes_text = ""
    offer_volumes_text = ""
    
    if bid_source == "✍️ กรอกเอง":
        st.markdown("##### วางข้อมูล Bid 5 ช่อง (คั่นด้วย space)")
        bid_volumes_text = st.text_area(
            "Bid volumes",
            placeholder="1200 2500 3800 1500 900",
            height=80,
            key="bid_manual",
            label_visibility="collapsed"
        )
        
        st.markdown("##### วางข้อมูล Offer 5 ช่อง (คั่นด้วย space)")
        offer_volumes_text = st.text_area(
            "Offer volumes",
            placeholder="800 1900 3200 4500 2300",
            height=80,
            key="offer_manual",
            label_visibility="collapsed"
        )
        
        if st.button("🔍 วิเคราะห์ Bid/Offer", use_container_width=True):
            st.session_state.analyze_bid_offer = True
        else:
            st.session_state.analyze_bid_offer = False
    
    else:  # Auto mode
        st.markdown("##### สถานะ Docker")
        docker_status = st.session_state.docker_status
        status_color = "🟢" if docker_status.get('service_ready') else "🔴"
        st.markdown(f"""
        <div class="docker-status">
            {status_color} Service: {'พร้อม' if docker_status.get('service_ready') else 'ไม่พร้อม'}<br>
            Docker: {'ติดตั้ง' if docker_status.get('docker_installed') else 'ไม่มี'}<br>
            Container: {'กำลังรัน' if docker_status.get('container_running') else 'หยุด'}
        </div>
        """, unsafe_allow_html=True)
        
        if not docker_status.get('service_ready'):
            if st.button("▶️ Start Docker", use_container_width=True):
                with st.spinner("กำลังเริ่ม Docker..."):
                    result = docker.start_container(build=True)
                    if result['success']:
                        st.success("✅ Docker started")
                        st.session_state.docker_status = docker.get_container_status()
                        st.rerun()
                    else:
                        st.error(f"❌ {result.get('error', 'Failed')}")

# ================== ดึงข้อมูล ==================

# แปลง period
period_map = {
    "1D": "1D", "5D": "5D", "1M": "1M", 
    "3M": "3M", "6M": "6M", "1Y": "1Y"
}
tv_interval = period_map.get(period, "3M")

# ดึงข้อมูล
with st.spinner(f"📥 กำลังโหลดข้อมูล {selected_symbol}..."):
    # ตรวจสอบว่าต้องการ Bid/Offer หรือไม่
    get_bid_offer = (bid_source == "🤖 Auto (Docker)" and 
                     st.session_state.docker_status.get('service_ready', False))
    
    data = fetcher.get_sync_data(
        symbol=selected_symbol,
        interval=tv_interval,
        bars=200,
        get_bid_offer=get_bid_offer
    )

# ตรวจสอบผลลัพธ์
if not data['tradingview']['success']:
    st.error(f"❌ ไม่สามารถดึงข้อมูล {selected_symbol} จาก TradingView ได้")
    st.info(f"สาเหตุ: {data['tradingview'].get('error', 'Unknown error')}")
    
    if st.button("🔄 ลองใหม่"):
        st.rerun()
    st.stop()

# ดึง DataFrame
df = data['tradingview']['df']

# คำนวณ indicators
df = analyzer.add_all_indicators(df)

# ข้อมูลล่าสุด
last = df.iloc[-1]
prev = df.iloc[-2] if len(df) > 1 else last

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

# ================== วิเคราะห์ Bid/Offer ตามกลยุทธ์นายพราน ==================

if bid_source == "✍️ กรอกเอง" and bid_volumes_text and offer_volumes_text:
    try:
        # แปลงข้อความเป็นตัวเลข (รองรับ comma)
        bid_volumes = [int(x.replace(',', '')) for x in bid_volumes_text.split()]
        offer_volumes = [int(x.replace(',', '')) for x in offer_volumes_text.split()]
        
        if len(bid_volumes) >= 3 and len(offer_volumes) >= 3:
            st.markdown("---")
            st.subheader("🐋 ผลวิเคราะห์ Bid/Offer")
            
            bid_3 = sum(bid_volumes[:3])
            offer_3 = sum(offer_volumes[:3])
            ratio = bid_3 / offer_3 if offer_3 > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Bid 3 ช่อง", f"{bid_3:,}")
            with col2:
                st.metric("Offer 3 ช่อง", f"{offer_3:,}")
            with col3:
                st.metric("อัตราส่วน", f"{ratio:.2f}")
            
            # วิเคราะห์ตามกลยุทธ์นายพราน
            if ratio >= 2:
                strategy_class = "whale-rider"
                strategy_name = "🐋 Whale Rider"
                action = "✅ ตามช้อน"
                desc = f"วอลุ่มซื้อหนา {ratio:.2f} เท่า"
            elif ratio >= 1.5:
                strategy_class = "reversal"
                strategy_name = "🎯 จับจังหวะกลับตัว"
                action = "⏳ รอดู"
                desc = f"วอลุ่มซื้อเริ่มเข้า {ratio:.2f} เท่า"
            elif ratio <= 0.5:
                strategy_class = "panic"
                strategy_name = "💀 หนีทันที"
                action = "⚠️ ขาย/ชอร์ต"
                desc = f"วอลุ่มขายหนา {1/ratio:.2f} เท่า"
            else:
                strategy_class = "tired"
                strategy_name = "🎣 รอซ้ำยามเปลี้ย"
                action = "👀 เฝ้าดู"
                desc = f"วอลุ่มสมดุล {ratio:.2f} เท่า"
            
            st.markdown(f"""
            <div class="strategy-box {strategy_class}">
                <h3>{strategy_name}</h3>
                <p><b>{action}</b></p>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # แสดง Bid/Offer 5 ช่อง
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 🟢 Bid 5 ช่อง")
                for i, v in enumerate(bid_volumes[:5], 1):
                    st.markdown(f"B{i}: {v:,}")
            
            with col2:
                st.markdown("#### 🔴 Offer 5 ช่อง")
                for i, v in enumerate(offer_volumes[:5], 1):
                    st.markdown(f"O{i}: {v:,}")
            
    except Exception as e:
        st.error(f"❌ รูปแบบข้อมูลไม่ถูกต้อง: {e}")

elif bid_source == "🤖 Auto (Docker)" and data.get('bid_offer') and data['bid_offer']['success']:
    st.markdown("---")
    st.subheader("🐋 ข้อมูล Bid/Offer จาก Docker")
    
    bid_offer = data['bid_offer']
    bid_volumes = [b['volume'] for b in bid_offer['bid'][:5]]
    offer_volumes = [o['volume'] for o in bid_offer['offer'][:5]]
    
    analysis = fetcher.analyze_volume_layers(bid_offer)
    
    if analysis:
        strategy_class = {
            '🐋 Whale Rider': 'whale-rider',
            '🎯 จับจังหวะกลับตัว': 'reversal',
            '💀 หนีทันที': 'panic',
            '🎣 รอซ้ำยามเปลี้ย': 'tired'
        }.get(analysis['strategy'], '')
        
        st.markdown(f"""
        <div class="strategy-box {strategy_class}">
            <h3>{analysis['strategy']}</h3>
            <p><b>{analysis['action']}</b></p>
            <p>{analysis['desc']}</p>
            <p>วอลุ่มซื้อ 3 ช่อง: {analysis['bid_3']:,} | วอลุ่มขาย 3 ช่อง: {analysis['offer_3']:,}</p>
            <p>อัตราส่วน: {analysis['ratio']:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # แสดง Bid/Offer 5 ช่อง
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🟢 Bid 5 ช่อง")
            for i, b in enumerate(bid_offer['bid'][:5], 1):
                st.markdown(f"B{i}: ฿{b['price']:.2f} | {b['volume']:,}")
        
        with col2:
            st.markdown("#### 🔴 Offer 5 ช่อง")
            for i, o in enumerate(bid_offer['offer'][:5], 1):
                st.markdown(f"O{i}: ฿{o['price']:.2f} | {o['volume']:,}")

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
        trend = "ขาขึ้น" if last['Close'] > last['MA20'] else "ขาลง"
        st.markdown(f"**แนวโน้ม:** {trend}")
        st.markdown(f"**RSI (14):** {last['RSI_14']:.1f}")
        st.markdown(f"**MACD:** {'Bullish' if last['MACD'] > last['Signal'] else 'Bearish'}")
        st.markdown(f"**ATR:** {last['ATR_Pct']:.2f}%")
        st.markdown(f"**แนวรับ 20:** ฿{last['Support_20']:.2f}")
        st.markdown(f"**แนวต้าน 20:** ฿{last['Resistance_20']:.2f}")
    
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
        st.markdown("### ℹ️ ข้อมูลระบบ")
        st.markdown(f"**แหล่งข้อมูลหลัก:** TradingView (tvdatafeed)")
        st.markdown(f"**Bid/Offer:** {'กรอกเอง' if bid_source=='✍️ กรอกเอง' else 'Auto'}")
        st.markdown(f"**เวลาที่โหลด:** {data['timestamp'][:19]}")
        st.markdown(f"**จำนวนข้อมูล:** {len(df)} วัน")

# ================== Footer ==================

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"หุ้น: {selected_symbol}")
with col2:
    st.caption(f"ข้อมูลล่าสุด: {df.index[-1].strftime('%Y-%m-%d')}")
with col3:
    st.caption("⚡ Hybrid: กรอกเอง / Docker")
