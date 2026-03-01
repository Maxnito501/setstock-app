"""
หน้า 6: นายพรานจับจังหวะ
รวม 5 กลยุทธ์ล่าเหยื่อในตลาดหุ้น
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os
import random

# เพิ่ม path เพื่อให้ import จาก utils ได้
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# กำหนดค่าเพจ
st.set_page_config(
    page_title="นายพรานจับจังหวะ",
    page_icon="🎯",
    layout="wide"
)

# CSS ตกแต่ง
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;700&display=swap');
    
    * {
        font-family: 'Kanit', sans-serif;
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .strategy-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid;
        transition: transform 0.3s;
    }
    
    .strategy-card:hover {
        transform: translateX(10px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .guru-tag {
        display: inline-block;
        padding: 0.3rem 1rem;
        border-radius: 50px;
        color: white;
        font-size: 0.9rem;
        margin-right: 0.5rem;
    }
    
    .signal-good {
        background: #10b981;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 50px;
        display: inline-block;
    }
    
    .signal-warning {
        background: #f59e0b;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 50px;
        display: inline-block;
    }
    
    .signal-danger {
        background: #ef4444;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 50px;
        display: inline-block;
    }
    
    .guru-quote {
        font-style: italic;
        color: #666;
        border-left: 3px solid #667eea;
        padding-left: 1rem;
        margin: 1rem 0;
    }
    
    .floating {
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    .stats-box {
        background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%);
        border-radius: 15px;
        padding: 1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ชื่อหน้า
st.markdown('<p class="main-title">🎯 นายพรานจับจังหวะ</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center;">5 กลยุทธ์ 5 กุนซือ หนึ่งเป้าหมาย... กําไร</p>', unsafe_allow_html=True)
st.markdown("---")

# ฟังก์ชันสร้างข้อมูลตัวอย่าง
def generate_sample_data():
    """สร้างข้อมูลตัวอย่าง 20 หุ้น"""
    stocks = ['ADVANC', 'PTT', 'CPALL', 'SCB', 'KBANK', 'BDMS', 'AOT', 'PTTEP', 
              'TRUE', 'JAS', 'BANPU', 'IRPC', 'SAWAD', 'BEM', 'CPN', 'IVL', 
              'BBL', 'KTB', 'TISCO', 'HMPRO']
    
    data = []
    for stock in stocks:
        # สุ่มข้อมูล
        trend_score = random.randint(30, 100)
        reversal_signals = random.randint(0, 5)
        shake_type = random.choice(['ปกติ', 'เขย่าขาลง', 'เขย่าขาขึ้น', 'แกว่งกรอบ'])
        whale_alert = random.choice(['ปกติ', 'ระวัง', 'อันตราย'])
        tired_score = random.randint(0, 100)
        
        data.append({
            'หุ้น': stock,
            'ราคา': round(random.uniform(10, 300), 2),
            'เทรนดี': trend_score,
            'กลับตัว': reversal_signals,
            'เจ้าเขย่า': shake_type,
            'เจ้าริน': whale_alert,
            'ยามเปลี้ย': tired_score,
            'ราคาเปลี่ยน %': round(random.uniform(-5, 5), 2),
            'Volume': random.randint(1, 100)
        })
    
    return pd.DataFrame(data)

# ดึงข้อมูล
df = generate_sample_data()

# แถบเลือกหุ้น
st.markdown("### 🔍 เลือกหุ้นที่ต้องการวิเคราะห์")

col1, col2 = st.columns([3, 1])
with col1:
    selected_stock = st.selectbox("", df['หุ้น'].tolist(), label_visibility="collapsed")
with col2:
    refresh = st.button("🔄 รีเฟรชข้อมูล", use_container_width=True)
    if refresh:
        st.rerun()

# ดึงข้อมูลหุ้นที่เลือก
stock_data = df[df['หุ้น'] == selected_stock].iloc[0]

# แสดงข้อมูลพื้นฐาน
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("ราคาปัจจุบัน", f"฿{stock_data['ราคา']:.2f}", 
              f"{stock_data['ราคาเปลี่ยน %']:+.2f}%")
with col2:
    st.metric("Volume (ล้าน)", f"{stock_data['Volume']}")
with col3:
    st.metric("เทรนดี", f"{stock_data['เทรนดี']}%")
with col4:
    st.metric("สัญญาณกลับตัว", f"{stock_data['กลับตัว']}/5")

st.markdown("---")

# 5 กลยุทธ์
st.markdown("## 🎯 5 กลยุทธ์นายพราน")

# สร้าง tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔥 เทรนดี", 
    "🎯 จังหวะกลับตัว", 
    "🐺 อ่านเกมเจ้า", 
    "💀 เจ้ารินเทขาย", 
    "🎣 รอซ้ำยามเปลี้ย",
    "📊 สรุปทั้งหมด"
])

# Tab 1: เทรนดี (ซุนวู)
with tab1:
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <span class="guru-tag" style="background: #667eea;">🎯 ซุนวู</span>
        <span style="margin-left: 1rem;">"รู้เขา รู้เรา รบร้อยครั้ง ชนะร้อยครั้ง"</span>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # กราฟเทรน
        fig = go.Figure()
        
        # สร้างข้อมูลเทรน
        days = 50
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        if stock_data['เทรนดี'] > 70:
            trend = 'ขาขึ้น'
            price = np.cumprod(1 + np.random.normal(0.005, 0.02, days)) * 100
            color = 'green'
        elif stock_data['เทรนดี'] > 40:
            trend = 'sideways'
            price = 100 + np.cumsum(np.random.normal(0, 2, days))
            color = 'orange'
        else:
            trend = 'ขาลง'
            price = np.cumprod(1 + np.random.normal(-0.005, 0.02, days)) * 100
            color = 'red'
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=price,
            mode='lines',
            name='ราคา',
            line=dict(color=color, width=3)
        ))
        
        # เพิ่ม MA
        ma20 = pd.Series(price).rolling(20).mean()
        ma50 = pd.Series(price).rolling(50).mean()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=ma20,
            mode='lines',
            name='MA20',
            line=dict(color='blue', width=1, dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=ma50,
            mode='lines',
            name='MA50',
            line=dict(color='red', width=1, dash='dash')
        ))
        
        fig.update_layout(
            title=f"{selected_stock} - แนวโน้ม {trend}",
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 คะแนนเทรนดี")
        
        score = stock_data['เทรนดี']
        if score >= 80:
            st.markdown(f"<h1 style='color: green; text-align: center;'>{score}%</h1>", unsafe_allow_html=True)
            st.markdown("🔥 <span class='signal-good'>เทรนดีมาก</span>", unsafe_allow_html=True)
        elif score >= 60:
            st.markdown(f"<h1 style='color: orange; text-align: center;'>{score}%</h1>", unsafe_allow_html=True)
            st.markdown("📊 <span class='signal-warning'>เทรนปานกลาง</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h1 style='color: red; text-align: center;'>{score}%</h1>", unsafe_allow_html=True)
            st.markdown("📉 <span class='signal-danger'>เทรนอ่อน</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🔍 วิเคราะห์")
        
        if score >= 80:
            st.markdown("✅ MA20 > MA50 > MA200")
            st.markdown("✅ ADX = 32 (เทรนแรง)")
            st.markdown("✅ Volume สูงกว่าค่าเฉลี่ย")
            st.markdown("""
            <div class="guru-quote">
                ซุนวู: "จงซื้อเมื่ออ่อนตัว รอจังหวะทะลุแนวต้าน"
            </div>
            """, unsafe_allow_html=True)
        elif score >= 60:
            st.markdown("📊 MA20 ≈ MA50")
            st.markdown("📊 ADX = 18 (เทรนอ่อน)")
            st.markdown("📊 Volume ปกติ")
            st.markdown("""
            <div class="guru-quote">
                ซุนวู: "รอให้ชัดเจนก่อน ค่อยค่อยเข้า"
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("❌ MA20 < MA50 < MA200")
            st.markdown("❌ ADX = 12 (ไม่มีเทรน)")
            st.markdown("❌ Volume ต่ำ")
            st.markdown("""
            <div class="guru-quote">
                ซุนวู: "ยังไม่ใช่จังหวะ รอต่อไป"
            </div>
            """, unsafe_allow_html=True)

# Tab 2: จังหวะกลับตัว (บัฟเฟต์ + บิล)
with tab2:
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <span class="guru-tag" style="background: #10b981;">🐂 บัฟเฟต์</span>
        <span class="guru-tag" style="background: #3b82f6;">💻 บิล เกตส์</span>
        <span style="margin-left: 1rem;">"ซื้อตอนคนกลัว ขายตอนคนโลภ"</span>
    </div>
    """, unsafe_allow_html=True)
    
    signals = stock_data['กลับตัว']
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🎯 สัญญาณกลับตัว")
        
        # สร้าง gauge chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = signals * 20,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "ความพร้อมกลับตัว"},
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
    
    with col2:
        st.markdown("### 🔍 สัญญาณที่พบ")
        
        signal_list = []
        if signals >= 1:
            signal_list.append("✅ ราคาดิ่ง 4-5 วันติด")
        if signals >= 2:
            signal_list.append("✅ RSI < 30 (Oversold)")
        if signals >= 3:
            signal_list.append("✅ Volume เริ่มเข้า 1.5 เท่า")
        if signals >= 4:
            signal_list.append("✅ Stochastic < 20")
        if signals >= 5:
            signal_list.append("✅ Bullish Divergence")
        
        for s in signal_list:
            st.markdown(s)
        
        for i in range(5 - len(signal_list)):
            st.markdown("⬜ กำลังรอสัญญาณ...")
    
    st.markdown("---")
    
    if signals >= 4:
        st.success("""
        ### 🎯 จังหวะช้อน!
        - RSI = 25.3 (Oversold)
        - Volume เพิ่ม 1.5 เท่า
        - ราคาดิ่ง 5 วันติด
        
        **กลยุทธ์:** ช้อนซื้อ 30% ของพอร์ต
        """)
    elif signals >= 3:
        st.warning("""
        ### 📊 เตรียมตัวช้อน
        - RSI ใกล้ Oversold
        - Volume เริ่มเข่า
        
        **กลยุทธ์:** รออีก 1-2 วัน
        """)
    else:
        st.info("""
        ### ⏳ ยังไม่ใช่จังหวะ
        - รอให้สัญญาณครบ 4 ข้อ
        
        **กลยุทธ์:** รอต่อไป
        """)

# Tab 3: อ่านเกมเจ้า (ซุนวู + เลโอนิดัส)
with tab3:
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <span class="guru-tag" style="background: #667eea;">🎯 ซุนวู</span>
        <span class="guru-tag" style="background: #dc2626;">⚔️ เลโอนิดัส</span>
        <span style="margin-left: 1rem;">"อ่านเกมเจ้าให้ออก อย่าตกเป็นเหยื่อ"</span>
    </div>
    """, unsafe_allow_html=True)
    
    shake = stock_data['เจ้าเขย่า']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🐺 รูปแบบการเขย่า")
        
        if shake == 'เขย่าขาลง':
            st.markdown("""
            <div style="background: #fee2e2; padding: 1rem; border-radius: 10px;">
                <h4 style="color: #dc2626;">⚠️ เขย่าขาลง</h4>
                <p>ราคาลงแรง แต่ Volume น้อย</p>
                <p><b>เจ้ากำลัง:</b> หลอกให้ขาย</p>
                <p><b>กลยุทธ์:</b> ถือของไว้!</p>
            </div>
            """, unsafe_allow_html=True)
        elif shake == 'เขย่าขาขึ้น':
            st.markdown("""
            <div style="background: #fef3c7; padding: 1rem; border-radius: 10px;">
                <h4 style="color: #f59e0b;">⚠️ เขย่าขาขึ้น</h4>
                <p>ราคาขึ้นแรง แต่ Volume น้อย</p>
                <p><b>เจ้ากำลัง:</b> หลอกให้ซื้อ</p>
                <p><b>กลยุทธ์:</b> อย่าเพิ่งซื้อ!</p>
            </div>
            """, unsafe_allow_html=True)
        elif shake == 'แกว่งกรอบ':
            st.markdown("""
            <div style="background: #e0f2fe; padding: 1rem; border-radius: 10px;">
                <h4 style="color: #0284c7;">🎢 แกว่งกรอบ</h4>
                <p>แกว่ง 5% ในกรอบแคบ</p>
                <p><b>เจ้ากำลัง:</b> ดึงเชือก เขย่าเม่า</p>
                <p><b>กลยุทธ์:</b> รอทะลุกรอบ</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #e5e7eb; padding: 1rem; border-radius: 10px;">
                <h4>✅ ปกติ</h4>
                <p>ไม่พบรูปแบบการเขย่า</p>
                <p><b>กลยุทธ์:</b> เทรดปกติ</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📊 กราฟปริศนา")
        
        # สร้างกราฟจำลองการเขย่า
        x = list(range(20))
        if shake == 'เขย่าขาลง':
            y = [100 - i*2 + random.uniform(-2, 2) for i in range(20)]
        elif shake == 'เขย่าขาขึ้น':
            y = [100 + i*2 + random.uniform(-2, 2) for i in range(20)]
        elif shake == 'แกว่งกรอบ':
            y = [100 + random.uniform(-5, 5) for i in range(20)]
        else:
            y = [100 + i*1 + random.uniform(-1, 1) for i in range(20)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='lines',
            line=dict(color='red' if 'เขย่า' in shake else 'green', width=2)
        ))
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("""
    <div class="guru-quote" style="font-size: 1.2rem;">
        เลโอนิดัส: "THIS IS SPARTA! ถ้าลงแรงแต่ Volume น้อย = หลอกขาย! ถือของไว้!"
    </div>
    """, unsafe_allow_html=True)

# Tab 4: เจ้ารินเทขาย (บิล เกตส์ + ซุนวู)
with tab4:
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <span class="guru-tag" style="background: #3b82f6;">💻 บิล เกตส์</span>
        <span class="guru-tag" style="background: #667eea;">🎯 ซุนวู</span>
        <span style="margin-left: 1rem;">"Data ไม่เคยโกหก หนีให้ทัน!"</span>
    </div>
    """, unsafe_allow_html=True)
    
    whale = stock_data['เจ้าริน']
    
    col1, col2 = st.columns(2)
    
    with col1:
        if whale == 'อันตราย':
            st.markdown("""
            <div style="background: #dc2626; color: white; padding: 2rem; border-radius: 20px; text-align: center;">
                <h1 style="font-size: 4rem;">💀</h1>
                <h2>WHALE DUMP ALERT!</h2>
                <h3>เจ้ารินเทขาย!</h3>
            </div>
            """, unsafe_allow_html=True)
        elif whale == 'ระวัง':
            st.markdown("""
            <div style="background: #f59e0b; color: white; padding: 2rem; border-radius: 20px; text-align: center;">
                <h1 style="font-size: 4rem;">⚠️</h1>
                <h2>PROCEED WITH CAUTION</h2>
                <h3>สัญญาณเตือน</h3>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #10b981; color: white; padding: 2rem; border-radius: 20px; text-align: center;">
                <h1 style="font-size: 4rem;">✅</h1>
                <h2>NORMAL</h2>
                <h3>ไม่มีสัญญาณอันตราย</h3>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🔍 สัญญาณที่ตรวจพบ")
        
        if whale == 'อันตราย':
            st.markdown("✅ Volume 2.3 เท่า ราคาไหลลง")
            st.markdown("✅ Offer ใหญ่ 2M หายไป")
            st.markdown("✅ ทะลุแนวรับสำคัญ 2%")
            st.markdown("✅ RSI ดิ่งจาก 70 สู่ 50")
            st.markdown("""
            <div class="guru-quote" style="margin-top: 1rem;">
                ซุนวู: "三十六计 - หนี!"
            </div>
            """, unsafe_allow_html=True)
        elif whale == 'ระวัง':
            st.markdown("✅ Volume สูง 1.5 เท่า")
            st.markdown("✅ ใกล้แนวรับ")
            st.markdown("⬜ ยังไม่ทะลุ")
            st.markdown("""
            <div class="guru-quote" style="margin-top: 1rem;">
                บิล เกตส์: "จับตาดูให้ดี อีกนิดเดียว"
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("✅ Volume ปกติ")
            st.markdown("✅ Bid/Offer ปกติ")
            st.markdown("✅ ราคาในกรอบ")
            st.markdown("""
            <div class="guru-quote" style="margin-top: 1rem;">
                บิล เกตส์: "System ปกติ เทรดได้"
            </div>
            """, unsafe_allow_html=True)

# Tab 5: รอซ้ำยามเปลี้ย (เลโอนิดัส + บัฟเฟต์)
with tab5:
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <span class="guru-tag" style="background: #dc2626;">⚔️ เลโอนิดัส</span>
        <span class="guru-tag" style="background: #10b981;">🐂 บัฟเฟต์</span>
        <span style="margin-left: 1rem;">"รอให้เหนื่อยแล้วค่อยซ้ำ!"</span>
    </div>
    """, unsafe_allow_html=True)
    
    tired_score = stock_data['ยามเปลี้ย']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 ความเหนื่อยของตลาด")
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = tired_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "ระดับความเหนื่อย"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 30], 'color': "green"},
                    {'range': [30, 60], 'color': "yellow"},
                    {'range': [60, 80], 'color': "orange"},
                    {'range': [80, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### ⏳ สถานะ")
        
        if tired_score >= 80:
            st.markdown("""
            <div style="background: #dc2626; color: white; padding: 1rem; border-radius: 10px;">
                <h3>🔥 ตลาดเหนื่อยมาก!</h3>
                <p>ความผันผวนสูง</p>
                <p>Volume 2.1x</p>
                <p>กรอบแคบ 4.5%</p>
                <p><b>รออีก 2-3 วัน ค่อยช้อน</b></p>
            </div>
            """, unsafe_allow_html=True)
        elif tired_score >= 60:
            st.markdown("""
            <div style="background: #f59e0b; color: white; padding: 1rem; border-radius: 10px;">
                <h3>⚡ เริ่มเหนื่อย</h3>
                <p>ความผันผวนปานกลาง</p>
                <p>Volume 1.5x</p>
                <p><b>รออีก 1-2 วัน</b></p>
            </div>
            """, unsafe_allow_html=True)
        elif tired_score >= 30:
            st.markdown("""
            <div style="background: #3b82f6; color: white; padding: 1rem; border-radius: 10px;">
                <h3>📊 ปกติ</h3>
                <p>ความผันผวนปกติ</p>
                <p>Volume ปกติ</p>
                <p><b>เทรดได้ตามปกติ</b></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #10b981; color: white; padding: 1rem; border-radius: 10px;">
                <h3>✅ สดชื่น</h3>
                <p>ตลาดปกติ</p>
                <p>Volume สม่ำเสมอ</p>
                <p><b>เทรดได้สบาย</b></p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    <div class="guru-quote" style="font-size: 1.2rem;">
        เลโอนิดัส: "รอให้เจ้าเหนื่อย แล้วเราค่อยซ้ำ! THIS IS SPARTA!"
    </div>
    """, unsafe_allow_html=True)

# Tab 6: สรุปทั้งหมด
with tab6:
    st.markdown("## 📊 สรุป 5 กลยุทธ์")

    # สร้างตารางสรุป
    summary_df = df.copy()
    
    # สร้าง column สรุป
    def get_summary(row):
        summaries = []
        
        if row['เทรนดี'] >= 80:
            summaries.append("🔥 เทรนดี")
        elif row['เทรนดี'] >= 60:
            summaries.append("📊 เทรนปานกลาง")
        
        if row['กลับตัว'] >= 4:
            summaries.append("🎯 พร้อมกลับตัว")
        elif row['กลับตัว'] >= 3:
            summaries.append("📈 เตรียมกลับตัว")
        
        if row['เจ้าเขย่า'] != 'ปกติ':
            summaries.append(f"🐺 {row['เจ้าเขย่า']}")
        
        if row['เจ้าริน'] == 'อันตราย':
            summaries.append("💀 ระวังเทขาย")
        elif row['เจ้าริน'] == 'ระวัง':
            summaries.append("⚠️ ใกล้เทขาย")
        
        if row['ยามเปลี้ย'] >= 80:
            summaries.append("🎣 รอซ้ำ")
        
        return ', '.join(summaries) if summaries else '✅ ปกติ'
    
    summary_df['สรุป'] = summary_df.apply(get_summary, axis=1)
    
    # แสดงตาราง
    st.dataframe(
        summary_df[['หุ้น', 'ราคา', 'ราคาเปลี่ยน %', 'Volume', 'สรุป']],
        use_container_width=True,
        height=500,
        column_config={
            'ราคา': st.column_config.NumberColumn('ราคา', format="฿%.2f"),
            'ราคาเปลี่ยน %': st.column_config.NumberColumn('เปลี่ยน %', format="%.2f%%"),
            'Volume': 'Volume (ล้าน)',
            'สรุป': 'สถานการณ์'
        }
    )
    
    # หุ้นที่น่าสนใจ
    st.markdown("---")
    st.markdown("## 🎯 หุ้นที่น่าสนใจวันนี้")
    
    interesting = summary_df[
        (summary_df['เทรนดี'] >= 80) |
        (summary_df['กลับตัว'] >= 4) |
        (summary_df['ยามเปลี้ย'] >= 80)
    ].head(5)
    
    for idx, row in interesting.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                st.markdown(f"### {row['หุ้น']}")
            with col2:
                st.markdown(f"**{row['สรุป']}**")
            with col3:
                if 'กลับตัว' in row['สรุป']:
                    st.markdown("🎯 <span class='signal-good'>ช้อน!</span>", unsafe_allow_html=True)
                elif 'เทรนดี' in row['สรุป']:
                    st.markdown("🔥 <span class='signal-good'>ตาม!</span>", unsafe_allow_html=True)
                elif 'รอซ้ำ' in row['สรุป']:
                    st.markdown("🎣 <span class='signal-warning'>รอ</span>", unsafe_allow_html=True)
                else:
                    st.markdown("📊 <span class='signal-warning'>เฝ้าดู</span>", unsafe_allow_html=True)
            st.markdown("---")

# คำคมปิดท้าย
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); border-radius: 20px;">
    <div style="font-size: 2rem; margin-bottom: 1rem;">🎯</div>
    <div style="font-size: 1.2rem; font-style: italic;">
        "5 กุนซือ 5 กลยุทธ์ หนึ่งเป้าหมาย... 500 บาทจากทุน 20000"
    </div>
    <div style="margin-top: 1rem; display: flex; justify-content: center; gap: 1rem;">
        <span>🎯 ซุนวู</span>
        <span>🐂 บัฟเฟต์</span>
        <span>💻 บิล</span>
        <span>🚀 อีลอน</span>
        <span>⚔️ เลโอนิดัส</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.caption(f"อัปเดตล่าสุด: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")