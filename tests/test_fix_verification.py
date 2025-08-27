#!/usr/bin/env python3
"""
测试脚本验证cookie引号问题是否已修复
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_login_and_subscribe():
    """测试登录和订阅功能"""
    session = requests.Session()
    
    # 1. 登录
    print("1. 登录测试...")
    login_data = {
        "username": "ccppaap",
        "password": "ccppaap123"
    }
    
    login_response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    print(f"登录状态码: {login_response.status_code}")
    print(f"登录响应头: {dict(login_response.headers)}")
    
    if login_response.status_code != 303:
        print("登录失败!")
        return False
    
    # 检查cookie
    cookies = session.cookies.get_dict()
    print(f"Cookies: {cookies}")
    
    access_token_cookie = cookies.get('access_token', '')
    print(f"Access token cookie值: {access_token_cookie}")
    
    # 2. 访问dashboard
    print("\n2. 访问dashboard...")
    dashboard_response = session.get(f"{BASE_URL}/dashboard")
    print(f"Dashboard状态码: {dashboard_response.status_code}")
    
    if dashboard_response.status_code != 200:
        print("Dashboard访问失败!")
        return False
    
    # 3. 添加股票订阅
    print("\n3. 添加股票订阅...")
    subscribe_data = {"stock_symbol": "GOOGL"}
    
    # 处理cookie中的引号和Bearer前缀
    token_value = access_token_cookie
    if token_value.startswith('"') and token_value.endswith('"'):
        token_value = token_value[1:-1]
    if token_value.startswith('Bearer '):
        token_value = token_value[7:]
    
    subscribe_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token_value}"
    }
    
    subscribe_response = session.post(
        f"{BASE_URL}/api/subscribe", 
        json=subscribe_data,
        headers=subscribe_headers
    )
    
    print(f"订阅状态码: {subscribe_response.status_code}")
    print(f"订阅响应: {subscribe_response.text}")
    
    if subscribe_response.status_code == 200:
        print("✅ 订阅成功!")
        return True
    else:
        print("❌ 订阅失败!")
        return False

if __name__ == "__main__":
    print("开始测试cookie引号问题修复...")
    success = test_login_and_subscribe()
    
    if success:
        print("\n🎉 测试通过! Cookie引号问题已修复")
    else:
        print("\n❌ 测试失败! 需要进一步调试")
