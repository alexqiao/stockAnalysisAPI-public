import requests
import json

# 测试ccppaap用户添加股票功能
BASE_URL = "http://localhost:8000"

def test_ccppaap_add_stock():
    # 先登录获取session
    session = requests.Session()
    
    # 登录
    login_data = {
        "username": "ccppaap",
        "password": "ccppaap123"
    }
    
    login_response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    if login_response.status_code != 303:
        print(f"登录失败: {login_response.status_code}")
        print(login_response.text)
        return
    
    print("登录成功")
    
    # 访问dashboard获取页面内容
    dashboard_response = session.get(f"{BASE_URL}/dashboard")
    print(f"Dashboard状态码: {dashboard_response.status_code}")
    
    # 从cookie中获取token（模拟浏览器JavaScript的行为）
    cookies = session.cookies.get_dict()
    access_token = cookies.get('access_token', '')
    
    print(f"原始cookie值: {access_token}")
    
    # 处理cookie中的引号（如果存在）
    if access_token.startswith('"') and access_token.endswith('"'):
        access_token = access_token[1:-1]
        print(f"去除引号后: {access_token}")
    
    # 去掉Bearer前缀（如果存在）
    if access_token.startswith('Bearer '):
        access_token = access_token[7:]
        print(f"去除Bearer前缀后: {access_token[:20]}...")
    
    # 模拟浏览器使用axios发送请求
    stock_data = {"stock_symbol": "TSLA"}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    print(f"发送请求头: Authorization: Bearer {access_token[:20]}...")
    
    add_response = session.post(f"{BASE_URL}/api/subscribe", 
                              json=stock_data,
                              headers=headers)
    
    print(f"添加股票状态码: {add_response.status_code}")
    print(f"添加股票响应: {add_response.text}")
    
    # 验证订阅列表
    subscriptions_response = session.get(f"{BASE_URL}/api/subscriptions", headers=headers)
    print(f"订阅列表状态码: {subscriptions_response.status_code}")
    print(f"订阅列表: {subscriptions_response.text}")
    
    # 检查数据库中的订阅记录
    import subprocess
    result = subprocess.run([
        'sqlite3', 'data/stocks.db', 
        "SELECT * FROM subscriptions WHERE user_id=2;"
    ], capture_output=True, text=True)
    
    print(f"数据库订阅记录: {result.stdout}")

if __name__ == "__main__":
    test_ccppaap_add_stock()
