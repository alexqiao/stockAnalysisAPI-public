import requests
import certifi

# --- 在这里修改您的代理 ---
proxies = {
   "http": "http://127.0.0.1:7890",
   "https": "http://127.0.0.1:7890",
}
# -------------------------

api_key = "***REMOVED***" # 您的API Key
symbol = "TSLA"
url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"

print("正在尝试连接 Alpha Vantage API...")

try:
    response = requests.get(
        url,
        proxies=proxies,
        verify=certifi.where(),
        timeout=20
    )
    response.raise_for_status()  # 如果状态码不是2xx，则抛出异常
    
    print("✅ 连接成功!")
    print("部分返回数据:", response.text[:200])

except requests.exceptions.ProxyError as e:
    print(f"❌ 代理错误: 请检查您的代理地址和端口是否正确，以及代理服务是否正在运行。")
    print(f"   详细信息: {e}")
except requests.exceptions.RequestException as e:
    print(f"❌ 请求失败: {e}")