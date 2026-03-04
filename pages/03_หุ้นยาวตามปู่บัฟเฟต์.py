"""
หน้า 3: วิเคราะห์หุ้นยาวตามปู่บัฟเฟต์ (Value Investing)
- ใช้ SET Smart API (ของพี่โบ้)
- วิเคราะห์ Buffett Score และดัชนีอื่นๆ
- แนะนำซื้อ/ขาย/รอ
- แสดงสถานะพอร์ตปัจจุบัน
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
import os

# เพิ่ม path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import SET Smart API
from utils.setsmart_api import SETSmartAPI

# ตั้งค่าเพจ
st.set_page_config(
    page_title="หุ้นยาวตามปู่บัฟเฟต์",
    page_icon="🐂",
    layout="wide"
)

# ================== สร้าง instance ==================

@st.cache_resource
def get_api():
    return SETSmartAPI()

api = get_api()

# ================== CSS ==================

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
    .score-excellent {
        background: #10b981;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .score-good {
        background: #3b82f6;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .score-fair {
        background: #f59e0b;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .score-poor {
        background: #ef4444;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .portfolio-box {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .buy-signal {
        background: #10b981;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        display: inline-block;
    }
    .sell-signal {
        background: #ef4444;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        display: inline-block;
    }
    .hold-signal {
        background: #f59e0b;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        display: inline-block;
    }
    .watch-signal {
        background: #6b7280;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        display: inline-block;
    }
    .mode-badge {
        background: #f0f2f6;
        color: #333;
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# ================== Sidebar ==================

with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/stocks--v1.png", width=60)
    st.subheader("🔍 เลือกหุ้น")
    
    # รายชื่อหุ้นทั้งหมดที่รองรับ
    stock_list = [
        'PTT', 'SCB', 'TISCO', 'AOT', 'HMPRO', 'SIRI', 'PTG',
        'PTTEP', 'KBANK', 'KTB', 'CPALL', 'BDMS', 'BH', 'GULF',
        'ADVANC', 'INTUCH', 'TOP', 'BANPU', 'CHG', 'COM7',
        'EA', 'LH', 'MINT', 'RATCH', 'SAWAD', 'TRUE', 'WHA'
    ]
    stock_list = sorted(stock_list)
    
    symbol = st.selectbox("เลือกหุ้น", stock_list)
    
    st.markdown("---")
    st.subheader("⚙️ ตั้งค่า")
    
    # เลือกโหมดข้อมูล
    use_mock = st.checkbox("ใช้ข้อมูลตัวอย่าง (Mock Mode)", value=api.use_mock)
    if use_mock != api.use_mock:
        api.set_use_mock(use_mock)
        st.rerun()
    
    show_portfolio = st.checkbox("แสดงพอร์ตปัจจุบัน", value=True)
    
    st.markdown("---")
    if st.button("🔄 รีเฟรชข้อมูล", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ================== ข้อมูลพอร์ตปัจจุบันของพี่โบ้ ==================

portfolio_data = {
    'PTT': {'shares': 100, 'cost': 33.00},
    'SCB': {'shares': 25, 'cost': 135.50},
    'TISCO': {'shares': 100, 'cost': 112.50},
    'AOT': {'shares': 200, 'cost': 54.50},
    'HMPRO': {'shares': 200, 'cost': 7.05},
    'SIRI': {'shares': 2300, 'cost': 1.47},
    'PTG': {'shares': 200, 'cost': 9.60}
}

# ================== ฟังก์ชันคำนวณ Buffett Score ==================

def calculate_buffett_score(fin_data):
    """คำนวณคะแนนตามหลัก Buffett"""
    
    if not fin_data:
        return None
    
    score = 0
    details = []
    
    # 1. ROE (30 คะแนน)
    roe = fin_data.get('roe', 0)
    if roe >= 20:
        score += 30
        details.append({"ปัจจัย": "ROE", "ค่า": f"{roe:.1f}%", "คะแนน": 30, "สถานะ": "ดีเยี่ยม"})
    elif roe >= 15:
        score += 20
        details.append({"ปัจจัย": "ROE", "ค่า": f"{roe:.1f}%", "คะแนน": 20, "สถานะ": "ดี"})
    elif roe >= 10:
        score += 10
        details.append({"ปัจจัย": "ROE", "ค่า": f"{roe:.1f}%", "คะแนน": 10, "สถานะ": "พอใช้"})
    else:
        details.append({"ปัจจัย": "ROE", "ค่า": f"{roe:.1f}%", "คะแนน": 0, "สถานะ": "ต่ำ"})
    
    # 2. P/E (25 คะแนน)
    pe = fin_data.get('pe', 100)
    if pe <= 10:
        score += 25
        details.append({"ปัจจัย": "P/E", "ค่า": f"{pe:.1f}", "คะแนน": 25, "สถานะ": "ถูกมาก"})
    elif pe <= 15:
        score += 20
        details.append({"ปัจจัย": "P/E", "ค่า": f"{pe:.1f}", "คะแนน": 20, "สถานะ": "ถูก"})
    elif pe <= 20:
        score += 10
        details.append({"ปัจจัย": "P/E", "ค่า": f"{pe:.1f}", "คะแนน": 10, "สถานะ": "เหมาะสม"})
    elif pe <= 25:
        score += 5
        details.append({"ปัจจัย": "P/E", "ค่า": f"{pe:.1f}", "คะแนน": 5, "สถานะ": "แพง"})
    else:
        details.append({"ปัจจัย": "P/E", "ค่า": f"{pe:.1f}", "คะแนน": 0, "สถานะ": "แพงมาก"})
    
    # 3. D/E (20 คะแนน)
    de = fin_data.get('de', 100)
    if de <= 0.3:
        score += 20
        details.append({"ปัจจัย": "D/E", "ค่า": f"{de:.2f}", "คะแนน": 20, "สถานะ": "ปลอดภัยสูง"})
    elif de <= 0.5:
        score += 15
        details.append({"ปัจจัย": "D/E", "ค่า": f"{de:.2f}", "คะแนน": 15, "สถานะ": "ปลอดภัย"})
    elif de <= 1.0:
        score += 10
        details.append({"ปัจจัย": "D/E", "ค่า": f"{de:.2f}", "คะแนน": 10, "สถานะ": "พอรับได้"})
    else:
        details.append({"ปัจจัย": "D/E", "ค่า": f"{de:.2f}", "คะแนน": 0, "สถานะ": "เสี่ยงสูง"})
    
    # 4. EPS Growth (15 คะแนน)
    growth = fin_data.get('eps_growth', 0)
    if growth >= 15:
        score += 15
        details.append({"ปัจจัย": "EPS Growth", "ค่า": f"{growth:.1f}%", "คะแนน": 15, "สถานะ": "ดีเยี่ยม"})
    elif growth >= 10:
        score += 10
        details.append({"ปัจจัย": "EPS Growth", "ค่า": f"{growth:.1f}%", "คะแนน": 10, "สถานะ": "ดี"})
    elif growth >= 5:
        score += 5
        details.append({"ปัจจัย": "EPS Growth", "ค่า": f"{growth:.1f}%", "คะแนน": 5, "สถานะ": "พอใช้"})
    else:
        details.append({"ปัจจัย": "EPS Growth", "ค่า": f"{growth:.1f}%", "คะแนน": 0, "สถานะ": "ช้า"})
    
    # 5. Profit Margin (10 คะแนน)
    margin = fin_data.get('profit_margin', 0)
    if margin >= 20:
        score += 10
        details.append({"ปัจจัย": "Profit Margin", "ค่า": f"{margin:.1f}%", "คะแนน": 10, "สถานะ": "ดีเยี่ยม"})
    elif margin >= 15:
        score += 7
        details.append({"ปัจจัย": "Profit Margin", "ค่า": f"{margin:.1f}%", "คะแนน": 7, "สถานะ": "ดี"})
    elif margin >= 10:
        score += 5
        details.append({"ปัจจัย": "Profit Margin", "ค่า": f"{margin:.1f}%", "คะแนน": 5, "สถานะ": "พอใช้"})
    else:
        details.append({"ปัจจัย": "Profit Margin", "ค่า": f"{margin:.1f}%", "คะแนน": 0, "สถานะ": "ต่ำ"})
    
    return {
        'total_score': score,
        'details': details,
        'pe': pe,
        'pbv': fin_data.get('pbv', 0),
        'div': fin_data.get('dividend_yield', 0)
    }

# ================== ส่วนหัว ==================

st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between;">
    <div style="display: flex; align-items: center;">
        <h1>🐂 วิเคราะห์หุ้นยาวตามปู่บัฟเฟต์</h1>
        <span class="version-badge">SET Smart API</span>
    </div>
</div>
""", unsafe_allow_html=True)

# แสดงโหมดปัจจุบัน
mode_text = "📊 ใช้ข้อมูลตัวอย่าง (Mock)" if api.use_mock else "✅ ใช้ API จริง (Live)"
st.markdown(f"<span class='mode-badge'>{mode_text}</span>", unsafe_allow_html=True)
st.markdown("---")

# ================== แสดงพอร์ตปัจจุบัน ==================

if show_portfolio:
    st.markdown("## 📋 พอร์ตการลงทุนปัจจุบัน")
    
    # คำนวณมูลค่าพอร์ต
    total_cost = 0
    total_value = 0
    portfolio_rows = []
    
    for sym, data in portfolio_data.items():
        shares = data['shares']
        cost = data['cost']
        
        # ดึงราคาปัจจุบัน
        price_data = api.get_eod_price(sym)
        current_price = price_data['price'] if price_data and price_data.get('price') else cost
        
        cost_value = shares * cost
        current_value = shares * current_price
        profit_loss = current_value - cost_value
        profit_pct = (profit_loss / cost_value) * 100 if cost_value > 0 else 0
        
        total_cost += cost_value
        total_value += current_value
        
        # กำหนดสี
        color = "🟢" if profit_loss > 0 else "🔴" if profit_loss < 0 else "⚪"
        
        portfolio_rows.append({
            'หุ้น': sym,
            'จำนวน': shares,
            'ราคาทุน': f"฿{cost:.2f}",
            'ราคาปัจจุบัน': f"฿{current_price:.2f}",
            'มูลค่าทุน': f"฿{cost_value:,.0f}",
            'มูลค่าปัจจุบัน': f"฿{current_value:,.0f}",
            'กำไร/ขาดทุน': f"{color} ฿{profit_loss:+,.0f}",
            '%': f"{profit_pct:+.1f}%"
        })
    
    # แสดงสรุปพอร์ต
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("มูลค่าทุนรวม", f"฿{total_cost:,.0f}")
    with col2:
        st.metric("มูลค่าปัจจุบัน", f"฿{total_value:,.0f}")
    with col3:
        total_profit = total_value - total_cost
        st.metric("กำไร/ขาดทุนรวม", f"฿{total_profit:+,.0f}")
    with col4:
        total_pct = (total_profit / total_cost) * 100 if total_cost > 0 else 0
        st.metric("% รวม", f"{total_pct:+.1f}%")
    
    # แสดงตารางพอร์ต
    if portfolio_rows:
        df_portfolio = pd.DataFrame(portfolio_rows)
        st.dataframe(df_portfolio, use_container_width=True, hide_index=True)
    
    st.markdown("---")

# ================== วิเคราะห์หุ้นที่เลือก ==================

st.markdown(f"## 📊 วิเคราะห์ {symbol}")

with st.spinner(f"กำลังโหลดข้อมูล {symbol}..."):
    # ดึงราคาปัจจุบัน
    price_data = api.get_eod_price(symbol)
    
    # ดึงข้อมูลงบการเงิน
    fin_data = api.get_financial_data(symbol)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 💰 ข้อมูลราคา")
    
    if price_data and price_data.get('price'):
        price = price_data['price']
        change = price_data.get('change', 0)
        change_pct = price_data.get('change_pct', 0)
        
        st.metric(
            "ราคาปัจจุบัน", 
            f"฿{price:.2f}",
            f"{change:+.2f} ({change_pct:+.2f}%)"
        )
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**สูงสุด:** ฿{price_data.get('high', price):.2f}")
            st.markdown(f"**ต่ำสุด:** ฿{price_data.get('low', price):.2f}")
        with col_b:
            st.markdown(f"**เปิด:** ฿{price_data.get('open', price):.2f}")
            st.markdown(f"**วอลุ่ม:** {price_data.get('volume', 0):,}")
    else:
        st.warning("ไม่สามารถดึงราคาปัจจุบัน")
    
    st.markdown("---")
    st.markdown("### 📈 ข้อมูลพื้นฐาน")
    
    if fin_data and fin_data.get('success'):
        st.markdown(f"**P/E:** {fin_data.get('pe', 'N/A'):.2f}")
        st.markdown(f"**P/BV:** {fin_data.get('pbv', 'N/A'):.2f}")
        st.markdown(f"**ROE:** {fin_data.get('roe', 'N/A'):.2f}%")
        st.markdown(f"**D/E:** {fin_data.get('de', 'N/A'):.2f}")
        st.markdown(f"**ปันผล:** {fin_data.get('dividend_yield', 'N/A'):.2f}%")
        st.markdown(f"**EPS:** {fin_data.get('eps', 'N/A'):.2f}")
        st.markdown(f"**EPS Growth:** {fin_data.get('eps_growth', 'N/A'):.2f}%")
    else:
        st.warning("ไม่สามารถดึงข้อมูลงบการเงิน")

with col2:
    if fin_data and fin_data.get('success'):
        # คำนวณ Buffett Score
        buffett = calculate_buffett_score(fin_data)
        
        if buffett:
            score = buffett['total_score']
            
            # แสดงคะแนน
            if score >= 80:
                st.markdown(f"""
                <div class="score-excellent">
                    <h2>🏆 Buffett Score: {score}</h2>
                    <p>ดีมาก - เหมาะสำหรับการลงทุนระยะยาว</p>
                </div>
                """, unsafe_allow_html=True)
                recommendation = "🟢 ซื้อสะสม"
                rec_color = "buy-signal"
                rec_text = "ซื้อสะสม"
            elif score >= 60:
                st.markdown(f"""
                <div class="score-good">
                    <h2>📊 Buffett Score: {score}</h2>
                    <p>ดี - ผ่านเกณฑ์พื้นฐาน</p>
                </div>
                """, unsafe_allow_html=True)
                recommendation = "🟡 ถือ/รอซื้อ"
                rec_color = "hold-signal"
                rec_text = "ถือ/รอซื้อ"
            elif score >= 40:
                st.markdown(f"""
                <div class="score-fair">
                    <h2>⚠️ Buffett Score: {score}</h2>
                    <p>ปานกลาง - ต้องพิจารณาเพิ่มเติม</p>
                </div>
                """, unsafe_allow_html=True)
                recommendation = "⚪ เฝ้าดู"
                rec_color = "watch-signal"
                rec_text = "เฝ้าดู"
            else:
                st.markdown(f"""
                <div class="score-poor">
                    <h2>❌ Buffett Score: {score}</h2>
                    <p>อ่อน - ควรหลีกเลี่ยง</p>
                </div>
                """, unsafe_allow_html=True)
                recommendation = "🔴 ขาย/หลีกเลี่ยง"
                rec_color = "sell-signal"
                rec_text = "ขาย/หลีกเลี่ยง"
            
            # ตารางแสดงคะแนนรายด้าน
            st.markdown("### 📊 รายละเอียดคะแนน")
            details_df = pd.DataFrame(buffett['details'])
            st.dataframe(details_df, use_container_width=True, hide_index=True)
            
            # แสดงจุดซื้อขาย
            st.markdown("---")
            st.markdown("### 🎯 จุดซื้อขายแนะนำ")
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.markdown("#### 🟢 จุดซื้อ")
                buy_points = []
                if buffett['pe'] < 10:
                    buy_points.append(f"P/E {buffett['pe']:.1f} (<10)")
                if buffett['pbv'] < 1:
                    buy_points.append(f"P/BV {buffett['pbv']:.2f} (<1)")
                if buffett['div'] > 5:
                    buy_points.append(f"ปันผล {buffett['div']:.1f}% (>5%)")
                
                if buy_points:
                    for point in buy_points:
                        st.markdown(f"✅ {point}")
                else:
                    st.markdown("⏳ รอให้ราคาถูกลง")
            
            with col_b:
                st.markdown("#### 🔴 จุดขาย")
                sell_points = []
                if buffett['pe'] > 20:
                    sell_points.append(f"P/E {buffett['pe']:.1f} (>20)")
                if buffett['pbv'] > 2:
                    sell_points.append(f"P/BV {buffett['pbv']:.2f} (>2)")
                
                if sell_points:
                    for point in sell_points:
                        st.markdown(f"⚠️ {point}")
                else:
                    st.markdown("✅ ยังไม่มีสัญญาณขาย")
            
            with col_c:
                st.markdown("#### 📊 คำแนะนำ")
                st.markdown(f"<div class='{rec_color}' style='padding:0.5rem; text-align:center; font-weight:bold;'>{rec_text}</div>", unsafe_allow_html=True)
    
    else:
        st.warning("ไม่สามารถคำนวณ Buffett Score ได้")

# ================== แสดงสถานะในพอร์ต (ถ้ามี) ==================

if symbol in portfolio_data and price_data:
    st.markdown("---")
    st.markdown("### 📋 สถานะในพอร์ต")
    
    port = portfolio_data[symbol]
    cost = port['cost']
    shares = port['shares']
    current_price = price_data['price']
    
    cost_value = shares * cost
    current_value = shares * current_price
    profit_loss = current_value - cost_value
    profit_pct = (profit_loss / cost_value) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("จำนวนหุ้น", f"{shares}")
    with col2:
        st.metric("ราคาทุน", f"฿{cost:.2f}")
    with col3:
        st.metric("มูลค่าทุน", f"฿{cost_value:,.0f}")
    with col4:
        st.metric("มูลค่าปัจจุบัน", f"฿{current_value:,.0f}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        profit_color = "🟢" if profit_loss > 0 else "🔴" if profit_loss < 0 else "⚪"
        st.metric("กำไร/ขาดทุน", f"{profit_color} ฿{profit_loss:+,.0f}")
    with col2:
        st.metric("% เปลี่ยนแปลง", f"{profit_pct:+.1f}%")
    with col3:
        # แนะนำตามสถานะ
        if profit_pct < -10:
            st.info("💡 DCA ซื้อเพิ่มเมื่อลงต่อ")
        elif profit_pct < -5:
            st.info("💡 ถือรอ หรือ DCA เล็กน้อย")
        elif profit_pct > 20:
            st.success("💡 ขายบางส่วนทำกำไร")
        else:
            st.info("💡 ถือต่อ")

# ================== Footer ==================

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.caption(f"ข้อมูล ณ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
with col2:
    st.caption("ที่มา: SET Smart API / ข้อมูลตัวอย่าง")
