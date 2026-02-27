"""
หน้า 4: บันทึกการซื้อขาย (Trade Journal)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os
import json

# เพิ่ม path เพื่อให้ import จาก utils ได้
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# กำหนดค่าเพจ
st.set_page_config(
    page_title="บันทึกขายหมู",
    page_icon="📝",
    layout="wide"
)

# ชื่อหน้า
st.title("📝 บันทึกการซื้อขาย (Trade Journal)")
st.markdown("---")

# ฟังก์ชันจัดการไฟล์บันทึก
def load_trades():
    """โหลดข้อมูลการซื้อขายจากไฟล์"""
    trades_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'trades.csv')
    if os.path.exists(trades_file):
        return pd.read_csv(trades_file)
    else:
        # สร้าง DataFrame เปล่า
        return pd.DataFrame(columns=[
            'วันที่', 'หุ้น', 'ประเภท', 'จำนวน', 'ราคา', 
            'มูลค่ารวม', 'กลยุทธ์', 'หมายเหตุ', 'รูปภาพ'
        ])

def save_trades(df):
    """บันทึกข้อมูลการซื้อขายลงไฟล์"""
    # สร้างโฟลเดอร์ data ถ้ายังไม่มี
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    trades_file = os.path.join(data_dir, 'trades.csv')
    df.to_csv(trades_file, index=False)

# เริ่มต้น session state
if 'trades' not in st.session_state:
    st.session_state.trades = load_trades()
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None

# สร้าง tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "➕ บันทึกการซื้อขาย",
    "📊 ประวัติการซื้อขาย",
    "📈 สถิติ",
    "⚙️ จัดการข้อมูล"
])

# Tab 1: บันทึกการซื้อขาย
with tab1:
    st.subheader("บันทึกรายการซื้อขายใหม่")
    
    col1, col2 = st.columns(2)
    
    with col1:
        trade_date = st.date_input("วันที่ทำรายการ", datetime.now())
        symbol = st.text_input("รหัสหุ้น", "").upper()
        action = st.selectbox("ประเภท", ["ซื้อ", "ขาย", "ชอร์ต", "คืนชอร์ต"])
        quantity = st.number_input("จำนวนหุ้น", min_value=100, step=100, value=100)
        
    with col2:
        price = st.number_input("ราคาต่อหุ้น", min_value=0.01, step=0.25, value=10.0)
        strategy = st.selectbox("กลยุทธ์", [
            "เล่นสั้น (Momentum)",
            "เล่นสั้น (Breakout)",
            "เล่นสั้น (Reversal)",
            "เล่นสั้น (Elliott Wave)",
            "ลงทุนยาว (Value)",
            "ลงทุนยาว (Dividend)",
            "อื่นๆ"
        ])
        notes = st.text_area("หมายเหตุ", height=100)
        screenshot = st.file_uploader("แนบรูป (optional)", type=['png', 'jpg', 'jpeg'])
    
    # ปุ่มบันทึก
    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("💾 บันทึกรายการ", type="primary", use_container_width=True):
            if symbol and quantity > 0 and price > 0:
                total = quantity * price
                
                new_trade = pd.DataFrame({
                    'วันที่': [trade_date],
                    'หุ้น': [symbol],
                    'ประเภท': [action],
                    'จำนวน': [quantity],
                    'ราคา': [price],
                    'มูลค่ารวม': [total],
                    'กลยุทธ์': [strategy],
                    'หมายเหตุ': [notes],
                    'รูปภาพ': ['มี' if screenshot else '']
                })
                
                st.session_state.trades = pd.concat([st.session_state.trades, new_trade], ignore_index=True)
                save_trades(st.session_state.trades)
                st.success("✅ บันทึกรายการสำเร็จ!")
                st.balloons()
            else:
                st.error("⚠️ กรุณากรอกข้อมูลให้ครบถ้วน")

# Tab 2: ประวัติการซื้อขาย
with tab2:
    st.subheader("ประวัติการซื้อขาย")
    
    if len(st.session_state.trades) > 0:
        # ตัวกรองข้อมูล
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # กรองตามหุ้น
            all_symbols = ['ทั้งหมด'] + list(st.session_state.trades['หุ้น'].unique())
            filter_symbol = st.selectbox("กรองตามหุ้น", all_symbols)
        
        with col2:
            # กรองตามประเภท
            all_types = ['ทั้งหมด'] + list(st.session_state.trades['ประเภท'].unique())
            filter_type = st.selectbox("กรองตามประเภท", all_types)
        
        with col3:
            # กรองตามกลยุทธ์
            all_strategies = ['ทั้งหมด'] + list(st.session_state.trades['กลยุทธ์'].unique())
            filter_strategy = st.selectbox("กรองตามกลยุทธ์", all_strategies)
        
        # คัดลอก DataFrame เพื่อกรอง
        display_df = st.session_state.trades.copy()
        
        # ใช้กรอง
        if filter_symbol != 'ทั้งหมด':
            display_df = display_df[display_df['หุ้น'] == filter_symbol]
        if filter_type != 'ทั้งหมด':
            display_df = display_df[display_df['ประเภท'] == filter_type]
        if filter_strategy != 'ทั้งหมด':
            display_df = display_df[display_df['กลยุทธ์'] == filter_strategy]
        
        # เรียงตามวันที่ล่าสุด
        display_df = display_df.sort_values('วันที่', ascending=False)
        
        # แสดงจำนวนรายการ
        st.info(f"พบ {len(display_df)} รายการ")
        
        # แสดงตาราง
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400,
            column_config={
                'วันที่': st.column_config.DateColumn('วันที่'),
                'หุ้น': 'หุ้น',
                'ประเภท': 'ประเภท',
                'จำนวน': st.column_config.NumberColumn('จำนวน', format="%d"),
                'ราคา': st.column_config.NumberColumn('ราคา', format="฿%.2f"),
                'มูลค่ารวม': st.column_config.NumberColumn('มูลค่ารวม', format="฿%.2f"),
                'กลยุทธ์': 'กลยุทธ์',
                'หมายเหตุ': 'หมายเหตุ',
                'รูปภาพ': 'รูป'
            }
        )
        
        # ปุ่มลบรายการ
        with st.expander("🗑️ ลบรายการ"):
            st.warning("⚠️ เลือกรายการที่ต้องการลบ")
            
            # สร้าง list ของรายการให้เลือก
            delete_options = []
            for idx, row in display_df.iterrows():
                delete_options.append(f"{row['วันที่']} - {row['หุ้น']} {row['ประเภท']} {row['จำนวน']} หุ้น @ ฿{row['ราคา']}")
            
            if delete_options:
                selected_for_delete = st.multiselect("เลือกรายการที่จะลบ", delete_options)
                
                if st.button("🗑️ ลบรายการที่เลือก", type="secondary"):
                    # หา index ที่จะลบ
                    indices_to_drop = []
                    for opt in selected_for_delete:
                        for idx, row in display_df.iterrows():
                            if f"{row['วันที่']} - {row['หุ้น']} {row['ประเภท']} {row['จำนวน']} หุ้น @ ฿{row['ราคา']}" == opt:
                                indices_to_drop.append(idx)
                    
                    # ลบและบันทึก
                    st.session_state.trades = st.session_state.trades.drop(indices_to_drop)
                    save_trades(st.session_state.trades)
                    st.success("✅ ลบรายการเรียบร้อย")
                    st.rerun()
    else:
        st.info("📭 ยังไม่มีประวัติการซื้อขาย")

# Tab 3: สถิติ
with tab3:
    st.subheader("สถิติการซื้อขาย")
    
    if len(st.session_state.trades) > 0:
        # คำนวณสถิติ
        df = st.session_state.trades.copy()
        
        # แยกประเภทซื้อ/ขาย
        buys = df[df['ประเภท'] == 'ซื้อ']
        sells = df[df['ประเภท'] == 'ขาย']
        
        total_buy = buys['มูลค่ารวม'].sum() if not buys.empty else 0
        total_sell = sells['มูลค่ารวม'].sum() if not sells.empty else 0
        pnl = total_sell - total_buy
        
        # แสดง summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("จำนวนรายการทั้งหมด", len(df))
        with col2:
            st.metric("รายการซื้อ", len(buys))
        with col3:
            st.metric("รายการขาย", len(sells))
        with col4:
            pnl_color = "normal" if pnl >= 0 else "inverse"
            st.metric("กำไร/ขาดทุน", f"฿{pnl:,.2f}", 
                     delta_color=pnl_color)
        
        # กราฟแสดงผลตอบแทนรายเดือน
        st.markdown("---")
        st.subheader("📊 ผลตอบแทนรายเดือน")
        
        # สร้างคอลัมน์เดือน
        df['เดือน'] = pd.to_datetime(df['วันที่']).dt.to_period('M')
        
        # คำนวณผลตอบแทนรายเดือน
        monthly_pnl = []
        for month in df['เดือน'].unique():
            month_df = df[df['เดือน'] == month]
            month_buy = month_df[month_df['ประเภท'] == 'ซื้อ']['มูลค่ารวม'].sum()
            month_sell = month_df[month_df['ประเภท'] == 'ขาย']['มูลค่ารวม'].sum()
            monthly_pnl.append({
                'เดือน': str(month),
                'ซื้อ': month_buy,
                'ขาย': month_sell,
                'กำไร': month_sell - month_buy
            })
        
        monthly_df = pd.DataFrame(monthly_pnl)
        
        if not monthly_df.empty:
            # กราฟแท่ง
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='ซื้อ',
                x=monthly_df['เดือน'],
                y=monthly_df['ซื้อ'],
                marker_color='red'
            ))
            fig.add_trace(go.Bar(
                name='ขาย',
                x=monthly_df['เดือน'],
                y=monthly_df['ขาย'],
                marker_color='green'
            ))
            fig.update_layout(
                barmode='group',
                height=400,
                title="ปริมาณการซื้อขายรายเดือน"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # กราฟเส้นแสดงกำไร
            fig2 = go.Figure()
            colors = ['red' if x < 0 else 'green' for x in monthly_df['กำไร']]
            fig2.add_trace(go.Bar(
                x=monthly_df['เดือน'],
                y=monthly_df['กำไร'],
                marker_color=colors,
                text=monthly_df['กำไร'].round(0),
                textposition='outside'
            ))
            fig2.update_layout(
                height=300,
                title="กำไร/ขาดทุน รายเดือน"
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # สถิติแยกตามกลยุทธ์
        st.markdown("---")
        st.subheader("📈 ผลตอบแทนแยกตามกลยุทธ์")
        
        strategy_stats = []
        for strategy in df['กลยุทธ์'].unique():
            strategy_df = df[df['กลยุทธ์'] == strategy]
            strategy_buy = strategy_df[strategy_df['ประเภท'] == 'ซื้อ']['มูลค่ารวม'].sum()
            strategy_sell = strategy_df[strategy_df['ประเภท'] == 'ขาย']['มูลค่ารวม'].sum()
            strategy_pnl = strategy_sell - strategy_buy
            win_rate = len(strategy_df[strategy_df['ประเภท'] == 'ขาย']) / len(strategy_df[strategy_df['ประเภท'] == 'ซื้อ']) * 100 if len(strategy_df[strategy_df['ประเภท'] == 'ซื้อ']) > 0 else 0
            
            strategy_stats.append({
                'กลยุทธ์': strategy,
                'จำนวนรายการ': len(strategy_df),
                'ซื้อรวม': strategy_buy,
                'ขายรวม': strategy_sell,
                'กำไร': strategy_pnl,
                'win rate': f"{win_rate:.1f}%"
            })
        
        stats_df = pd.DataFrame(strategy_stats)
        st.dataframe(stats_df, use_container_width=True)
        
        # หุ้นที่ทำกำไรสูงสุด
        st.markdown("---")
        st.subheader("🏆 หุ้นที่ทำกำไรสูงสุด")
        
        # คำนวณกำไรแยกตามหุ้น
        stock_pnl = []
        for stock in df['หุ้น'].unique():
            stock_df = df[df['หุ้น'] == stock]
            stock_buy = stock_df[stock_df['ประเภท'] == 'ซื้อ']['มูลค่ารวม'].sum()
            stock_sell = stock_df[stock_df['ประเภท'] == 'ขาย']['มูลค่ารวม'].sum()
            stock_pnl.append({
                'หุ้น': stock,
                'ซื้อ': stock_buy,
                'ขาย': stock_sell,
                'กำไร': stock_sell - stock_buy
            })
        
        stock_pnl_df = pd.DataFrame(stock_pnl)
        stock_pnl_df = stock_pnl_df.sort_values('กำไร', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### กำไรสูงสุด")
            st.dataframe(stock_pnl_df.head(5), use_container_width=True)
        
        with col2:
            st.markdown("#### ขาดทุนสูงสุด")
            st.dataframe(stock_pnl_df.tail(5), use_container_width=True)
        
    else:
        st.info("📭 ยังไม่มีข้อมูลสำหรับแสดงสถิติ")

# Tab 4: จัดการข้อมูล
with tab4:
    st.subheader("⚙️ จัดการข้อมูล")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📥 นำเข้าข้อมูล")
        uploaded_file = st.file_uploader("เลือกไฟล์ CSV", type=['csv'])
        
        if uploaded_file is not None:
            try:
                import_df = pd.read_csv(uploaded_file)
                st.success(f"พบ {len(import_df)} รายการ")
                
                if st.button("นำเข้าข้อมูล"):
                    st.session_state.trades = import_df
                    save_trades(st.session_state.trades)
                    st.success("✅ นำเข้าข้อมูลสำเร็จ!")
                    st.rerun()
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")
    
    with col2:
        st.markdown("### 📤 ส่งออกข้อมูล")
        if len(st.session_state.trades) > 0:
            csv = st.session_state.trades.to_csv(index=False)
            st.download_button(
                label="📥 ดาวน์โหลด CSV",
                data=csv,
                file_name=f"trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("ไม่มีข้อมูลให้ส่งออก")
    
    st.markdown("---")
    st.markdown("### 🗑️ ลบข้อมูลทั้งหมด")
    
    if st.button("⚠️ ลบประวัติทั้งหมด", type="secondary"):
        if st.checkbox("ยืนยันการลบข้อมูลทั้งหมด"):
            st.session_state.trades = pd.DataFrame(columns=[
                'วันที่', 'หุ้น', 'ประเภท', 'จำนวน', 'ราคา', 
                'มูลค่ารวม', 'กลยุทธ์', 'หมายเหตุ', 'รูปภาพ'
            ])
            save_trades(st.session_state.trades)
            st.success("✅ ลบข้อมูลทั้งหมดเรียบร้อย")
            st.rerun()

# ท้ายหน้า
st.markdown("---")
st.caption(f"อัปเดตล่าสุด: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")