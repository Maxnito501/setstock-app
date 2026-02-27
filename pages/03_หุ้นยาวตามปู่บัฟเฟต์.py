"""
หน้า 3: วิเคราะห์หุ้นยาวตามแนวทาง Warren Buffett
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import sys
import os
from datetime import datetime

# เพิ่ม path เพื่อให้ import จาก utils ได้
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# ลอง import utils (ถ้ามี)
try:
    from utils.fundamental_analysis import FundamentalAnalyzer
    analyzer = FundamentalAnalyzer()
    utils_ready = True
except:
    utils_ready = False
    st.warning("⚠️ กำลังใช้โหมดข้อมูลตัวอย่าง (ไม่ได้เชื่อมต่อ utils)")

# กำหนดค่าเพจ
st.set_page_config(
    page_title="หุ้นยาวตาม Buffett",
    page_icon="🐂",
    layout="wide"
)

# ชื่อหน้า
st.title("🐂 วิเคราะห์หุ้นยาว แบบ Warren Buffett")
st.markdown("---")

# ข้อมูลตัวอย่างหุ้นไทย
thai_stocks = {
    'ADVANC': {
        'name': 'Advanced Info Service',
        'sector': 'เทคโนโลยี',
        'price': 248.00,
        'roe': 28.5,
        'pe': 19.5,
        'de': 0.85,
        'profit_margin': 18.5,
        'eps': 12.8,
        'eps_growth': 12.5,
        'book_value': 45.2,
        'dividend': 3.2,
        'market_share': 45,
        'brand_score': 9
    },
    'PTT': {
        'name': 'PTT Public Company',
        'sector': 'พลังงาน',
        'price': 35.75,
        'roe': 12.3,
        'pe': 8.2,
        'de': 0.62,
        'profit_margin': 8.2,
        'eps': 4.35,
        'eps_growth': 8.2,
        'book_value': 28.5,
        'dividend': 4.5,
        'market_share': 35,
        'brand_score': 8
    },
    'CPALL': {
        'name': 'CP All',
        'sector': 'ค้าปลีก',
        'price': 62.50,
        'roe': 18.7,
        'pe': 25.3,
        'de': 1.82,
        'profit_margin': 4.5,
        'eps': 2.85,
        'eps_growth': 15.2,
        'book_value': 12.8,
        'dividend': 2.1,
        'market_share': 70,
        'brand_score': 9
    },
    'SCB': {
        'name': 'Siam Commercial Bank',
        'sector': 'การเงิน',
        'price': 112.00,
        'roe': 9.2,
        'pe': 7.8,
        'de': 1.12,
        'profit_margin': 35.2,
        'eps': 14.2,
        'eps_growth': 5.8,
        'book_value': 185.5,
        'dividend': 5.2,
        'market_share': 18,
        'brand_score': 8
    },
    'KBANK': {
        'name': 'Kasikornbank',
        'sector': 'การเงิน',
        'price': 138.50,
        'roe': 10.1,
        'pe': 8.5,
        'de': 1.08,
        'profit_margin': 32.8,
        'eps': 16.8,
        'eps_growth': 6.5,
        'book_value': 195.2,
        'dividend': 4.8,
        'market_share': 17,
        'brand_score': 8
    },
    'BDMS': {
        'name': 'Bangkok Dusit Medical',
        'sector': 'การแพทย์',
        'price': 28.25,
        'roe': 15.8,
        'pe': 32.1,
        'de': 0.45,
        'profit_margin': 12.5,
        'eps': 0.88,
        'eps_growth': 10.5,
        'book_value': 5.2,
        'dividend': 1.8,
        'market_share': 25,
        'brand_score': 8
    }
}

# Sidebar สำหรับเลือกหุ้นและตั้งค่า
with st.sidebar:
    st.subheader("🔍 เลือกหุ้นที่ต้องการวิเคราะห์")
    
    # เลือกหุ้น
    selected_symbol = st.selectbox(
        "รหัสหุ้น",
        list(thai_stocks.keys()),
        index=0
    )
    
    st.markdown("---")
    st.subheader("⚙️ เกณฑ์การคัดเลือก")
    
    # ตั้งค่าเกณฑ์ต่างๆ
    min_roe = st.slider("ROE ขั้นต่ำ (%)", 0, 30, 15)
    max_pe = st.slider("P/E สูงสุด", 0, 50, 20)
    max_de = st.slider("D/E สูงสุด", 0.0, 3.0, 1.0, 0.1)
    min_margin = st.slider("กำไรขั้นต่ำ (%)", 0, 50, 10)
    
    st.markdown("---")
    st.caption("ที่มา: ข้อมูลตัวอย่างเพื่อการทดสอบ")

# แสดงข้อมูลหุ้นที่เลือก
stock = thai_stocks[selected_symbol]

st.subheader(f"📋 ข้อมูลพื้นฐาน {selected_symbol} - {stock['name']}")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("ราคาปัจจุบัน", f"฿{stock['price']:.2f}")
with col2:
    st.metric("P/E Ratio", f"{stock['pe']:.1f}")
with col3:
    st.metric("ROE", f"{stock['roe']:.1f}%")
with col4:
    st.metric("Dividend Yield", f"{stock['dividend']:.1f}%")

# วิเคราะห์ตามหลัก Buffett
st.markdown("---")
st.subheader("📊 วิเคราะห์ตามหลักการของ Warren Buffett")

# เตรียมข้อมูลสำหรับวิเคราะห์
stock_data = {
    'roe': stock['roe'],
    'pe': stock['pe'],
    'debt_to_equity': stock['de'],
    'profit_margin': stock['profit_margin'],
    'eps_growth': stock['eps_growth'],
    'eps': stock['eps'],
    'book_value': stock['book_value'],
    'growth_rate': stock['eps_growth'],
    'brand_strength': stock['brand_score'],
    'market_share': stock['market_share'],
    'innovation_score': 7,
    'switching_cost': 7
}

if utils_ready:
    # ใช้ utils จริง
    buffett_score = analyzer.calculate_buffett_score(stock_data)
    intrinsic_value = analyzer.calculate_intrinsic_value_dcf(stock_data)
    margin = analyzer.calculate_margin_of_safety(stock['price'], intrinsic_value)
    graham = analyzer.graham_number(stock['eps'], stock['book_value'])
    moat = analyzer.analyze_moat(stock_data)
else:
    # ใช้ข้อมูลตัวอย่าง
    buffett_score = {
        'total_score': 75,
        'level': 'ดี',
        'recommendation': 'ถือ/สะสม',
        'details': [
            {'criteria': 'ROE', 'status': 'ดี', 'score': 20},
            {'criteria': 'P/E', 'status': 'เหมาะสม', 'score': 10},
            {'criteria': 'D/E', 'status': 'ปลอดภัย', 'score': 15},
            {'criteria': 'EPS Growth', 'status': 'ดี', 'score': 10},
            {'criteria': 'Profit Margin', 'status': 'ดี', 'score': 7}
        ]
    }
    intrinsic_value = stock['price'] * 1.2
    margin = 16.7
    graham = stock['price'] * 0.9
    moat = {
        'moat_score': 75,
        'moat_level': 'แข็งแกร่ง',
        'factors': [
            {'factor': 'Brand', 'score': 20},
            {'factor': 'Market Share', 'score': 20},
            {'factor': 'Profit Margin', 'score': 15},
            {'factor': 'Innovation', 'score': 10},
            {'factor': 'Switching Cost', 'score': 10}
        ]
    }

# แสดงคะแนน Buffett
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏆 Buffett Score")
    
    # สร้าง gauge chart
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = buffett_score['total_score'],
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"คะแนน {buffett_score['level']}"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 40], 'color': "red"},
                {'range': [40, 60], 'color': "orange"},
                {'range': [60, 80], 'color': "yellow"},
                {'range': [80, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 60
            }
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"**คำแนะนำ:** {buffett_score['recommendation']}")

with col2:
    st.markdown("### 💰 มูลค่าที่แท้จริง")
    
    # สร้างกราฟเปรียบเทียบราคา
    comparison = pd.DataFrame({
        'ประเภท': ['ราคาตลาด', 'มูลค่า DCF', 'Graham Number'],
        'มูลค่า': [stock['price'], intrinsic_value, graham]
    })
    
    fig = px.bar(comparison, x='ประเภท', y='มูลค่า', 
                 color='ประเภท',
                 color_discrete_map={
                     'ราคาตลาด': 'blue',
                     'มูลค่า DCF': 'green',
                     'Graham Number': 'orange'
                 })
    fig.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"**Margin of Safety:** {margin:.1f}%")
    if margin > 30:
        st.success("✅ มีส่วนเผื่อความปลอดภัยสูง")
    elif margin > 15:
        st.info("📊 ส่วนเผื่อความปลอดภัยปานกลาง")
    else:
        st.warning("⚠️ ส่วนเผื่อความปลอดภัยต่ำ")

# รายละเอียดคะแนน
st.markdown("---")
st.subheader("📈 รายละเอียดการให้คะแนน")

# สร้างตารางแสดงคะแนนแต่ละด้าน
details_df = pd.DataFrame(buffett_score['details'])
st.dataframe(details_df, use_container_width=True)

# วิเคราะห์ Economic Moat
st.markdown("---")
st.subheader("🛡️ วิเคราะห์ Economic Moat (ความได้เปรียบในการแข่งขัน)")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"### คะแนน Moat: {moat['moat_score']}/100")
    st.markdown(f"**ระดับ:** {moat['moat_level']}")
    
    # สร้างกราฟแสดงคะแนนแต่ละปัจจัย
    moat_df = pd.DataFrame(moat['factors'])
    fig = px.bar(moat_df, x='factor', y='score', 
                 color='score',
                 color_continuous_scale='viridis')
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### คำอธิบาย")
    st.markdown("""
    **Economic Moat** คือความได้เปรียบทางการแข่งขันที่ยั่งยืน
    
    **5 ปัจจัยหลัก:**
    1. **Brand** - ความแข็งแกร่งของแบรนด์
    2. **Market Share** - ส่วนแบ่งการตลาด
    3. **Profit Margin** - อัตรากำไรที่สูง
    4. **Innovation** - ความสามารถในการสร้างนวัตกรรม
    5. **Switching Cost** - ต้นทุนในการเปลี่ยนผู้ให้บริการ
    """)

# เปรียบเทียบกับเกณฑ์ของ Buffett
st.markdown("---")
st.subheader("✅ ตรวจสอบตามเกณฑ์ของ Buffett")

# สร้าง checklist
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### เกณฑ์ด้านคุณภาพ")
    
    # ตรวจสอบ ROE
    if stock['roe'] >= 15:
        st.success("✅ ROE > 15% (ผ่าน)")
    else:
        st.error("❌ ROE < 15% (ไม่ผ่าน)")
    
    # ตรวจสอบ D/E
    if stock['de'] <= 1.0:
        st.success("✅ D/E <= 1 (ผ่าน)")
    else:
        st.error("❌ D/E > 1 (ไม่ผ่าน)")
    
    # ตรวจสอบ Profit Margin
    if stock['profit_margin'] >= 15:
        st.success("✅ Profit Margin > 15% (ผ่าน)")
    elif stock['profit_margin'] >= 10:
        st.info("📊 Profit Margin ปานกลาง (10-15%)")
    else:
        st.error("❌ Profit Margin < 10% (ไม่ผ่าน)")

with col2:
    st.markdown("#### เกณฑ์ด้านราคา")
    
    # ตรวจสอบ P/E
    if stock['pe'] <= 15:
        st.success("✅ P/E <= 15 (ถูก)")
    elif stock['pe'] <= 20:
        st.info("📊 P/E ปานกลาง (15-20)")
    else:
        st.error("❌ P/E > 20 (แพง)")
    
    # ตรวจสอบ PEG
    peg = stock['pe'] / stock['eps_growth'] if stock['eps_growth'] > 0 else 999
    if peg <= 1:
        st.success(f"✅ PEG = {peg:.2f} <= 1 (ผ่าน)")
    else:
        st.error(f"❌ PEG = {peg:.2f} > 1 (ไม่ผ่าน)")
    
    # ตรวจสอบ Margin of Safety
    if margin >= 30:
        st.success("✅ Margin of Safety > 30% (ดีมาก)")
    elif margin >= 15:
        st.info("📊 Margin of Safety ปานกลาง")
    else:
        st.error("❌ Margin of Safety < 15% (น้อย)")

# สรุป
st.markdown("---")
st.subheader("📝 สรุปการลงทุน")

if buffett_score['total_score'] >= 80:
    st.success("""
    ### 🎯 เหมาะสำหรับการลงทุนระยะยาว
    - ผ่านเกณฑ์ของ Buffett ทุกด้าน
    - มีความได้เปรียบทางการแข่งขันชัดเจน
    - ราคายังเหมาะสมกับมูลค่าพื้นฐาน
    """)
elif buffett_score['total_score'] >= 60:
    st.info("""
    ### 📊 พอใช้ แต่ต้องติดตาม
    - ผ่านเกณฑ์พื้นฐาน แต่ยังมีจุดที่ต้องปรับปรุง
    - อาจรอจังหวะราคาที่เหมาะสมกว่านี้
    """)
else:
    st.warning("""
    ### ⚠️ ยังไม่ผ่านเกณฑ์
    - ควรศึกษาข้อมูลเพิ่มเติม
    - หรือมองหาหุ้นตัวอื่นที่เหมาะสมกว่า
    """)

# เปรียบเทียบกับหุ้นตัวอื่น
st.markdown("---")
st.subheader("📊 เปรียบเทียบกับหุ้นในกลุ่มเดียวกัน")

# สร้าง DataFrame สำหรับเปรียบเทียบ
compare_data = []
for sym, data in thai_stocks.items():
    if data['sector'] == stock['sector']:
        compare_data.append({
            'หุ้น': sym,
            'ราคา': data['price'],
            'P/E': data['pe'],
            'ROE': data['roe'],
            'D/E': data['de'],
            'กำไร': data['profit_margin']
        })

if compare_data:
    compare_df = pd.DataFrame(compare_data)
    st.dataframe(compare_df, use_container_width=True)

# ท้ายหน้า
st.markdown("---")
st.caption(f"วิเคราะห์เมื่อ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("หมายเหตุ: ข้อมูลเป็นตัวอย่างเพื่อการทดสอบเท่านั้น ไม่ใช่คำแนะนำในการลงทุน")