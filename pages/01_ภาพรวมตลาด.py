"""
หน้าแรก: ภาพรวมตลาด
แสดงข้อมูลหุ้นเด่น วอลุ่มสูง RSI และการซื้อขายรายใหญ่
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# เพิ่ม path เพื่อให้ import จาก utils ได้
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# กำหนดค่าเพจ
st.set_page_config(
    page_title="ภาพรวมตลาด",
    page_icon="📊",
    layout="wide"
)

# ชื่อหน้า
st.title("📊 ภาพรวมตลาดหุ้น")
st.markdown("---")

# ฟังก์ชันสร้างข้อมูลตัวอย่าง
def get_market_data():
    """สร้างข้อมูลตัวอย่างสำหรับแสดง"""
    
    # ข้อมูลหุ้นเด่น
    leaders = pd.DataFrame({
        'Symbol': ['ADVANC', 'PTT', 'CPALL', 'SCB', 'KBANK', 'BDMS', 'AOT', 'PTTEP'],
        'Price': [248.00, 35.75, 62.50, 112.00, 138.50, 28.25, 72.50, 142.00],
        'Change': [4.50, 1.25, -0.75, 2.00, -1.50, 0.50, 1.25, 2.50],
        'Change %': [1.85, 3.62, -1.19, 1.82, -1.07, 1.80, 1.75, 1.79],
        'Volume': [15.2, 45.3, 22.1, 8.7, 12.4, 18.5, 25.3, 10.2],
        'RSI': [72, 68, 45, 65, 32, 58, 71, 69]
    })
    
    # ข้อมูลวอลุ่มสูง
    volumes = pd.DataFrame({
        'Symbol': ['PTT', 'TRUE', 'JAS', 'BANPU', 'ADVANC', 'CPALL', 'KBANK', 'SCB'],
        'Volume': [85.3, 92.5, 88.3, 75.1, 65.2, 42.1, 38.7, 32.4],
        'Price': [35.75, 5.25, 3.18, 8.45, 248.00, 62.50, 138.50, 112.00],
        'Change %': [3.62, -1.50, -0.80, -2.10, 1.85, -1.19, -1.07, 1.82]
    })
    
    # ข้อมูล RSI
    rsi_data = pd.DataFrame({
        'Symbol': ['ADVANC', 'PTTEP', 'BEM', 'AOT', 'TRUE', 'JAS', 'BANPU', 'IRPC'],
        'RSI': [78.5, 75.2, 73.8, 72.1, 25.3, 28.1, 29.5, 26.8],
        'Status': ['Overbought', 'Overbought', 'Overbought', 'Overbought', 
                   'Oversold', 'Oversold', 'Oversold', 'Oversold']
    })
    
    # ข้อมูลรายใหญ่
    big_trades = pd.DataFrame({
        'Symbol': ['ADVANC', 'PTT', 'CPALL', 'SCB', 'KBANK', 'BDMS'],
        'Foreign': [152, -85, 120, -45, 65, -25],
        'Institution': [75, 110, -35, 28, -52, 42],
        'Prop': [-45, 32, -18, 55, 23, -12],
        'Net': [182, 57, 67, 38, 36, 5]
    })
    
    return leaders, volumes, rsi_data, big_trades

# ดึงข้อมูล
leaders, volumes, rsi_data, big_trades = get_market_data()

# สร้าง tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔥 หุ้นเด่น", 
    "📈 วอลุ่มสูง", 
    "⚡ RSI", 
    "🏦 รายใหญ่"
])

# Tab 1: หุ้นเด่น
with tab1:
    st.subheader("หุ้นที่มีการเคลื่อนไหวเด่นประจำวัน")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔼 หุ้นขึ้นแรง")
        gainers = leaders.nlargest(5, 'Change %')[['Symbol', 'Price', 'Change %', 'Volume']]
        # กำหนดสี
        def color_green(val):
            return 'color: green'
        st.dataframe(
            gainers.style.applymap(color_green, subset=['Change %']),
            use_container_width=True
        )
    
    with col2:
        st.markdown("### 🔽 หุ้นลงแรง")
        losers = leaders.nsmallest(5, 'Change %')[['Symbol', 'Price', 'Change %', 'Volume']]
        def color_red(val):
            return 'color: red'
        st.dataframe(
            losers.style.applymap(color_red, subset=['Change %']),
            use_container_width=True
        )
    
    # Market Breadth
    st.markdown("---")
    st.markdown("### 📊 Market Breadth")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("หุ้นขึ้น", "245", "+32")
    with col2:
        st.metric("หุ้นลง", "178", "-15")
    with col3:
        st.metric("ไม่เปลี่ยนแปลง", "45", "")
    with col4:
        st.metric("อัตราส่วน", "1.38", "Positive")

# Tab 2: วอลุ่มสูง
with tab2:
    st.subheader("หุ้นที่มีวอลุ่มซื้อขายสูงสุด")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # กราฟแท่งแสดงวอลุ่ม
        fig = go.Figure(data=[
            go.Bar(
                x=volumes['Symbol'],
                y=volumes['Volume'],
                marker_color='lightblue',
                text=volumes['Volume'].round(1),
                textposition='outside'
            )
        ])
        fig.update_layout(
            title="วอลุ่มซื้อขาย (ล้านหุ้น)",
            xaxis_title="หุ้น",
            yaxis_title="วอลุ่ม (ล้าน)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### สรุปวอลุ่ม")
        st.metric("รวมวอลุ่ม 10 อันดับ", f"{volumes['Volume'].sum():.1f}M", "")
        st.metric("วอลุ่มเฉลี่ย", f"{volumes['Volume'].mean():.1f}M", "")
        
        st.markdown("### ตารางวอลุ่ม")
        st.dataframe(
            volumes[['Symbol', 'Volume', 'Price', 'Change %']].head(5),
            use_container_width=True
        )

# Tab 3: RSI
with tab3:
    st.subheader("RSI Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔴 RSI สูง (>70) - Overbought")
        overbought = rsi_data[rsi_data['Status'] == 'Overbought']
        fig = go.Figure(data=[
            go.Bar(
                x=overbought['Symbol'],
                y=overbought['RSI'],
                marker_color='red',
                text=overbought['RSI'].round(1),
                textposition='outside'
            )
        ])
        fig.add_hline(y=70, line_dash="dash", line_color="red")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🟢 RSI ต่ำ (<30) - Oversold")
        oversold = rsi_data[rsi_data['Status'] == 'Oversold']
        fig = go.Figure(data=[
            go.Bar(
                x=oversold['Symbol'],
                y=oversold['RSI'],
                marker_color='green',
                text=oversold['RSI'].round(1),
                textposition='outside'
            )
        ])
        fig.add_hline(y=30, line_dash="dash", line_color="green")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # คำอธิบาย RSI
    with st.expander("📚 วิธีอ่าน RSI"):
        st.markdown("""
        - **RSI > 70**: Overbought (ซื้อมากเกินไป) - เสี่ยงที่จะปรับลง
        - **RSI < 30**: Oversold (ขายมากเกินไป) - โอกาสที่จะรีบาวด์
        - **RSI 50-70**: แนวโน้มขาขึ้น
        - **RSI 30-50**: แนวโน้มขาลง
        """)

# Tab 4: รายใหญ่
with tab4:
    st.subheader("การซื้อขายของรายใหญ่")
    
    # กราฟแสดงการซื้อขาย
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='ต่างชาติ',
        x=big_trades['Symbol'],
        y=big_trades['Foreign'],
        marker_color='blue'
    ))
    fig.add_trace(go.Bar(
        name='สถาบัน',
        x=big_trades['Symbol'],
        y=big_trades['Institution'],
        marker_color='orange'
    ))
    fig.add_trace(go.Bar(
        name='บัญชีบริษัท',
        x=big_trades['Symbol'],
        y=big_trades['Prop'],
        marker_color='purple'
    ))
    
    fig.update_layout(
        title="การซื้อขายรายใหญ่แยกตามประเภท (ล้านบาท)",
        barmode='group',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # ตารางแสดงข้อมูล
    st.markdown("### สรุปการซื้อขายรายใหญ่")
    
    # กำหนดสีให้ตัวเลข
    def color_net(val):
        if isinstance(val, (int, float)):
            color = 'green' if val > 0 else 'red' if val < 0 else 'white'
            return f'color: {color}'
        return ''
    
    styled_df = big_trades.style.applymap(color_net, subset=['Foreign', 'Institution', 'Prop', 'Net'])
    st.dataframe(styled_df, use_container_width=True)
    
    # สรุปยอด
    col1, col2, col3 = st.columns(3)
    with col1:
        total_foreign = big_trades['Foreign'].sum()
        st.metric("ต่างชาติสุทธิ", f"{total_foreign:+,.0f}M", 
                 "ซื้อ" if total_foreign > 0 else "ขาย")
    with col2:
        total_inst = big_trades['Institution'].sum()
        st.metric("สถาบันสุทธิ", f"{total_inst:+,.0f}M",
                 "ซื้อ" if total_inst > 0 else "ขาย")
    with col3:
        total_net = big_trades['Net'].sum()
        st.metric("สุทธิทั้งหมด", f"{total_net:+,.0f}M",
                 "บวก" if total_net > 0 else "ลบ")

# ท้ายหน้า
st.markdown("---")
st.caption("ข้อมูล ณ วันที่ " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))