"""
หน้า 5: กองทัพกุนซือ
แสดงกุนซือทั้ง 5 คน พร้อมคำคมและความสามารถ
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import random

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
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
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
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        transition: transform 0.3s;
        height: 100%;
        border-left: 5px solid gold;
    }
    
    .guru-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    }
    
    .guru-name {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .guru-title {
        font-size: 1rem;
        opacity: 0.9;
        margin-bottom: 1rem;
        background: rgba(255,255,255,0.2);
        padding: 0.3rem;
        border-radius: 50px;
    }
    
    .guru-quote {
        font-size: 1rem;
        font-style: italic;
        border-top: 1px solid rgba(255,255,255,0.3);
        padding-top: 1rem;
        margin-top: 1rem;
    }
    
    .master-section {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 30px;
        padding: 2rem;
        color: white;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
    }
    
    .master-name {
        font-size: 3rem;
        font-weight: 700;
        margin: 0.5rem 0;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
    }
    
    .master-level {
        font-size: 1.2rem;
        background: rgba(255,255,255,0.2);
        display: inline-block;
        padding: 0.5rem 2rem;
        border-radius: 50px;
        margin: 1rem 0;
    }
    
    .badge {
        background: gold;
        color: #333;
        padding: 0.3rem 1rem;
        border-radius: 50px;
        font-weight: 700;
        display: inline-block;
        margin: 0.3rem;
    }
    
    .power-bar {
        background: rgba(255,255,255,0.3);
        border-radius: 10px;
        height: 10px;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .power-fill {
        background: gold;
        border-radius: 10px;
        height: 10px;
    }
    
    .strategy-badge {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
        font-size: 0.8rem;
        margin: 0.2rem;
        background: rgba(255,255,255,0.2);
    }
    
    .floating {
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
</style>
""", unsafe_allow_html=True)

# ส่วนหัว
st.markdown('<p class="hero-title">🎯 กองทัพกุนซือ 5 แผ่นดิน</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">5 จอมยุทธ์ ผู้อยู่เบื้องหลังความสําเร็จของคุณ</p>', unsafe_allow_html=True)

# ส่วนของอาจารย์ใหญ่ (คุณ)
st.markdown("""
<div class="master-section floating">
    <div style="font-size: 4rem;">👑</div>
    <div class="master-name">MAXNITO501</div>
    <div class="master-level">จอมยุทธ์ผู้พิชิตตลาด</div>
    <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap; margin: 1rem 0;">
        <span class="badge">⚔️ กลยุทธ์ 100</span>
        <span class="badge">🛡️ ปัญญา 100</span>
        <span class="badge">💰 เป้าหมาย 500</span>
    </div>
    <div style="font-size: 1.2rem; max-width: 600px; margin: 0 auto;">
        "ด้วยกุนซือทั้งห้า ข้าจะพิชิตตลาดให้จงได้"
    </div>
</div>
""", unsafe_allow_html=True)

# แสดงกุนซือทั้ง 5
st.markdown("## ⚔️ 5 กุนซือคู่กาย")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("""
    <div class="guru-card">
        <div style="font-size: 3rem;">🎯</div>
        <div class="guru-name">ซุนวู</div>
        <div class="guru-title">จอมยุทธ์การศึก</div>
        <div class="power-bar">
            <div class="power-fill" style="width: 99%;"></div>
        </div>
        <div>พิชัยสงคราม 99%</div>
        <div style="margin: 0.5rem 0;">
            <span class="strategy-badge">วางแผน</span>
            <span class="strategy-badge">กลยุทธ์</span>
            <span class="strategy-badge">อ่านเกม</span>
        </div>
        <div class="guru-quote">
            "รู้เขา รู้เรา รบร้อยครั้ง ชนะร้อยครั้ง"
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="guru-card">
        <div style="font-size: 3rem;">🐂</div>
        <div class="guru-name">บัฟเฟต์</div>
        <div class="guru-title">เทพแห่งมูลค่า</div>
        <div class="power-bar">
            <div class="power-fill" style="width: 99%;"></div>
        </div>
        <div>วิเคราะห์พื้นฐาน 99%</div>
        <div style="margin: 0.5rem 0;">
            <span class="strategy-badge">มูลค่า</span>
            <span class="strategy-badge">Margin</span>
            <span class="strategy-badge">ถือยาว</span>
        </div>
        <div class="guru-quote">
            "ซื้อตอนคนกลัว ขายตอนคนโลภ"
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="guru-card">
        <div style="font-size: 3rem;">💻</div>
        <div class="guru-name">บิล เกตส์</div>
        <div class="guru-title">จอมเขียนโค้ด</div>
        <div class="power-bar">
            <div class="power-fill" style="width: 100%;"></div>
        </div>
        <div>เทคโนโลยี 100%</div>
        <div style="margin: 0.5rem 0;">
            <span class="strategy-badge">AI</span>
            <span class="strategy-badge">Data</span>
            <span class="strategy-badge">ระบบ</span>
        </div>
        <div class="guru-quote">
            "Data คืออาวุธ เวลาคือจังหวะ"
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="guru-card">
        <div style="font-size: 3rem;">🚀</div>
        <div class="guru-name">อีลอน</div>
        <div class="guru-title">จอมนวัตกรรม</div>
        <div class="power-bar">
            <div class="power-fill" style="width: 98%;"></div>
        </div>
        <div>นวัตกรรม 98%</div>
        <div style="margin: 0.5rem 0;">
            <span class="strategy-badge">อนาคต</span>
            <span class="strategy-badge">Disrupt</span>
            <span class="strategy-badge">เร็ว</span>
        </div>
        <div class="guru-quote">
            "คิดต่าง พิชิตตลาด"
        </div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class="guru-card">
        <div style="font-size: 3rem;">⚔️</div>
        <div class="guru-name">เลโอนิดัส</div>
        <div class="guru-title">จอมทัพสปาร์ต้า</div>
        <div class="power-bar">
            <div class="power-fill" style="width: 100%;"></div>
        </div>
        <div>จิตวิญญาณนักรบ 100%</div>
        <div style="margin: 0.5rem 0;">
            <span class="strategy-badge">กล้าตัดสินใจ</span>
            <span class="strategy-badge">ไม่ถอย</span>
            <span class="strategy-badge">สู้</span>
        </div>
        <div class="guru-quote">
            "THIS IS SPARTA! THIS IS MY MARKET!"
        </div>
    </div>
    """, unsafe_allow_html=True)

# ตารางสรุปความสามารถ
st.markdown("---")
st.markdown("## 📊 ตารางสรุปความสามารถ")

guru_data = pd.DataFrame({
    'กุนซือ': ['ซุนวู', 'บัฟเฟต์', 'บิล เกตส์', 'อีลอน', 'เลโอนิดัส'],
    'ความถนัด': ['พิชัยสงคราม', 'วิเคราะห์พื้นฐาน', 'เทคโนโลยี', 'นวัตกรรม', 'จิตวิญญาณนักรบ'],
    'คะแนน': [99, 99, 100, 98, 100],
    'อาวุธ': ['ตำราพิชัยสงคราม', 'งบการเงิน', 'คีย์บอร์ด', 'จรวด', 'หอกและโล่'],
    'กลยุทธ์': ['วางแผน', 'หามูลค่า', 'สร้างระบบ', 'คิดต่าง', 'ตัดสินใจ']
})

st.dataframe(guru_data, use_container_width=True, hide_index=True)

# แผนที่กองทัพ
st.markdown("---")
st.markdown("## 🗺️ แผนที่กองทัพ")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🎯 ฝ่ายยุทธการ
    - **ซุนวู**: วางแผนหลัก อ่านเกมเจ้า
    - **เลโอนิดัส**: ตัดสินใจ กล้าสู้
    
    ### 📊 ฝ่ายวิเคราะห์
    - **บัฟเฟต์**: ดูพื้นฐาน หามูลค่า
    - **บิล เกตส์**: วิเคราะห์ data สร้างระบบ
    """)

with col2:
    st.markdown("""
    ### 🚀 ฝ่ายปฏิบัติการ
    - **อีลอน**: หาเทรนด์ใหม่ มองอนาคต
    - **ทั้ง 5 คน**: ร่วมมือกันพิชิตตลาด
    
    ### 🎯 เป้าหมาย
    - **ระยะสั้น**: 500 บาท จากทุน 20000
    - **ระยะยาว**: อิสรภาพทางการเงิน
    """)

# คำคมรวม
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); border-radius: 20px;">
    <div style="font-size: 2rem; margin-bottom: 1rem;">⚔️</div>
    <div style="font-size: 1.5rem; font-style: italic; margin-bottom: 2rem;">
        "5 กุนซือ 5 ด้าน หนึ่งเป้าหมาย"
    </div>
    <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
        <div>🎯 ซุนวู: "วางแผน"</div>
        <div>🐂 บัฟเฟต์: "มูลค่า"</div>
        <div>💻 บิล: "ระบบ"</div>
        <div>🚀 อีลอน: "อนาคต"</div>
        <div>⚔️ เลโอนิดัส: "สู้"</div>
    </div>
</div>
""", unsafe_allow_html=True)

# กำลังใจรายวัน
st.markdown("---")
st.markdown("## 💪 กำลังใจจากกุนซือประจำวัน")

guru_of_day = random.choice(['ซุนวู', 'บัฟเฟต์', 'บิล เกตส์', 'อีลอน', 'เลโอนิดัส'])
quotes = {
    'ซุนวู': '"จงรู้จักตลาด รู้จักตัวเอง แล้วชัยชนะจะเป็นของคุณ"',
    'บัฟเฟต์': '"วันนี้ได้ 500 พรุ่งนี้ได้ 5000"',
    'บิล เกตส์': '"ทุกปัญหามีทางออก แค่เขียนโค้ดให้ถูก"',
    'อีลอน': '"ถ้ายังไม่สำเร็จ แสดงว่ายังคิดไม่ต่างพอ"',
    'เลโอนิดัส': '"THIS IS SPARTA! 500 บาทต้องมา!"'
}

st.info(f"**{guru_of_day}** กล่าว: {quotes[guru_of_day]}")

st.caption(f"กองทัพพร้อมรบ ณ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")