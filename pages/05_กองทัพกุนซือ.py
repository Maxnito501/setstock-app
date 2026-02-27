"""
หน้า 5: กองทัพกุนซือ
แสดงภาพการ์ตูนกุนซือทั้ง 4 ที่คอยสนับสนุน
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import base64
from PIL import Image
import io

# กำหนดค่าเพจ
st.set_page_config(
    page_title="กองทัพกุนซือ",
    page_icon="🎯",
    layout="wide"
)

# CSS เพื่อทำให้เท่
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;700&display=swap');
    
    * {
        font-family: 'Kanit', sans-serif;
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .sub-title {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .guru-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        transition: transform 0.3s;
        height: 100%;
    }
    
    .guru-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    }
    
    .guru-name {
        font-size: 2rem;
        font-weight: 700;
        margin: 1rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .guru-title {
        font-size: 1rem;
        opacity: 0.9;
        margin-bottom: 1rem;
    }
    
    .guru-quote {
        font-size: 1.1rem;
        font-style: italic;
        border-top: 1px solid rgba(255,255,255,0.3);
        padding-top: 1rem;
        margin-top: 1rem;
    }
    
    .master-section {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 30px;
        padding: 3rem;
        color: white;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
    }
    
    .master-name {
        font-size: 3.5rem;
        font-weight: 700;
        margin: 1rem 0;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
    }
    
    .master-level {
        font-size: 1.5rem;
        background: rgba(255,255,255,0.2);
        display: inline-block;
        padding: 0.5rem 2rem;
        border-radius: 50px;
        margin: 1rem 0;
    }
    
    .stats-box {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        color: #333;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .floating {  
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
        100% { transform: translateY(0px); }
    }
    
    .badge {
        background: gold;
        color: #333;
        padding: 0.3rem 1rem;
        border-radius: 50px;
        font-weight: 700;
        display: inline-block;
        margin: 0.5rem;
    }
    
    .power-bar {
        background: rgba(255,255,255,0.2);
        border-radius: 10px;
        height: 10px;
        margin: 1rem 0;
    }
    
    .power-fill {
        background: gold;
        border-radius: 10px;
        height: 10px;
        width: 95%;
    }
</style>
""", unsafe_allow_html=True)

# ส่วนหัว
st.markdown('<p class="hero-title">🎯 กองทัพกุนซือระดับโลก</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">4 จอมยุทธ์ ผู้อยู่เบื้องหลังความสำเร็จของคุณ</p>', unsafe_allow_html=True)

# ส่วนของอาจารย์ใหญ่ (คุณ)
st.markdown("""
<div class="master-section floating">
    <div style="font-size: 5rem;">👑</div>
    <div class="master-name">MAXNITO501</div>
    <div class="master-level">จอมยุทธ์ผู้พิชิตตลาด</div>
    <div style="display: flex; justify-content: center; gap: 1rem; margin: 2rem 0;">
        <span class="badge">⚔️ เทพยุทธ์ 99</span>
        <span class="badge">🛡️ กันชน 99</span>
        <span class="badge">💰 รวย 99</span>
    </div>
    <div style="font-size: 1.2rem; max-width: 600px; margin: 0 auto;">
        "ด้วยพลังของกุนซือทั้งสี่ ข้าจะพิชิตตลาดหุ้นให้จงได้"
    </div>
</div>
""", unsafe_allow_html=True)

# แสดงกุนซือทั้ง 4
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="guru-card">
        <div style="font-size: 4rem;">🎯</div>
        <div class="guru-name">ขงเบ้ง</div>
        <div class="guru-title">จอมยุทธ์วางแผน</div>
        <div class="power-bar">
            <div class="power-fill" style="width: 98%;"></div>
        </div>
        <div>อ่านขาด 98%</div>
        <div class="guru-quote">
            "กลยุทธ์ดี มีชัยไปกว่าครึ่ง"
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="guru-card">
        <div style="font-size: 4rem;">🐂</div>
        <div class="guru-name">บัฟเฟต์</div>
        <div class="guru-title">เทพเจ้าแห่งคุณค่า</div>
        <div class="power-bar">
            <div class="power-fill" style="width: 99%;"></div>
        </div>
        <div>แม่นยำ 99%</div>
        <div class="guru-quote">
            "ซื้อถูกคือกำไรครึ่งหนึ่ง"
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="guru-card">
        <div style="font-size: 4rem;">💻</div>
        <div class="guru-name">บิล เกตส์</div>
        <div class="guru-title">จอมเขียนโค้ด</div>
        <div class="power-bar">
            <div class="power-fill" style="width: 100%;"></div>
        </div>
        <div>โค้ดเทพ 100%</div>
        <div class="guru-quote">
            "AI จะทำให้คุณเหนือมนุษย์"
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="guru-card">
        <div style="font-size: 4rem;">🚀</div>
        <div class="guru-name">อีลอน</div>
        <div class="guru-title">บ้าพลังนวัตกรรม</div>
        <div class="power-bar">
            <div class="power-fill" style="width: 97%;"></div>
        </div>
        <div>ล้ำยุค 97%</div>
        <div class="guru-quote">
            "เทรดให้เร็ว เหมือนจรวด"
        </div>
    </div>
    """, unsafe_allow_html=True)

# สถิติพลังรวม
st.markdown("---")
st.markdown("## 📊 พลังรวมกองทัพ")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="stats-box">
        <div style="font-size: 2rem;">⚔️</div>
        <div style="font-size: 1.5rem; font-weight: 700;">98.5%</div>
        <div>พลังโจมตี</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stats-box">
        <div style="font-size: 2rem;">🛡️</div>
        <div style="font-size: 1.5rem; font-weight: 700;">99.2%</div>
        <div>พลังป้องกัน</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stats-box">
        <div style="font-size: 2rem;">📈</div>
        <div style="font-size: 1.5rem; font-weight: 700;">∞</div>
        <div>พลังทำกำไร</div>
    </div>
    """, unsafe_allow_html=True)

# เป้าหมาย
st.markdown("---")
st.markdown("## 🎯 ภารกิจต่อไป")

missions = [
    "⚔️ สร้างระบบตามรอยรายใหญ่",
    "📊 พัฒนา AI พยากรณ์แนวโน้ม",
    "🤖 เชื่อมต่อเทรดอัตโนมัติ",
    "💰 สร้างกองทุนพันล้าน"
]

for mission in missions:
    st.markdown(f"""
    <div style="background: #f0f2f6; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
        {mission}
    </div>
    """, unsafe_allow_html=True)

# คำคมปิดท้าย
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); border-radius: 20px;">
    <div style="font-size: 3rem; margin-bottom: 1rem;">💪</div>
    <div style="font-size: 1.5rem; font-weight: 300;">
        "ด้วยกุนซือระดับโลก ไม่มีตลาดไหนที่พิชิตไม่ได้"
    </div>
    <div style="margin-top: 1rem; color: #666;">
        - Maxnito501 จอมยุทธ์ผู้ยิ่งใหญ่ -
    </div>
</div>
""", unsafe_allow_html=True)

st.caption(f"กองทัพพร้อมรบ ณ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")