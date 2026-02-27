"""
โมดูลสำหรับวิเคราะห์พื้นฐาน (Buffett Style)
"""

import pandas as pd
import numpy as np

class FundamentalAnalyzer:
    def __init__(self):
        """เริ่มต้นตัววิเคราะห์พื้นฐาน"""
        pass
    
    def calculate_buffett_score(self, stock_data):
        """
        คำนวณ Buffett Score (คะแนนตามหลักของ Warren Buffett)
        
        Parameters:
        stock_data: dict ที่มีข้อมูลพื้นฐานของหุ้น
        {
            'roe': Return on Equity,
            'pe': P/E Ratio,
            'debt_to_equity': D/E Ratio,
            'profit_margin': อัตรากำไร,
            'eps_growth': การเติบโตของ EPS,
            'dividend': อัตราเงินปันผล
        }
        
        Returns:
        dict: คะแนนและคำแนะนำ
        """
        score = 0
        details = []
        
        # 1. ตรวจสอบ ROE (Return on Equity) - ควร > 15%
        roe = stock_data.get('roe', 0)
        if roe >= 20:
            score += 30
            details.append({"criteria": "ROE", "status": "ดีเยี่ยม", "score": 30})
        elif roe >= 15:
            score += 20
            details.append({"criteria": "ROE", "status": "ดี", "score": 20})
        elif roe >= 10:
            score += 10
            details.append({"criteria": "ROE", "status": "พอใช้", "score": 10})
        else:
            details.append({"criteria": "ROE", "status": "ควรปรับปรุง", "score": 0})
        
        # 2. ตรวจสอบ P/E Ratio - ควรต่ำ
        pe = stock_data.get('pe', 100)
        if pe <= 10:
            score += 25
            details.append({"criteria": "P/E", "status": "ถูก", "score": 25})
        elif pe <= 15:
            score += 20
            details.append({"criteria": "P/E", "status": "ค่อนข้างถูก", "score": 20})
        elif pe <= 20:
            score += 10
            details.append({"criteria": "P/E", "status": "เหมาะสม", "score": 10})
        elif pe <= 25:
            score += 5
            details.append({"criteria": "P/E", "status": "แพง", "score": 5})
        else:
            details.append({"criteria": "P/E", "status": "แพงมาก", "score": 0})
        
        # 3. ตรวจสอบ D/E (Debt to Equity) - ควร < 1
        de = stock_data.get('debt_to_equity', 100)
        if de <= 0.3:
            score += 20
            details.append({"criteria": "D/E", "status": "ปลอดภัยสูง", "score": 20})
        elif de <= 0.5:
            score += 15
            details.append({"criteria": "D/E", "status": "ปลอดภัย", "score": 15})
        elif de <= 1.0:
            score += 10
            details.append({"criteria": "D/E", "status": "พอรับได้", "score": 10})
        else:
            details.append({"criteria": "D/E", "status": "เสี่ยงสูง", "score": 0})
        
        # 4. ตรวจสอบการเติบโตของ EPS
        eps_growth = stock_data.get('eps_growth', 0)
        if eps_growth >= 15:
            score += 15
            details.append({"criteria": "EPS Growth", "status": "ดีเยี่ยม", "score": 15})
        elif eps_growth >= 10:
            score += 10
            details.append({"criteria": "EPS Growth", "status": "ดี", "score": 10})
        elif eps_growth >= 5:
            score += 5
            details.append({"criteria": "EPS Growth", "status": "พอใช้", "score": 5})
        else:
            details.append({"criteria": "EPS Growth", "status": "ช้า", "score": 0})
        
        # 5. ตรวจสอบอัตรากำไร
        profit_margin = stock_data.get('profit_margin', 0)
        if profit_margin >= 20:
            score += 10
            details.append({"criteria": "Profit Margin", "status": "ดีเยี่ยม", "score": 10})
        elif profit_margin >= 15:
            score += 7
            details.append({"criteria": "Profit Margin", "status": "ดี", "score": 7})
        elif profit_margin >= 10:
            score += 5
            details.append({"criteria": "Profit Margin", "status": "พอใช้", "score": 5})
        else:
            details.append({"criteria": "Profit Margin", "status": "ต่ำ", "score": 0})
        
        # สรุปผล
        if score >= 80:
            recommendation = "ซื้อ (ผ่านเกณฑ์ Buffett)"
            level = "ดีมาก"
        elif score >= 60:
            recommendation = "ถือ/สะสม"
            level = "ดี"
        elif score >= 40:
            recommendation = "เฝ้าดู"
            level = "ปานกลาง"
        else:
            recommendation = "ไม่ผ่านเกณฑ์"
            level = "ควรหลีกเลี่ยง"
        
        return {
            'total_score': score,
            'level': level,
            'recommendation': recommendation,
            'details': details
        }
    
    def calculate_intrinsic_value_dcf(self, stock_data, years=5):
        """
        คำนวณมูลค่าที่แท้จริงด้วยวิธี DCF (Discounted Cash Flow)
        """
        # รับข้อมูล
        current_eps = stock_data.get('eps', 0)
        growth_rate = stock_data.get('growth_rate', 10) / 100
        discount_rate = stock_data.get('discount_rate', 8) / 100
        terminal_growth = stock_data.get('terminal_growth', 3) / 100
        
        if current_eps <= 0:
            return 0
        
        # คำนวณกระแสเงินสดในอนาคต
        future_values = []
        for year in range(1, years + 1):
            future_eps = current_eps * ((1 + growth_rate) ** year)
            present_value = future_eps / ((1 + discount_rate) ** year)
            future_values.append(present_value)
        
        # คำนวณ terminal value
        terminal_eps = current_eps * ((1 + growth_rate) ** years) * (1 + terminal_growth)
        terminal_value = terminal_eps / (discount_rate - terminal_growth)
        terminal_pv = terminal_value / ((1 + discount_rate) ** years)
        
        # มูลค่าที่แท้จริง
        intrinsic_value = sum(future_values) + terminal_pv
        
        return round(intrinsic_value, 2)
    
    def calculate_margin_of_safety(self, current_price, intrinsic_value):
        """
        คำนวณ Margin of Safety (ส่วนเผื่อความปลอดภัย)
        """
        if intrinsic_value <= 0 or current_price <= 0:
            return 0
        
        margin = ((intrinsic_value - current_price) / intrinsic_value) * 100
        return round(margin, 2)
    
    def graham_number(self, eps, book_value):
        """
        คำนวณ Graham Number (สูตรของ Benjamin Graham)
        Graham Number = sqrt(22.5 * EPS * BVPS)
        """
        if eps <= 0 or book_value <= 0:
            return 0
        
        graham = np.sqrt(22.5 * eps * book_value)
        return round(graham, 2)
    
    def analyze_moat(self, stock_data):
        """
        วิเคราะห์ Economic Moat (ความได้เปรียบในการแข่งขัน)
        """
        moat_score = 0
        moat_factors = []
        
        # 1. Brand Strength (ความแข็งแกร่งของแบรนด์)
        brand = stock_data.get('brand_strength', 5)  # คะแนน 1-10
        if brand >= 8:
            moat_score += 20
            moat_factors.append({"factor": "Brand", "score": 20})
        elif brand >= 6:
            moat_score += 15
            moat_factors.append({"factor": "Brand", "score": 15})
        else:
            moat_factors.append({"factor": "Brand", "score": 5})
        
        # 2. Market Share (ส่วนแบ่งการตลาด)
        market_share = stock_data.get('market_share', 10)  # เปอร์เซ็นต์
        if market_share >= 30:
            moat_score += 25
            moat_factors.append({"factor": "Market Share", "score": 25})
        elif market_share >= 20:
            moat_score += 20
            moat_factors.append({"factor": "Market Share", "score": 20})
        elif market_share >= 10:
            moat_score += 15
            moat_factors.append({"factor": "Market Share", "score": 15})
        else:
            moat_factors.append({"factor": "Market Share", "score": 5})
        
        # 3. Profit Margin (อัตรากำไร)
        margin = stock_data.get('profit_margin', 0)
        if margin >= 20:
            moat_score += 25
            moat_factors.append({"factor": "Profit Margin", "score": 25})
        elif margin >= 15:
            moat_score += 20
            moat_factors.append({"factor": "Profit Margin", "score": 20})
        elif margin >= 10:
            moat_score += 15
            moat_factors.append({"factor": "Profit Margin", "score": 15})
        else:
            moat_factors.append({"factor": "Profit Margin", "score": 5})
        
        # 4. R&D หรือ Innovation
        innovation = stock_data.get('innovation_score', 5)
        if innovation >= 8:
            moat_score += 15
            moat_factors.append({"factor": "Innovation", "score": 15})
        else:
            moat_factors.append({"factor": "Innovation", "score": 5})
        
        # 5. Switching Cost
        switching_cost = stock_data.get('switching_cost', 5)
        if switching_cost >= 8:
            moat_score += 15
            moat_factors.append({"factor": "Switching Cost", "score": 15})
        else:
            moat_factors.append({"factor": "Switching Cost", "score": 5})
        
        # สรุป
        if moat_score >= 80:
            moat_level = "แข็งแกร่งมาก"
        elif moat_score >= 60:
            moat_level = "แข็งแกร่ง"
        elif moat_score >= 40:
            moat_level = "ปานกลาง"
        else:
            moat_level = "อ่อนแอ"
        
        return {
            'moat_score': moat_score,
            'moat_level': moat_level,
            'factors': moat_factors
        }
    
    def get_sample_data(self, symbol):
        """
        ข้อมูลตัวอย่างสำหรับทดสอบ (mock data)
        """
        sample_data = {
            'ADVANC': {
                'roe': 28.5,
                'pe': 19.5,
                'debt_to_equity': 0.85,
                'eps_growth': 12.5,
                'profit_margin': 18.5,
                'eps': 12.8,
                'book_value': 45.2,
                'growth_rate': 10,
                'brand_strength': 9,
                'market_share': 45,
                'innovation_score': 8,
                'switching_cost': 9
            },
            'PTT': {
                'roe': 12.3,
                'pe': 8.2,
                'debt_to_equity': 0.62,
                'eps_growth': 8.2,
                'profit_margin': 8.2,
                'eps': 4.35,
                'book_value': 28.5,
                'growth_rate': 5,
                'brand_strength': 8,
                'market_share': 35,
                'innovation_score': 6,
                'switching_cost': 5
            },
            'CPALL': {
                'roe': 18.7,
                'pe': 25.3,
                'debt_to_equity': 1.82,
                'eps_growth': 15.2,
                'profit_margin': 4.5,
                'eps': 2.85,
                'book_value': 12.8,
                'growth_rate': 12,
                'brand_strength': 9,
                'market_share': 70,
                'innovation_score': 7,
                'switching_cost': 6
            },
            'SCB': {
                'roe': 9.2,
                'pe': 7.8,
                'debt_to_equity': 1.12,
                'eps_growth': 5.8,
                'profit_margin': 35.2,
                'eps': 14.2,
                'book_value': 185.5,
                'growth_rate': 4,
                'brand_strength': 8,
                'market_share': 18,
                'innovation_score': 7,
                'switching_cost': 8
            },
            'KBANK': {
                'roe': 10.1,
                'pe': 8.5,
                'debt_to_equity': 1.08,
                'eps_growth': 6.5,
                'profit_margin': 32.8,
                'eps': 16.8,
                'book_value': 195.2,
                'growth_rate': 5,
                'brand_strength': 8,
                'market_share': 17,
                'innovation_score': 7,
                'switching_cost': 8
            }
        }
        
        return sample_data.get(symbol, sample_data['ADVANC'])