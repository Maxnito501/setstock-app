"""
Stock Analysis Application
Main entry point for the Streamlit app
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Page config - ต้องเป็นคำสั่งแรกของ Streamlit
st.set_page_config(
    page_title="Stock Analysis Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ตรวจสอบว่าโฟลเดอร์ต่างๆ มีครบหรือไม่
folders = ['pages', 'utils', 'data']
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"สร้างโฟลเดอร์ {folder} เรียบร้อย")

# Sidebar
with st.sidebar:
    st.title("📊 Stock Analysis Pro")
    st.markdown("---")
    
    # รับค่าหุ้นจากผู้ใช้
    symbol = st.text_input("รหัสหุ้น", "ADVANC").upper()
    
    # เลือกช่วงวันที่
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("วันที่เริ่มต้น", datetime.now() - timedelta(days=180))
    with col2:
        end_date = st.date_input("วันที่สิ้นสุด", datetime.now())
    
    st.markdown("---")
    st.markdown("### เกี่ยวกับโปรแกรม")
    st.info("โปรแกรมวิเคราะห์หุ้น สำหรับนักลงทุนไทย")

# Main content
st.title("📈 Stock Analysis Platform")
st.markdown("---")

# แสดงสถานะตลาดแบบจำลอง
st.subheader("📊 ภาพรวมตลาด")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("SET Index", "1,523.45", "+12.34 (0.82%)")

with col2:
    st.metric("ปริมาณการซื้อขาย", "45.2B", "")

with col3:
    st.metric("ต่างชาติสุทธิ", "ซื้อ 2.1B", "")

with col4:
    st.metric("Market Cap", "19.8T", "")

# แสดงเมนู
st.markdown("---")
st.subheader("📌 เลือกเมนูที่ต้องการ")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("### 📊 ภาพรวมตลาด")
    st.markdown("- หุ้นเด่น")
    st.markdown("- วอลุ่มสูง")
    st.markdown("- RSI พุ่ง")

with col2:
    st.markdown("### ⚡ หุ้นเล่นสั้น")
    st.markdown("- RSI, MACD")
    st.markdown("- Elliot Wave")
    st.markdown("- จุดเข้าซื้อ")

with col3:
    st.markdown("### 🐂 หุ้นยาว")
    st.markdown("- วิเคราะห์พื้นฐาน")
    st.markdown("- ROE, P/E")
    st.markdown("- Buffett Score")

with col4:
    st.markdown("### 📝 บันทึกขายหมู")
    st.markdown("- บันทึกการซื้อขาย")
    st.markdown("- ประวัติ")
    st.markdown("- สถิติ")

# แสดงสถานะ
st.markdown("---")
st.info("👈 คลิกที่เมนูด้านข้างเพื่อเลือกหน้าการวิเคราะห์")