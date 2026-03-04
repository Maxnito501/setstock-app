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
import requests
import time

# เพิ่ม path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# ตั้งค่าเพจ
st.set_page_config(
    page_title="หุ้นยาวตามปู่บัฟเฟต์",
    page_icon="🐂",
    layout="wide"
)

# ================== SET Smart API Class ==================

class SETSmartAPI:
    """เชื่อมต่อ SET Smart API"""
    
    def __init__(self):
        self.api_key = "025e08a9-3f69-4ccf-8339-f8d37c03a4af"
        self.base_url = "https://www.setsmart.com/api/listed-company-api"
        self.last_call = 0
        self.min_interval = 3
        
    def _call_api(self, endpoint, params):
        """เรียก API พร้อม rate limit"""
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        
        params['api_key'] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, params=params, timeout=10)
            self.last_call = time.time()
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code}")
                return None
        except Exception as e:
            st.error(f"Connection Error: {e}")
            return None
    
    def get_eod_price(self, symbol):
        """ดึงราคาปิดล่าสุด"""
        data = self._call_api("eod-price-by-symbol", {"symbol": symbol})
        if data:
            return {
                'price': data.get('price', 0),
                'change': data.get('change', 0),
                'change_pct': data.get('changePercent', 0),
                'volume': data.get('volume', 0)
            }
        return None
    
    def get_financial_data(self, symbol):
        """ดึงข้อมูลงบการเงิน"""
        return self._call_api("financial-data-and-ratio-by-symbol", 
                             {"symbol": symbol})

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
</style>
""", unsafe_allow_html=True)

# ชื่อหน้า
st.markdown("""
<div style="display: flex; align-items: center;">
    <h1>🐂 วิเคราะห์หุ้นยาวตามปู่บัฟเฟต์</h1>
    <span class="version-badge">SET Smart API</span>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

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

def calculate_buffett_score(financial_data):
    """คำนวณคะแนนตามหลัก Buffett"""
    
    if not financial_data:
        return None
    
    score = 0
    details = []
    
    # 1. ROE (30 คะแนน)
    roe = financial_data.get('roe', 0)
    if roe >= 20:
        score += 30
        details.append({"criteria": "ROE", "value": f"{roe:.1f}%", "score": 30, "status": "ดีเยี่ยม"})
    elif roe >= 15:
        score += 20
        details.append({"criteria": "ROE", "value": f"{roe:.1f}%", "score": 20, "status": "ดี"})
    elif roe >= 10:
        score += 10
        details.append({"criteria": "ROE", "value": f"{roe:.1f}%", "score": 10, "status": "พอใช้"})
    else:
        details.append({"criteria": "ROE", "value": f"{roe:.1f}%", "score": 0, "status": "ต่ำ"})
    
    # 2. P/E (25 คะแนน)
    pe = financial_data.get('pe', 100)
    if pe <= 10:
        score += 25
        details.append({"criteria": "P/E", "value": f"{pe:.1f}", "score": 25, "status": "ถูกมาก"})
    elif pe <= 15:
        score += 20
        details.append({"criteria": "P/E", "value": f"{pe:.1f}", "score": 20, "status": "ถูก"})
    elif pe <= 20:
        score += 10
        details.append({"criteria": "P/E", "value": f"{pe:.1f}", "score": 10, "status": "เหมาะสม"})
    elif pe <= 25:
        score += 5
        details.append({"criteria": "P/E", "value": f"{pe:.1f}", "score": 5, "status": "แพง"})
    else:
        details.append({"criteria": "P/E", "value": f"{pe:.1f}", "score": 0, "status": "แพงมาก"})
    
    # 3. D/E (20 คะแนน)
    de = financial_data.get('de', 100)
    if de <= 0.3:
        score += 20
        details.append({"criteria": "D/E", "value": f"{de:.2f}", "score": 20, "status": "ปลอดภัยสูง"})
    elif de <= 0.5:
        score += 15
        details.append({"criteria": "D/E", "value": f"{de:.2f}", "score": 15, "status": "ปลอดภัย"})
    elif de <= 1.0:
        score += 10
        details.append({"criteria": "D/E", "value": f"{de:.2f}", "score": 10, "status": "พอรับได้"})
    else:
        details.append({"criteria": "D/E", "value": f"{de:.2f}", "score": 0, "status": "เสี่ยงสูง"})
    
    # 4. EPS Growth (15 คะแนน)
    growth = financial_data.get('eps_growth', 0)
    if growth >= 15:
        score += 15
        details.append({"criteria": "EPS Growth", "value": f"{growth:.1f}%", "score": 15, "status": "ดีเยี่ยม"})
    elif growth >= 10:
        score += 10
        details.append({"criteria": "EPS Growth", "value": f"{growth:.1f}%", "score": 10, "status": "ดี"})
    elif growth >= 5:
        score += 5
        details.append({"criteria": "EPS Growth", "value": f"{growth:.1f}%", "score": 5, "status": "พอใช้"})
    else:
        details.append({"criteria": "EPS Growth", "value": f"{growth:.1f}%", "score": 0, "status": "ช้า"})
    
    # 5. Profit Margin (10 คะแนน)
    margin = financial_data.get('profit_margin', 0)
    if margin >= 20:
        score += 10
        details.append({"criteria": "Profit Margin", "value": f"{margin:.1f}%", "score": 10, "status": "ดีเยี่ยม"})
    elif margin >= 15:
        score += 7
        details.append({"criteria": "Profit Margin", "value": f"{margin:.1f}%", "score": 7, "status": "ดี"})
    elif margin >= 10:
        score += 5
        details.append({"criteria": "Profit Margin", "value": f"{margin:.1f}%", "score": 5, "status": "พอใช้"})
    else:
        details.append({"criteria": "Profit Margin", "value": f"{margin:.1f}%", "score": 0, "status": "ต่ำ"})
    
    # 6. P/B (เพิ่มเติม)
    pb = financial_data.get('pb', 0)
    if pb <= 1.0:
        pb_status = "ถูก"
    elif pb <= 1.5:
        pb_status = "เหมาะสม"
    elif pb <= 2.0:
        pb_status = "แพง"
    else:
        pb_status = "แพงมาก"
    
    # 7. Dividend Yield (เพิ่มเติม)
    div = financial_data.get('dividend_yield', 0)
    if div >= 5:
        div_status = "สูง"
    elif div >= 3:
        div_status = "ปานกลาง"
    else:
        div_status = "ต่ำ"
    
    return {
        'total_score': score,
        'details': details,
        'pb': pb,
        'pb_status': pb_status,
        'div': div,
        'div_status': div_status
    }

# ================== Sidebar ==================

with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/stocks--v1.png", width=60)
    st.subheader("🔍 เลือกหุ้น")
    
    # รายชื่อหุ้น
    stock_list = list(portfolio_data.keys()) + ['PTTEP', 'KBANK', 'CPALL', 'BDMS']
    stock_list = sorted(list(set(stock_list)))
    
    symbol = st.selectbox("เลือกหุ้น", stock_list)
    
    st.markdown("---")
    st.subheader("📊 แสดงพอร์ต")
    show_portfolio = st.checkbox("แสดงพอร์ตปัจจุบัน", value=True)
    
    st.markdown("---")
    if st.button("🔄 รีเฟรชข้อมูล", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

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
        
        # ดึงราคาปัจจุบันจาก SET Smart
        price_data = api.get_eod_price(sym)
        current_price = price_data['price'] if price_data else cost
        
        cost_value = shares * cost
        current_value = shares * current_price
        profit_loss = current_value - cost_value
        profit_pct = (profit_loss / cost_value) * 100 if cost_value > 0 else 0
        
        total_cost += cost_value
        total_value += current_value
        
        portfolio_rows.append({
            'หุ้น': sym,
            'จำนวน': shares,
            'ราคาทุน': f"฿{cost:.2f}",
            'ราคาปัจจุบัน': f"฿{current_price:.2f}",
            'มูลค่าทุน': f"฿{cost_value:,.0f}",
            'มูลค่าปัจจุบัน': f"฿{current_value:,.0f}",
            'กำไร/ขาดทุน': f"฿{profit_loss:+,.0f}",
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

with st.spinner(f"กำลังโหลดข้อมูล {symbol} จาก SET Smart..."):
    # ดึงราคาปัจจุบัน
    price_data = api.get_eod_price(symbol)
    
    # ดึงข้อมูลงบการเงิน
    fin_data = api.get_financial_data(symbol)

col1, col2 = st.columns([1, 2])

with col1:
    # แสดงราคาปัจจุบัน
    if price_data:
        st.metric(
            "ราคาปัจจุบัน", 
            f"฿{price_data['price']:.2f}",
            f"{price_data['change']:+.2f} ({price_data['change_pct']:+.2f}%)"
        )
        st.caption(f"วอลุ่ม: {price_data['volume']:,}")
    else:
        st.warning("ไม่สามารถดึงราคาปัจจุบัน")
    
    # แสดงข้อมูลพื้นฐาน (ถ้ามี)
    if fin_data:
        st.markdown("### 📈 ข้อมูลพื้นฐาน")
        st.markdown(f"**P/E:** {fin_data.get('pe', 'N/A')}")
        st.markdown(f"**P/BV:** {fin_data.get('pbv', 'N/A')}")
        st.markdown(f"**ROE:** {fin_data.get('roe', 'N/A')}%")
        st.markdown(f"**D/E:** {fin_data.get('de', 'N/A')}")
        st.markdown(f"**ปันผล:** {fin_data.get('dividend_yield', 'N/A')}%")
        st.markdown(f"**EPS:** {fin_data.get('eps', 'N/A')}")
    else:
        st.warning("ไม่สามารถดึงข้อมูลงบการเงิน")

with col2:
    if fin_data:
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
            elif score >= 60:
                st.markdown(f"""
                <div class="score-good">
                    <h2>📊 Buffett Score: {score}</h2>
                    <p>ดี - ผ่านเกณฑ์พื้นฐาน</p>
                </div>
                """, unsafe_allow_html=True)
                recommendation = "🟡 ถือ/รอซื้อ"
                rec_color = "hold-signal"
            elif score >= 40:
                st.markdown(f"""
                <div class="score-fair">
                    <h2>⚠️ Buffett Score: {score}</h2>
                    <p>ปานกลาง - ต้องพิจารณาเพิ่มเติม</p>
                </div>
                """, unsafe_allow_html=True)
                recommendation = "⚪ เฝ้าดู"
                rec_color = "watch-signal"
            else:
                st.markdown(f"""
                <div class="score-poor">
                    <h2>❌ Buffett Score: {score}</h2>
                    <p>อ่อน - ควรหลีกเลี่ยง</p>
                </div>
                """, unsafe_allow_html=True)
                recommendation = "🔴 ขาย/หลีกเลี่ยง"
                rec_color = "sell-signal"
            
            # ตารางแสดงคะแนนรายด้าน
            st.markdown("### 📊 รายละเอียดคะแนน")
            details_df = pd.DataFrame(buffett['details'])
            st.dataframe(details_df, use_container_width=True, hide_index=True)
    else:
        st.warning("ไม่สามารถคำนวณ Buffett Score ได้")

# ================== จุดซื้อขายแนะนำ ==================

if fin_data and price_data:
    st.markdown("---")
    st.markdown("## 🎯 จุดซื้อขายแนะนำ")
    
    col1, col2, col3 = st.columns(3)
    
    current_price = price_data['price']
    
    with col1:
        st.markdown("### 🟢 จุดซื้อ")
        
        pe = fin_data.get('pe', 100)
        pb = fin_data.get('pbv', 100)
        div = fin_data.get('dividend_yield', 0)
        
        buy_points = []
        
        if pe < 10:
            buy_points.append(f"P/E {pe:.1f} (<10)")
        if pb < 1:
            buy_points.append(f"P/BV {pb:.2f} (<1)")
        if div > 5:
            buy_points.append(f"ปันผล {div:.1f}% (>5%)")
        
        if buy_points:
            for point in buy_points:
                st.markdown(f"✅ {point}")
        else:
            st.markdown("⏳ รอให้ราคาถูกลง")
        
        # ราคาเหมาะสม
        fair_price = current_price * 0.9
        st.markdown(f"**ราคาเหมาะสม:** ฿{fair_price:.2f}")
    
    with col2:
        st.markdown("### 🔴 จุดขาย")
        
        sell_points = []
        
        if pe > 20:
            sell_points.append(f"P/E {pe:.1f} (>20)")
        if pb > 2:
            sell_points.append(f"P/BV {pb:.2f} (>2)")
        
        if sell_points:
            for point in sell_points:
                st.markdown(f"⚠️ {point}")
        else:
            st.markdown("✅ ยังไม่มีสัญญาณขาย")
        
        # ราคาเป้าหมาย
        target_price = fair_price * 1.5
        st.markdown(f"**เป้าหมายขาย:** ฿{target_price:.2f}")
    
    with col3:
        st.markdown("### 📊 คำแนะนำ")
        
        st.markdown(f"<div class='{rec_color}' style='padding:0.5rem; text-align:center; font-weight:bold;'>{recommendation}</div>", unsafe_allow_html=True)
        
        # แสดงสถานะในพอร์ต (ถ้ามี)
        if symbol in portfolio_data:
            port = portfolio_data[symbol]
            cost = port['cost']
            
            st.markdown("---")
            st.markdown("### 📋 สถานะในพอร์ต")
            st.markdown(f"**จำนวน:** {port['shares']} หุ้น")
            st.markdown(f"**ราคาทุน:** ฿{cost:.2f}")
            
            profit_pct = ((current_price - cost) / cost) * 100
            profit_color = "🟢" if profit_pct > 0 else "🔴" if profit_pct < 0 else "⚪"
            st.markdown(f"**กำไร/ขาดทุน:** {profit_color} {profit_pct:+.1f}%")
            
            # แนะนำตามสถานะ
            if profit_pct < -10:
                st.markdown("💡 **แนะนำ:** DCA ซื้อเพิ่มเมื่อลงต่อ")
            elif profit_pct < -5:
                st.markdown("💡 **แนะนำ:** ถือรอ หรือ DCA เล็กน้อย")
            elif profit_pct > 20:
                st.markdown("💡 **แนะนำ:** ขายบางส่วนทำกำไร")
            else:
                st.markdown("💡 **แนะนำ:** ถือต่อ")

# ================== Footer ==================

st.markdown("---")
st.caption(f"อัปเดตล่าสุด: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("ที่มา: SET Smart API (ข้อมูล ณ วันที่ 5 มีนาคม 2569)")
