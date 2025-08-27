#!/usr/bin/env python3
"""
简单测试API认证
"""

import requests

# 测试配置
BASE_URL = "http://localhost:8000"
USERNAME = "ccppaap"
PASSWORD = "ccppaap123"

def test_login():
    """测试登录获取token"""
    print("测试登录...")
    try:
        # 使用表单数据登录
        response = requests.post(
            f"{BASE_URL}/api/token",
            data={
                "username": USERNAME,
                "password": PASSWORD
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10  # 设置超时时间
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            print(f"登录成功! Token: {token_data['access_token'][:20]}...")
            return True
        else:
            print(f"登录失败: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("登录请求超时")
        return False
    except Exception as e:
        print(f"登录请求错误: {e}")
        return False

if __name__ == "__main__":
    print("=" * 30)
    print("简单API认证测试")
    print("=" * 30)
    
    success = test_login()
    
    if success:
        print("\n✅ API认证正常工作!")
    else:
        print("\n❌ API认证存在问题")
