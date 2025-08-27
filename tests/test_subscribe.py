#!/usr/bin/env python3
"""
测试脚本：模拟添加股票的API请求
"""

import requests
import json

# 测试数据
BASE_URL = "http://localhost:8000"
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjIiLCJleHAiOjE3NTU2MTI3MTJ9.em-BrO9yU8d6N38S8GU-IYhiIBTGQptrfer922GB854"  # testuser2的token
STOCK_SYMBOL = "AAPL"

def test_subscribe():
    """测试订阅股票API"""
    headers = {
        "Authorization": TEST_TOKEN,
        "Content-Type": "application/json"
    }
    
    data = {
        "stock_symbol": STOCK_SYMBOL
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/subscribe",
            headers=headers,
            json=data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ 订阅成功！")
        else:
            print("❌ 订阅失败")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求错误: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")

if __name__ == "__main__":
    test_subscribe()
