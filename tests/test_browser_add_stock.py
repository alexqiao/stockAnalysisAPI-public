import requests
import json

# 测试浏览器界面添加股票功能
BASE_URL = "http://localhost:8000"

def test_browser_add_stock():
    # 先登录获取session
    session = requests.Session()
    
    # 登录
    login_data = {
        "username": "apitest2",
        "password": "testpassword123"
    }
    
    login_response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    if login_response.status_code != 303:
        print(f"登录失败: {login_response.status_code}")
        return
    
    print("登录成功")
    
    # 访问dashboard获取页面内容
    dashboard_response = session.get(f"{BASE_URL}/dashboard")
    print(f"Dashboard状态码: {dashboard_response.status_code}")
    
    # 从cookie中获取token（模拟浏览器JavaScript的行为）
    cookies = session.cookies.get_dict()
    access_token = cookies.get('access_token', '')
    
    # 处理cookie中的引号（如果存在）
    if access_token.startswith('"') and access_token.endswith('"'):
        access_token = access_token[1:-1]
    
    # 去掉Bearer前缀（如果存在）
    if access_token.startswith('Bearer '):
        access_token = access_token[7:]
    
    print(f"从cookie获取的token: {access_token[:20]}...")
    
    # 模拟浏览器使用axios发送请求
    stock_data = {"stock_symbol": "MSFT"}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    add_response = session.post(f"{BASE_URL}/api/subscribe", 
                              json=stock_data,
                              headers=headers)
    
    print(f"添加股票状态码: {add_response.status_code}")
    print(f"添加股票响应: {add_response.text}")
    
    # 验证订阅列表
    subscriptions_response = session.get(f"{BASE_URL}/api/subscriptions", headers=headers)
    print(f"订阅列表状态码: {subscriptions_response.status_code}")
    print(f"订阅列表: {subscriptions_response.text}")

if __name__ == "__main__":
    test_browser_add_stock()
