#!/usr/bin/env python3
"""
测试登录功能修复的脚本
"""

import requests
import sys
import time

def test_login():
    """测试登录功能"""
    base_url = "http://localhost:8000"
    
    print("测试登录功能...")
    
    # 测试登录页面可访问
    try:
        response = requests.get(f"{base_url}/login")
        if response.status_code == 200:
            print("✓ 登录页面可正常访问")
        else:
            print(f"✗ 登录页面访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 无法访问登录页面: {e}")
        return False
    
    # 测试登录功能 - 使用用户提供的账号
    login_data = {
        "username": "ccppaap",
        "password": "ccppaap123"
    }
    
    try:
        response = requests.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        
        if response.status_code == 303 and "dashboard" in response.headers.get("Location", ""):
            print("✓ 登录成功，重定向到dashboard")
            
            # 检查是否有cookie
            cookies = response.cookies
            if "access_token" in cookies:
                print("✓ 成功设置access_token cookie")
                return True
            else:
                print("✗ 未设置access_token cookie")
                return False
        else:
            print(f"✗ 登录失败: 状态码={response.status_code}, 位置={response.headers.get('Location')}")
            return False
            
    except Exception as e:
        print(f"✗ 登录请求失败: {e}")
        return False

if __name__ == "__main__":
    # 等待服务器完全启动
    print("等待服务器启动...")
    time.sleep(2)
    
    success = test_login()
    
    if success:
        print("\n✓ 登录功能测试通过！")
        sys.exit(0)
    else:
        print("\n✗ 登录功能测试失败")
        sys.exit(1)
