"""
หน้า 2: วิเคราะห์หุ้นเล่นสั้น
ใช้ Yahoo Finance ดึงข้อมูล
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime
import time

# เพิ่ม path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import API
try:
    from utils.settrade_api import StockAPI
    api = StockAPI()
    api_ready = True
except Exception as e:
    api_ready = False
    st.error(f"⚠️ ไม่สามารถเชื่อมต่อ: {e}")

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
    .signal-high {
        background: #ef4444;
        color: white;
        padding: 0.5rem;
        border-radius: 10px;
        text-align: center;
    }
    .signal-medium {
        background: #f59e0b;
        color: white;
        padding: 0.5rem;
        border-radius: 10px;
        text-align: center;
    }
    .signal-normal {
        background: #10b981;
        color: white;
        padding: 0.5rem;
        border-radius: 10px;
        text-align: center;
    }
    .signal-low {
        background: #6b7280;
        color: white;
        padding: 0.5rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ชื่อหน้า
st.markdown("""
<div style="display: flex; align-items: center; margin-bottom: 1rem;">
    <h1>⚡ วิเคราะห์หุ้นเล่นสั้น</h1>
    <span class="version-badge">Yahoo Finance</span>
</div>
""", unsafe_allow_html=True)

# แสดงสถานะ
if api_ready:
    st.success("✅ เชื่อมต่อ Yahoo Finance สำเร็จ")
else:
    st.error("❌ ไม่สามารถเชื่อมต่อ")
    st.stop()

st.markdown("---")

# Sidebar
with st.sidebar:
    st.subheader("🔍 เลือกหุ้น")
    symbol = st.text_input("รหัสหุ้น", "ADVANC").upper()
    
    st.markdown("---")
    auto_refresh = st.checkbox("Auto Refresh ทุก 30 วิ", value=False)
    
    st.markdown("---")
    if st.button("🔄 ดึงข้อมูลใหม่", use_container_width=True):
        st.rerun()

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"📊 ข้อมูล {symbol}")
    
    # ดึงข้อมูล
    quote = api.get_quote(symbol)
    
    if quote['success']:
        # แสดง metrics
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        
        with mcol1:
            st.metric("ราคาล่าสุด", f"฿{quote['price']:.2f}")
        with mcol2:
            st.metric("เปลี่ยนแปลง", f"{quote['change']:+.2f}")
        with mcol3:
            st.metric("% เปลี่ยนแปลง", f"{quote['change_percent']:+.2f}%")
        with mcol4:
            st.metric("วอลุ่ม", f"{quote['volume']:,}")
        
        # วิเคราะห์วอลุ่ม
        st.markdown("---")
        st.subheader("🎯 วิเคราะห์วอลุ่ม")
        
        analysis = api.analyze_volume(symbol)
        
        if analysis['success']:
            # แสดงผลตามระดับ
            level_class = {
                'สูง': 'signal-high',
                'กลาง': 'signal-medium',
                'ปกติ': 'signal-normal',
                'ต่ำ': 'signal-low'
            }.get(analysis['level'], 'signal-normal')
            
            st.markdown(f"""
            <div class="{level_class}">
                <h2>{analysis['signal']}</h2>
                <h3>วอลุ่ม: {analysis['volume']:,}</h3>
                <p>{analysis['action']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # ข้อมูลเพิ่มเติม
        st.markdown("---")
        st.subheader("📈 ข้อมูลเพิ่มเติม")
        
        icol1, icol2, icol3 = st.columns(3)
        with icol1:
            st.markdown(f"สูงสุดวัน: ฿{quote['high']:.2f}")
        with icol2:
            st.markdown(f"ต่ำสุดวัน: ฿{quote['low']:.2f}")
        with icol3:
            st.markdown(f"เปิด: ฿{quote['open']:.2f}")
        
    elif 'wait' in quote:
        st.warning(f"⏳ {quote['error']}")
        if auto_refresh:
            time.sleep(1)
            st.rerun()
    else:
        st.error(f"❌ {quote['error']}")

with col2:
    st.subheader("🎯 คำแนะนำ")
    
    st.markdown("""
    ### หลักการดูวอลุ่ม
    - **🔴 วอลุ่มสูงมาก** (>10M): ระวังเจ้ามือ
    - **🟡 วอลุ่มปานกลาง** (5-10M): จับตาดู
    - **🟢 วอลุ่มปกติ** (1-5M): ปกติ
    - **⚪ วอลุ่มเบาบาง** (<1M): เงียบ
    
    ### กลยุทธ์
    1. วอลุ่มสูง + ราคาขึ้น = แรงซื้อ
    2. วอลุ่มสูง + ราคาลง = แรงขาย
    3. วอลุ่มสูง + ราคานิ่ง = สะสม
    """)
    
    st.markdown("---")
    st.markdown(f"อัปเดต: {datetime.now().strftime('%H:%M:%S')}")

# Auto refresh
if auto_refresh and quote.get('success'):
    time.sleep(30)
    st.rerun()

st.markdown("---")
st.caption(f"ข้อมูลจาก Yahoo Finance | อัปเดตล่าสุด: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
