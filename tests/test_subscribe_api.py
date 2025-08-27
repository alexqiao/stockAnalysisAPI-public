import requests
import json

# 测试API端点
BASE_URL = "http://localhost:8000"

def test_subscribe():
    # 首先获取一个有效的token（需要先登录）
    login_data = {
        "username": "testuser",
        "password": "password"   # 假设密码是password
    }
    
    try:
        # 尝试登录获取token
        response = requests.post(f"{BASE_URL}/token", data=login_data)
        if response.status_code != 200:
            print(f"登录失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return
        
        token = response.json()["access_token"]
        print(f"获取到token: {token[:20]}...")
        
        # 测试订阅API
        subscribe_data = {"stock_symbol": "AAPL"}
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/subscribe", 
            json=subscribe_data, 
            headers=headers
        )
        
        print(f"订阅API响应状态码: {response.status_code}")
        print(f"订阅API响应内容: {response.text}")
        
        if response.status_code == 200:
            print("订阅成功！")
        else:
            print("订阅失败")
            
    except Exception as e:
        print(f"测试过程中出现异常: {e}")

if __name__ == "__main__":
    test_subscribe()
