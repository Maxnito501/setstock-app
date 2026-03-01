"""
โมดูลเชื่อมต่อ SET Smart API
- ส่ง API Key เป็น Parameter
"""

import requests
import time
import pandas as pd
from datetime import datetime
import streamlit as st

class SETSmartAPI:
    def __init__(self):
        """เริ่มต้นการเชื่อมต่อ SET Smart API"""
        self.base_url = "https://www.setsmart.com/api/listed-company-api"
        self.api_key = "025e08a9-3f69-4ccf-8339-f8d37c03a4af"  # API Key
        self.last_call = {}  # เก็บเวลาที่เรียกใช้ล่าสุดของแต่ละหุ้น
        self.min_interval = 20  # เว้น 20 วินาที
        
        # ตั้งค่า headers (ไม่ต้องมี API Key ใน headers)
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # ทดสอบการเชื่อมต่อ
        self.test_connection()
    
    def test_connection(self):
        """ทดสอบว่า API key ใช้ได้ไหม"""
        try:
            # ลองเรียก API ง่ายๆ โดยส่ง api_key ใน params
            params = {
                "symbol": "ADVANC",
                "api_key": self.api_key  # ส่ง API Key ใน params
            }
            
            response = requests.get(
                f"{self.base_url}/eod-price-by-symbol",
                headers=self.headers,
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                print("✅ เชื่อมต่อ SET Smart API สำเร็จ")
                print("Response:", response.json())
            else:
                print(f"⚠️ เชื่อมต่อไม่สำเร็จ: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"⚠️ ไม่สามารถเชื่อมต่อ: {e}")
    
    def get_stock_price(self, symbol):
        """
        ดึงราคาและวอลุ่มปัจจุบันของหุ้น
        """
        # เช็คว่าควรเรียกได้หรือยัง
        if symbol in self.last_call:
            elapsed = time.time() - self.last_call[symbol]
            if elapsed < self.min_interval:
                wait_time = self.min_interval - elapsed
                return {
                    'success': False,
                    'error': f'ต้องรออีก {wait_time:.0f} วินาที',
                    'wait': wait_time
                }
        
        try:
            # เรียก API จริง - ส่ง api_key ใน params
            url = f"{self.base_url}/eod-price-by-symbol"
            params = {
                "symbol": symbol,
                "api_key": self.api_key  # API Key อยู่ในนี้!
            }
            
            response = requests.get(
                url, 
                headers=self.headers, 
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # บันทึกเวลาที่เรียก
                self.last_call[symbol] = time.time()
                
                return {
                    'success': True,
                    'symbol': symbol,
                    'data': data,  # ส่งข้อมูลดิบกลับไปก่อน
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code}",
                    'details': response.text
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_eod_price(self, symbol, date=None):
        """
        ดึงราคาปิดรายวัน
        """
        try:
            url = f"{self.base_url}/eod-price-by-symbol"
            params = {
                "symbol": symbol,
                "api_key": self.api_key
            }
            if date:
                params["date"] = date
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_all_stocks(self):
        """
        ดึงข้อมูลทุกหลักทรัพย์
        """
        try:
            url = f"{self.base_url}/eod-price-by-security-type"
            params = {
                "api_key": self.api_key
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_financial_data(self, symbol):
        """
        ดึงข้อมูลงบการเงินรายหลักทรัพย์
        """
        try:
            url = f"{self.base_url}/financial-data-and-ratio-by-symbol"
            params = {
                "symbol": symbol,
                "api_key": self.api_key
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_all_financial(self):
        """
        ดึงข้อมูลงบการเงินทั้งหมด
        """
        try:
            url = f"{self.base_url}/financial-data-and-ratio"
            params = {
                "api_key": self.api_key
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def wait_if_needed(self, symbol):
        """
        รอถ้ายังไม่ถึงเวลาที่กำหนด
        """
        if symbol in self.last_call:
            elapsed = time.time() - self.last_call[symbol]
            if elapsed < self.min_interval:
                wait_time = self.min_interval - elapsed
                return wait_time
        return 0