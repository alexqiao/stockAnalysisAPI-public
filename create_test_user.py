import requests

# 创建测试用户
BASE_URL = "http://localhost:8000"

def create_test_user():
    user_data = {
        "username": "apitest2",
        "email": "apitest2@example.com",
        "password": "testpassword123"
    }
    
    try:
        # 使用表单提交而不是JSON API
        response = requests.post(f"{BASE_URL}/register", data=user_data)
        print(f"创建用户响应状态码: {response.status_code}")
        print(f"创建用户响应内容: {response.text}")
        
        if response.status_code == 303:  # 注册成功会重定向到登录页面
            print("用户创建成功！")
            return user_data
        else:
            print("用户创建失败")
            return None
            
    except Exception as e:
        print(f"创建用户过程中出现异常: {e}")
        return None

def test_subscribe(user_data):
    try:
        # 登录获取token
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        
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
    user_data = create_test_user()
    if user_data:
        test_subscribe(user_data)
