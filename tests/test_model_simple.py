import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_model_simple():
    """简单测试模型是否能正常响应"""
    ollama_url = "http://localhost:11434/api/chat"
    model_name = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")
    
    print(f"测试模型: {model_name}")
    print(f"Ollama URL: {ollama_url}")
    
    # 非常简单的测试
    payload = {
        "model": model_name,
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": "Hello, please respond with a simple greeting."
            }
        ]
    }
    
    try:
        response = requests.post(ollama_url, json=payload, timeout=30)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("message", {}).get("content", "")
            print(f"模型响应: {content}")
            return True
        else:
            print(f"错误响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"请求异常: {e}")
        return False

if __name__ == "__main__":
    success = test_model_simple()
    if success:
        print("✅ 模型测试成功")
    else:
        print("❌ 模型测试失败")
