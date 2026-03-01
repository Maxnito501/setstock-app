"""
หน้า 2: วิเคราะห์หุ้นเล่นสั้น เวอร์ชัน InnovestX
- เชื่อมต่อข้อมูลจริงจาก InnovestX API
- ดึงราคาและ Bid/Offer 5 ช่อง
- วิเคราะห์วอลุ่ม 3 ช่องแรกตามกลยุทธ์นายพราน
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime, timedelta
import time

# เพิ่ม path เพื่อ import จาก utils
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import Settrade API
try:
    from utils.settrade_api import StockAPI
    api = StockAPI()
    api_ready = api.connected
except Exception as e:
    api_ready = False
    st.error(f"⚠️ ไม่สามารถเชื่อมต่อ InnovestX: {e}")

# กำหนดค่าเพจ
st.set_page_config(
    page_title="หุ้นเล่นสั้น - InnovestX",
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
    .bid-box {
        background: #dcfce7;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
    }
    .offer-box {
        background: #fee2e2;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
    }
    .signal-strong {
        background: #10b981;
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 50px;
        font-weight: bold;
    }
    .signal-warning {
        background: #f59e0b;
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 50px;
        font-weight: bold;
    }
    .signal-danger {
        background: #ef4444;
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 50px;
        font-weight: bold;
    }
    .wait-timer {
        background: #3b82f6;
        color: white;
        padding: 0.5rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

# ชื่อหน้า
st.markdown("""
<div style="display: flex; align-items: center; margin-bottom: 1rem;">
    <h1>⚡ วิเคราะห์หุ้นเล่นสั้น</h1>
    <span class="version-badge">InnovestX Real-time</span>
</div>
""", unsafe_allow_html=True)

# แสดงสถานะการเชื่อมต่อ
if api_ready:
    st.success("✅ เชื่อมต่อ InnovestX สำเร็จ พร้อมใช้งาน")
else:
    st.error("❌ ไม่สามารถเชื่อมต่อ InnovestX กรุณาตรวจสอบ API Key")
    st.stop()

st.markdown("---")

# Sidebar
with st.sidebar:
    st.subheader("🔍 เลือกหุ้น")
    
    symbol = st.text_input("รหัสหุ้น", "ADVANC").upper()
    
    st.markdown("---")
    st.subheader("⚙️ ตั้งค่า")
    
    # จำนวนช่องที่ต้องการวิเคราะห์
    layers = st.slider("จำนวนช่อง Bid/Offer ที่วิเคราะห์", 1, 5, 3)
    
    # Auto refresh
    auto_refresh = st.checkbox("Auto Refresh ทุก 20 วิ", value=False)
    
    st.markdown("---")
    if st.button("🔄 ดึงข้อมูลใหม่", use_container_width=True):
        st.rerun()

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"📊 ข้อมูลเรียลไทม์ {symbol}")
    
    # ดึงข้อมูลจาก InnovestX
    quote = api.get_quote(symbol)
    
    if quote['success']:
        # แสดง metric
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        
        with mcol1:
            st.metric(
                "ราคาล่าสุด", 
                f"฿{quote['price']:.2f}",
                f"{quote['change']:+.2f}"
            )
        with mcol2:
            st.metric("เปลี่ยนแปลง %", f"{quote['change_percent']:+.2f}%")
        with mcol3:
            st.metric("วอลุ่ม", f"{quote['volume']:,}")
        with mcol4:
            st.metric("เวลา", quote['timestamp'][11:19])
        
        # แสดง Bid/Offer
        st.markdown("### 📊 Bid/Offer 5 ช่อง")
        
        bid_cols = st.columns(5)
        offer_cols = st.columns(5)
        
        # Bid (ซื้อ)
        for i, b in enumerate(quote['bid'][:5]):
            with bid_cols[i]:
                st.markdown(f"""
                <div class="bid-box">
                    <b>B{i+1}</b><br>
                    ฿{b['price']:.2f}<br>
                    {b['volume']:,}
                </div>
                """, unsafe_allow_html=True)
        
        # Offer (ขาย)
        for i, o in enumerate(quote['offer'][:5]):
            with offer_cols[i]:
                st.markdown(f"""
                <div class="offer-box">
                    <b>O{i+1}</b><br>
                    ฿{o['price']:.2f}<br>
                    {o['volume']:,}
                </div>
                """, unsafe_allow_html=True)
        
        # วิเคราะห์วอลุ่มตามกลยุทธ์นายพราน
        st.markdown("---")
        st.subheader("🎯 วิเคราะห์ตามกลยุทธ์นายพราน")
        
        analysis = api.analyze_volume(symbol)
        
        acol1, acol2, acol3 = st.columns(3)
        
        with acol1:
            st.markdown(f"### {analysis['bid_volume_n']:,}")
            st.caption(f"วอลุ่มซื้อ {layers} ช่องแรก")
        
        with acol2:
            st.markdown(f"### {analysis['offer_volume_n']:,}")
            st.caption(f"วอลุ่มขาย {layers} ช่องแรก")
        
        with acol3:
            st.markdown(f"### {analysis['ratio']}")
            st.caption("อัตราส่วน ซื้อ/ขาย")
        
        # แสดงสัญญาณ
        signal_color = {
            'green': '🟢', 'yellow': '🟡', 'red': '🔴', 'gray': '⚪'
        }.get(analysis['color'], '⚪')
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
            <h2>{signal_color} {analysis['signal']}</h2>
            <h3>⚔️ กลยุทธ์: {analysis['hunter_strategy']}</h3>
            <p>คำแนะนำ: {analysis['action']}</p>
        </div>
        """, unsafe_allow_html=True)
        
    elif 'wait' in quote:
        # กำลังรอ
        wait_time = quote['wait']
        st.markdown(f"""
        <div class="wait-timer">
            ⏳ ต้องรอ {wait_time:.0f} วินาที ก่อนเรียกข้อมูลใหม่
        </div>
        """, unsafe_allow_html=True)
        
        # นับถอยหลัง
        if auto_refresh:
            time.sleep(1)
            st.rerun()
    else:
        st.error(f"❌ {quote['error']}")

with col2:
    st.subheader("📈 ข้อมูลเพิ่มเติม")
    
    if quote['success']:
        # ราคาสูง/ต่ำ
        st.markdown("### ราคาสูง-ต่ำ")
        st.markdown(f"- สูงสุดวัน: ฿{quote['high']:.2f}")
        st.markdown(f"- ต่ำสุดวัน: ฿{quote['low']:.2f}")
        st.markdown(f"- เปิด: ฿{quote['open']:.2f}")
        st.markdown(f"- ปิดก่อนหน้า: ฿{quote['prev_close']:.2f}")
        
        # สรุป Bid/Offer
        st.markdown("### สรุปวอลุ่ม")
        st.markdown(f"- รวมวอลุ่มซื้อ: {quote['bid_volume']:,}")
        st.markdown(f"- รวมวอลุ่มขาย: {quote['offer_volume']:,}")
        st.markdown(f"- อัตราส่วนรวม: {quote['bid_volume']/quote['offer_volume']:.2f}" if quote['offer_volume'] > 0 else "-")
        
        # คำแนะนำจากกุนซือ
        st.markdown("---")
        st.markdown("### 🎯 คำแนะนำ")
        
        ratio = analysis['ratio']
        if ratio >= 2:
            st.success("""
            **ซุนวู:** "จังหวะดี เตรียมช้อน"
            **เลโอนิดัส:** "THIS IS SPARTA! จัดการ!"
            """)
        elif ratio >= 1.5:
            st.info("""
            **บัฟเฟต์:** "รออีกนิด ดูแนวรับ"
            """)
        elif ratio <= 0.5:
            st.error("""
            **ซุนวู:** "三十六计 - หนี!"
            """)
        else:
            st.warning("""
            **ขงเบ้ง:** "รอให้ชัดเจนก่อน"
            """)
    else:
        st.info("รอข้อมูล...")

# Auto refresh
if auto_refresh and quote.get('success'):
    time.sleep(20)
    st.rerun()

st.markdown("---")
st.caption(f"ข้อมูลจาก InnovestX | อัปเดตล่าสุด: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")